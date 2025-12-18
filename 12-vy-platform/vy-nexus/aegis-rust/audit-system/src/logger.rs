//! BasicAuditLogger - Cryptographic audit trail implementation
//!
//! Provides a blockchain-like audit log with cryptographic signatures,
//! persistent storage, and comprehensive querying capabilities.
//!
//! ## Implementation serves the interface
//! This implementation hides cryptographic complexity behind a simple,
//! ergonomic API that matches natural usage patterns.

use crate::{AuditEntry, AuditSystem, Hash};
use anyhow::{Context, Result};
use async_trait::async_trait;
use ed25519_dalek::{SigningKey, Signature, Signer};
use rand::rngs::OsRng;
use rusqlite::{params, Connection};
use serde_json::Value;
use std::sync::{Arc, Mutex};
use std::sync::atomic::{AtomicUsize, Ordering};

/// Basic implementation of the Audit System
pub struct BasicAuditLogger {
    db: Arc<Mutex<Connection>>,
    signing_key: SigningKey,
    entry_count: Arc<AtomicUsize>,
}

impl BasicAuditLogger {
    /// Create a new BasicAuditLogger with in-memory database
    pub fn new() -> Result<Self> {
        Self::with_path(":memory:")
    }

    /// Create a new BasicAuditLogger with persistent database
    pub fn with_path(db_path: &str) -> Result<Self> {
        let conn = Connection::open(db_path)
            .context("Failed to open database connection")?;

        // Create audit_log table
        conn.execute(
            "CREATE TABLE IF NOT EXISTS audit_log (
                id TEXT PRIMARY KEY,
                timestamp INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                action_data TEXT NOT NULL,
                signature BLOB NOT NULL,
                previous_hash BLOB NOT NULL,
                merkle_root BLOB NOT NULL
            )",
            [],
        )
        .context("Failed to create audit_log table")?;

        // Create index for faster queries
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_log(timestamp)",
            [],
        )
        .context("Failed to create timestamp index")?;

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_action_type ON audit_log(action_type)",
            [],
        )
        .context("Failed to create action_type index")?;

        let mut csprng = OsRng;
        let secret_bytes: [u8; 32] = rand::Rng::gen(&mut csprng);
        let keypair = SigningKey::from_bytes(&secret_bytes);

        // Count existing entries
        let entry_count: usize = conn
            .query_row("SELECT COUNT(*) FROM audit_log", [], |row| row.get(0))
            .unwrap_or(0);

        Ok(Self {
            db: Arc::new(Mutex::new(conn)),
            signing_key: keypair,
            entry_count: Arc::new(AtomicUsize::new(entry_count)),
        })
    }

    /// Get the last entry's hash
    fn get_last_hash(&self) -> Result<Hash> {
        let db = self.db.lock().unwrap();
        let result = db.query_row(
            "SELECT id, timestamp, action_type, action_data, signature FROM audit_log ORDER BY timestamp DESC LIMIT 1",
            [],
            |row| {
                let id: String = row.get(0)?;
                let timestamp: i64 = row.get(1)?;
                let action_type: String = row.get(2)?;
                let action_data_str: String = row.get(3)?;
                let signature: Vec<u8> = row.get(4)?;
                Ok((id, timestamp, action_type, action_data_str, signature))
            },
        );

        match result {
            Ok((id, timestamp, action_type, action_data_str, signature)) => {
                // Compute hash for this entry (same as in log_action)
                let sign_data = format!(
                    "{}:{}:{}:{}",
                    id, timestamp, action_type, action_data_str
                );
                let hash = Hash::new(format!("{}{:?}", sign_data, signature).as_bytes());
                Ok(hash)
            }
            Err(rusqlite::Error::QueryReturnedNoRows) => Ok(Hash::zero()),
            Err(e) => Err(anyhow::anyhow!("Failed to get last hash: {}", e)),
        }
    }

    /// Compute Merkle root from recent entries
    fn compute_merkle_root(&self, current_hash: &Hash) -> Hash {
        // For simplicity, we'll use a simple hash of the current hash
        // In a production system, this would be a proper Merkle tree
        let db = self.db.lock().unwrap();
        let mut hashes: Vec<Vec<u8>> = db
            .prepare("SELECT previous_hash FROM audit_log ORDER BY timestamp DESC LIMIT 10")
            .ok()
            .and_then(|mut stmt| {
                stmt.query_map([], |row| row.get(0))
                    .ok()
                    .map(|rows| rows.filter_map(|r| r.ok()).collect())
            })
            .unwrap_or_default();

        hashes.push(current_hash.0.clone());

        // Combine all hashes
        let combined: Vec<u8> = hashes.into_iter().flatten().collect();
        Hash::new(&combined)
    }

    /// Sign data with the signing key
    fn sign_data(&self, data: &[u8]) -> Vec<u8> {
        let signature: Signature = self.signing_key.sign(data);
        signature.to_bytes().to_vec()
    }

    /// Generate unique ID for entry
    fn generate_id(&self) -> String {
        let count = self.entry_count.fetch_add(1, Ordering::SeqCst);
        format!("audit_{:08}", count)
    }

    /// Get current timestamp in seconds
    fn current_timestamp() -> i64 {
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs() as i64
    }
}

impl Default for BasicAuditLogger {
    fn default() -> Self {
        Self::new().expect("Failed to create default BasicAuditLogger")
    }
}

#[async_trait]
impl AuditSystem for BasicAuditLogger {
    /// Log an action - Simple API serving ergonomic usage
    ///
    /// Takes action_type and data as separate params (what developers want)
    /// Handles all cryptographic complexity internally
    async fn log_action(
        &self,
        action_type: String,
        action_data: Value,
    ) -> Result<AuditEntry> {
        let id = self.generate_id();
        let timestamp = Self::current_timestamp();
        let previous_hash = self.get_last_hash()?;

        // Create data to sign
        let sign_data = format!(
            "{}:{}:{}:{}",
            id,
            timestamp,
            action_type,
            serde_json::to_string(&action_data)?
        );
        let signature = self.sign_data(sign_data.as_bytes());

        // Compute current hash
        let current_hash = Hash::new(
            format!("{}{:?}", sign_data, signature).as_bytes()
        );

        let merkle_root = self.compute_merkle_root(&current_hash);

        let entry = AuditEntry {
            id: id.clone(),
            timestamp,
            action_type: action_type.clone(),
            action_data: action_data.clone(),
            signature: signature.clone(),
            previous_hash: previous_hash.clone(),
            merkle_root: merkle_root.clone(),
        };

        // Store in database
        let db = self.db.lock().unwrap();
        db.execute(
            "INSERT INTO audit_log (id, timestamp, action_type, action_data, signature, previous_hash, merkle_root)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
            params![
                &entry.id,
                &entry.timestamp,
                &entry.action_type,
                serde_json::to_string(&entry.action_data)?,
                &entry.signature,
                &entry.previous_hash.0,
                &entry.merkle_root.0,
            ],
        )
        .context("Failed to insert audit entry")?;

        Ok(entry)
    }

    async fn verify_chain(&self) -> Result<bool> {
        let db = self.db.lock().unwrap();
        let mut stmt = db.prepare(
            "SELECT id, timestamp, action_type, action_data, signature, previous_hash, merkle_root
             FROM audit_log ORDER BY timestamp ASC"
        )?;

        let entries: Vec<AuditEntry> = stmt
            .query_map([], |row| {
                let action_data_str: String = row.get(3)?;
                let action_data: Value = serde_json::from_str(&action_data_str)
                    .map_err(|e| rusqlite::Error::ToSqlConversionFailure(Box::new(e)))?;

                Ok(AuditEntry {
                    id: row.get(0)?,
                    timestamp: row.get(1)?,
                    action_type: row.get(2)?,
                    action_data,
                    signature: row.get(4)?,
                    previous_hash: Hash(row.get(5)?),
                    merkle_root: Hash(row.get(6)?),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        // Verify chain integrity
        let mut expected_previous_hash = Hash::zero();
        for entry in entries {
            if entry.previous_hash != expected_previous_hash {
                return Ok(false);
            }

            // Compute hash for this entry
            let sign_data = format!(
                "{}:{}:{}:{}",
                entry.id,
                entry.timestamp,
                entry.action_type,
                serde_json::to_string(&entry.action_data)?
            );
            expected_previous_hash = Hash::new(
                format!("{}{:?}", sign_data, entry.signature).as_bytes()
            );
        }

        Ok(true)
    }

    /// Query history - Simple Optional parameters API
    ///
    /// Takes 4 separate Optional params (what developers want)
    /// Builds complex SQL query internally
    async fn query_history(
        &self,
        start_time: Option<i64>,
        end_time: Option<i64>,
        action_types: Option<Vec<String>>,
        limit: Option<usize>,
    ) -> Result<Vec<AuditEntry>> {
        let db = self.db.lock().unwrap();
        
        let mut query = String::from(
            "SELECT id, timestamp, action_type, action_data, signature, previous_hash, merkle_root
             FROM audit_log WHERE 1=1"
        );
        let mut params: Vec<Box<dyn rusqlite::ToSql>> = Vec::new();

        if let Some(start) = start_time {
            query.push_str(" AND timestamp >= ?");
            params.push(Box::new(start));
        }

        if let Some(end) = end_time {
            query.push_str(" AND timestamp <= ?");
            params.push(Box::new(end));
        }

        if let Some(types) = action_types {
            if !types.is_empty() {
                let placeholders = types.iter()
                    .map(|_| "?")
                    .collect::<Vec<_>>()
                    .join(",");
                query.push_str(&format!(" AND action_type IN ({})", placeholders));
                for action_type in types {
                    params.push(Box::new(action_type));
                }
            }
        }

        query.push_str(" ORDER BY timestamp DESC");

        if let Some(lim) = limit {
            query.push_str(" LIMIT ?");
            params.push(Box::new(lim as i64));
        }

        let mut stmt = db.prepare(&query)?;
        let param_refs: Vec<&dyn rusqlite::ToSql> = params.iter()
            .map(|p| p.as_ref())
            .collect();

        let entries: Vec<AuditEntry> = stmt
            .query_map(param_refs.as_slice(), |row| {
                let action_data_str: String = row.get(3)?;
                let action_data: Value = serde_json::from_str(&action_data_str)
                    .map_err(|e| rusqlite::Error::ToSqlConversionFailure(Box::new(e)))?;

                Ok(AuditEntry {
                    id: row.get(0)?,
                    timestamp: row.get(1)?,
                    action_type: row.get(2)?,
                    action_data,
                    signature: row.get(4)?,
                    previous_hash: Hash(row.get(5)?),
                    merkle_root: Hash(row.get(6)?),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(entries)
    }

    fn get_merkle_root(&self) -> Hash {
        let db = self.db.lock().unwrap();
        db.query_row(
            "SELECT merkle_root FROM audit_log ORDER BY timestamp DESC LIMIT 1",
            [],
            |row| {
                let bytes: Vec<u8> = row.get(0)?;
                Ok(Hash(bytes))
            },
        )
        .unwrap_or_else(|_| Hash::zero())
    }

    async fn export_log(&self, path: &str) -> Result<()> {
        let db = self.db.lock().unwrap();
        let mut stmt = db.prepare(
            "SELECT id, timestamp, action_type, action_data, signature, previous_hash, merkle_root
             FROM audit_log ORDER BY timestamp ASC"
        )?;

        let entries: Vec<AuditEntry> = stmt
            .query_map([], |row| {
                let action_data_str: String = row.get(3)?;
                let action_data: Value = serde_json::from_str(&action_data_str)
                    .map_err(|e| rusqlite::Error::ToSqlConversionFailure(Box::new(e)))?;

                Ok(AuditEntry {
                    id: row.get(0)?,
                    timestamp: row.get(1)?,
                    action_type: row.get(2)?,
                    action_data,
                    signature: row.get(4)?,
                    previous_hash: Hash(row.get(5)?),
                    merkle_root: Hash(row.get(6)?),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        // Write to JSON file
        let json = serde_json::to_string_pretty(&entries)?;
        std::fs::write(path, json)
            .context("Failed to write audit log to file")?;

        Ok(())
    }
}
// Implementation for HITL-specific AuditLogger trait
use hitl_collab::{AuditLogger, DecisionRequest, DecisionResponse};

#[async_trait]
impl AuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<()> {
        self.log_action(
            "hitl_decision_request".to_string(),
            serde_json::json!({
                "id": request.id,
                "description": request.description,
                "context": request.context,
                "priority": request.priority,
                "requested_at": request.requested_at,
                "timeout_seconds": request.timeout_seconds,
                "requester": request.requester,
            }),
        ).await?;
        Ok(())
    }

    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<()> {
        self.log_action(
            "hitl_decision_response".to_string(),
            serde_json::json!({
                "request_id": response.request_id,
                "approved": response.approved,
                "reasoning": response.reasoning,
                "responder": response.responder,
                "responded_at": response.responded_at,
            }),
        ).await?;
        Ok(())
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}


// Implementation of hitl-collab's AuditLogger trait for BasicAuditLogger
#[cfg(test)]
use hitl_collab::{AuditLogger as HITLAuditLogger, DecisionRequest, DecisionResponse};

#[cfg(test)]
#[async_trait::async_trait]
impl HITLAuditLogger for BasicAuditLogger {
    async fn log_decision_request(&self, request: &DecisionRequest) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision request to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_request",
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
    
    async fn log_decision_response(&self, response: &DecisionResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // Convert decision response to JSON and log it
        let action_data = serde_json::json!({
            "type": "hitl_decision_response",
            "request_id": response.request_id,
            "approved": response.approved,
            "reason": response.reason,
        });
        self.log_action(action_data).await.map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)
    }
}
