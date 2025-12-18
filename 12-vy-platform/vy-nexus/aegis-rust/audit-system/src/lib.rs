//! Audit System - Cryptographic accountability for all actions
//!
//! This module maintains a tamper-proof audit trail using cryptographic
//! signatures and Merkle trees.
//!
//! ## Design Philosophy: Built Backwards from Usage
//!
//! API designed by analyzing how developers naturally log and query actions.
//! Simple method signatures hide cryptographic complexity.

use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use anyhow::Result;
use sha2::{Sha256, Digest};

/// A single entry in the audit log
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditEntry {
    pub id: String,
    pub timestamp: i64,
    pub action_type: String,
    pub action_data: serde_json::Value,
    pub signature: Vec<u8>,
    pub previous_hash: Hash,
    pub merkle_root: Hash,
}

/// Cryptographic hash
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct Hash(pub Vec<u8>);

impl Hash {
    pub fn new(data: &[u8]) -> Self {
        let mut hasher = Sha256::new();
        hasher.update(data);
        Hash(hasher.finalize().to_vec())
    }
    
    pub fn zero() -> Self {
        Hash(vec![0; 32])
    }
}

/// Filter for querying audit history (internal use)
///
/// Public API uses simple Optional parameters instead of this struct.
/// This exists for internal implementation and backwards compatibility.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Filter {
    pub start_time: Option<i64>,
    pub end_time: Option<i64>,
    pub action_types: Vec<String>,
    pub limit: Option<usize>,
}

/// Main trait for the Audit System
///
/// ## Built Backwards from Real Usage
///
/// Methods designed to match natural developer usage patterns from integration tests.
#[async_trait]
pub trait AuditSystem: Send + Sync {
    /// Log an action with cryptographic signature
    ///
    /// ## Simple API (what developers want)
    /// ```ignore
    /// logger.log_action(
    ///     "safety_check",                      // Action type
    ///     json!({"score": 0.8, "safe": true}), // Action data
    /// ).await?;
    /// ```
    ///
    /// Internally handles:
    /// - Timestamp generation
    /// - ID generation
    /// - Cryptographic signing
    /// - Merkle tree updates
    /// - Chain linking
    async fn log_action(
        &self,
        action_type: String,
        action_data: serde_json::Value,
    ) -> Result<AuditEntry>;
    
    /// Verify the integrity of the audit chain
    async fn verify_chain(&self) -> Result<bool>;
    
    /// Query audit history with simple optional filters
    ///
    /// ## Simple API (what developers want)
    /// ```ignore
    /// // Get all entries
    /// let all = logger.query_history(None, None, None, None).await?;
    ///
    /// // Get entries in time range
    /// let recent = logger.query_history(
    ///     Some(start_time),
    ///     Some(end_time),
    ///     None,
    ///     None,
    /// ).await?;
    ///
    /// // Get specific action types with limit
    /// let safety_checks = logger.query_history(
    ///     None,
    ///     None,
    ///     Some(vec!["safety_check".to_string()]),
    ///     Some(10),
    /// ).await?;
    /// ```
    async fn query_history(
        &self,
        start_time: Option<i64>,
        end_time: Option<i64>,
        action_types: Option<Vec<String>>,
        limit: Option<usize>,
    ) -> Result<Vec<AuditEntry>>;
    
    /// Get the current Merkle root
    fn get_merkle_root(&self) -> Hash;
    
    /// Export audit log for external verification
    async fn export_log(&self, path: &str) -> Result<()>;
}

mod logger;
pub use logger::BasicAuditLogger;

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_hash_creation() {
        let hash1 = Hash::new(b"test data");
        let hash2 = Hash::new(b"test data");
        let hash3 = Hash::new(b"different data");
        
        assert_eq!(hash1, hash2);
        assert_ne!(hash1, hash3);
    }
    
    #[test]
    fn test_zero_hash() {
        let zero = Hash::zero();
        assert_eq!(zero.0.len(), 32);
        assert!(zero.0.iter().all(|&b| b == 0));
    }

    #[tokio::test]
    async fn test_basic_audit_logger_creation() {
        let logger = BasicAuditLogger::new();
        assert!(logger.is_ok());
    }

    #[tokio::test]
    async fn test_log_single_action() {
        let logger = BasicAuditLogger::new().unwrap();
        
        let entry = logger.log_action(
            "test_action".to_string(),
            json!({"key": "value"}),
        ).await.unwrap();
        
        assert_eq!(entry.action_type, "test_action");
        assert!(!entry.signature.is_empty());
    }

    #[tokio::test]
    async fn test_query_history_simple_api() {
        let logger = BasicAuditLogger::new().unwrap();
        
        // Log some actions
        logger.log_action("action1".to_string(), json!({"data": 1})).await.unwrap();
        logger.log_action("action2".to_string(), json!({"data": 2})).await.unwrap();
        logger.log_action("action1".to_string(), json!({"data": 3})).await.unwrap();
        
        // Query all
        let all = logger.query_history(None, None, None, None).await.unwrap();
        assert_eq!(all.len(), 3);
        
        // Query with type filter
        let action1s = logger.query_history(
            None,
            None,
            Some(vec!["action1".to_string()]),
            None,
        ).await.unwrap();
        assert_eq!(action1s.len(), 2);
        
        // Query with limit
        let limited = logger.query_history(None, None, None, Some(1)).await.unwrap();
        assert_eq!(limited.len(), 1);
    }

    #[tokio::test]
    async fn test_chain_verification() {
        let logger = BasicAuditLogger::new().unwrap();
        
        logger.log_action("action1".to_string(), json!({})).await.unwrap();
        logger.log_action("action2".to_string(), json!({})).await.unwrap();
        logger.log_action("action3".to_string(), json!({})).await.unwrap();
        
        let valid = logger.verify_chain().await.unwrap();
        assert!(valid, "Chain should be valid");
    }
}
