use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::fs::OpenOptions;
use std::io::{Write, BufRead, BufReader};
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LedgerEntry {
    pub timestamp: i64,
    pub intent_hash: String,
    pub pre_state_snapshot: String,
    pub action_payload: String,
    pub post_state_snapshot: String,
    pub previous_entry_hash: String,
    pub entry_hash: String,
}

impl LedgerEntry {
    pub fn new(
        intent: &str,
        pre_state: &str,
        action: &str,
        post_state: &str,
        previous_hash: &str,
    ) -> Self {
        let timestamp = chrono::Utc::now().timestamp();
        let intent_hash = Self::hash(intent);
        let pre_state_snapshot = Self::hash(pre_state);
        let post_state_snapshot = Self::hash(post_state);
        let action_payload = action.to_string();
        let previous_entry_hash = previous_hash.to_string();
        
        let entry_data = format!(
            "{}{}{}{}{}{}",
            timestamp, intent_hash, pre_state_snapshot, action_payload, post_state_snapshot, previous_entry_hash
        );
        let entry_hash = Self::hash(&entry_data);
        
        Self {
            timestamp,
            intent_hash,
            pre_state_snapshot,
            action_payload,
            post_state_snapshot,
            previous_entry_hash,
            entry_hash,
        }
    }
    
    fn hash(data: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(data.as_bytes());
        format!("{:x}", hasher.finalize())
    }
}

pub struct AuditLedger {
    pub entries: Vec<LedgerEntry>,
    file_path: PathBuf,
}

impl AuditLedger {
    pub fn new(file_path: PathBuf) -> Self {
        let mut ledger = Self {
            entries: Vec::new(),
            file_path,
        };
        
        // Load existing entries from file
        if let Err(e) = ledger.load_from_file() {
            eprintln!("Warning: Could not load ledger from file: {}", e);
        }
        
        ledger
    }
    
    fn load_from_file(&mut self) -> Result<(), std::io::Error> {
        if !self.file_path.exists() {
            return Ok(());
        }
        
        let file = std::fs::File::open(&self.file_path)?;
        let reader = BufReader::new(file);
        
        for line in reader.lines() {
            let line = line?;
            if let Ok(entry) = serde_json::from_str::<LedgerEntry>(&line) {
                self.entries.push(entry);
            }
        }
        
        Ok(())
    }
    
    pub fn append(&mut self, entry: LedgerEntry) -> Result<(), std::io::Error> {
        // Verify chain integrity
        if let Some(last) = self.entries.last() {
            if entry.previous_entry_hash != last.entry_hash {
                return Err(std::io::Error::new(
                    std::io::ErrorKind::InvalidData,
                    "Chain integrity violation: previous hash mismatch",
                ));
            }
        } else if entry.previous_entry_hash != "genesis" {
            return Err(std::io::Error::new(
                std::io::ErrorKind::InvalidData,
                "First entry must have 'genesis' as previous hash",
            ));
        }
        
        // Append to file
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.file_path)?;
        
        let json = serde_json::to_string(&entry)?;
        writeln!(file, "{}", json)?;
        
        self.entries.push(entry);
        Ok(())
    }
    
    pub fn verify_integrity(&self) -> bool {
        if self.entries.is_empty() {
            return true;
        }
        
        // Check first entry
        if self.entries[0].previous_entry_hash != "genesis" {
            return false;
        }
        
        // Check chain
        for i in 1..self.entries.len() {
            if self.entries[i].previous_entry_hash != self.entries[i - 1].entry_hash {
                return false;
            }
        }
        
        true
    }
    
    pub fn get_last_hash(&self) -> String {
        self.entries
            .last()
            .map(|e| e.entry_hash.clone())
            .unwrap_or_else(|| "genesis".to_string())
    }
}
