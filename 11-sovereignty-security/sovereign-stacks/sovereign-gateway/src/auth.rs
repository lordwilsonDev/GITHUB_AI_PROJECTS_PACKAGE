// Authentication & Authorization Layer
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use std::sync::atomic::{AtomicU64, Ordering};
use chrono::{DateTime, Utc, Duration};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiKey {
    pub key: String,
    pub name: String,
    pub permissions: Vec<String>,
    pub created_at: DateTime<Utc>,
    pub expires_at: Option<DateTime<Utc>>,
    pub rate_limit: usize,
}

impl ApiKey {
    pub fn new(name: &str, permissions: Vec<String>, rate_limit: usize) -> Self {
        static COUNTER: AtomicU64 = AtomicU64::new(0);
        let id = COUNTER.fetch_add(1, Ordering::SeqCst);
        
        Self {
            key: format!("sk_{:016x}", id),
            name: name.to_string(),
            permissions,
            created_at: Utc::now(),
            expires_at: None,
            rate_limit,
        }
    }

    pub fn with_expiry(mut self, days: i64) -> Self {
        self.expires_at = Some(Utc::now() + Duration::days(days));
        self
    }

    pub fn is_expired(&self) -> bool {
        if let Some(expires_at) = self.expires_at {
            Utc::now() > expires_at
        } else {
            false
        }
    }

    pub fn has_permission(&self, permission: &str) -> bool {
        self.permissions.contains(&"*".to_string()) || 
        self.permissions.contains(&permission.to_string())
    }
}

#[derive(Clone)]
pub struct AuthManager {
    keys: Arc<RwLock<HashMap<String, ApiKey>>>,
}

impl AuthManager {
    pub fn new() -> Self {
        Self {
            keys: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub fn create_key(&self, name: &str, permissions: Vec<String>, rate_limit: usize) -> ApiKey {
        let key = ApiKey::new(name, permissions, rate_limit);
        let mut keys = self.keys.write().unwrap();
        keys.insert(key.key.clone(), key.clone());
        key
    }

    pub fn validate_key(&self, key: &str) -> Result<ApiKey, String> {
        let keys = self.keys.read().unwrap();
        
        match keys.get(key) {
            Some(api_key) => {
                if api_key.is_expired() {
                    Err("API key has expired".to_string())
                } else {
                    Ok(api_key.clone())
                }
            }
            None => Err("Invalid API key".to_string()),
        }
    }

    pub fn check_permission(&self, key: &str, permission: &str) -> Result<(), String> {
        let api_key = self.validate_key(key)?;
        
        if api_key.has_permission(permission) {
            Ok(())
        } else {
            Err(format!("Permission denied: {}", permission))
        }
    }

    pub fn revoke_key(&self, key: &str) -> Result<(), String> {
        let mut keys = self.keys.write().unwrap();
        
        if keys.remove(key).is_some() {
            Ok(())
        } else {
            Err("API key not found".to_string())
        }
    }

    pub fn list_keys(&self) -> Vec<ApiKey> {
        let keys = self.keys.read().unwrap();
        keys.values().cloned().collect()
    }

    pub fn get_rate_limit(&self, key: &str) -> Result<usize, String> {
        let api_key = self.validate_key(key)?;
        Ok(api_key.rate_limit)
    }
}

// Middleware helper
pub fn extract_api_key(auth_header: Option<&str>) -> Option<String> {
    auth_header
        .and_then(|h| h.strip_prefix("Bearer "))
        .map(|k| k.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_api_key_creation() {
        let key = ApiKey::new("test", vec!["read".to_string()], 100);
        assert!(key.key.starts_with("sk_"));
        assert_eq!(key.name, "test");
        assert!(!key.is_expired());
    }

    #[test]
    fn test_api_key_expiry() {
        let key = ApiKey::new("test", vec![], 100).with_expiry(-1);
        assert!(key.is_expired());
    }

    #[test]
    fn test_api_key_permissions() {
        let key = ApiKey::new("test", vec!["read".to_string(), "write".to_string()], 100);
        assert!(key.has_permission("read"));
        assert!(key.has_permission("write"));
        assert!(!key.has_permission("admin"));
        
        let admin_key = ApiKey::new("admin", vec!["*".to_string()], 1000);
        assert!(admin_key.has_permission("anything"));
    }

    #[test]
    fn test_auth_manager() {
        let manager = AuthManager::new();
        let key = manager.create_key("test", vec!["read".to_string()], 100);
        
        assert!(manager.validate_key(&key.key).is_ok());
        assert!(manager.check_permission(&key.key, "read").is_ok());
        assert!(manager.check_permission(&key.key, "write").is_err());
        
        assert!(manager.revoke_key(&key.key).is_ok());
        assert!(manager.validate_key(&key.key).is_err());
    }

    #[test]
    fn test_extract_api_key() {
        assert_eq!(
            extract_api_key(Some("Bearer sk_test123")),
            Some("sk_test123".to_string())
        );
        assert_eq!(extract_api_key(Some("Invalid")), None);
        assert_eq!(extract_api_key(None), None);
    }
}
