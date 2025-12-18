// Response Caching Layer with TTL and LRU Eviction
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use std::time::{Duration, Instant};
use std::hash::{Hash, Hasher};
use std::collections::hash_map::DefaultHasher;

#[derive(Clone, Debug)]
struct CacheEntry {
    data: String,
    created_at: Instant,
    ttl: Duration,
    access_count: usize,
    last_accessed: Instant,
}

impl CacheEntry {
    fn new(data: String, ttl: Duration) -> Self {
        let now = Instant::now();
        Self {
            data,
            created_at: now,
            ttl,
            access_count: 0,
            last_accessed: now,
        }
    }

    fn is_expired(&self) -> bool {
        self.created_at.elapsed() > self.ttl
    }

    fn access(&mut self) -> String {
        self.access_count += 1;
        self.last_accessed = Instant::now();
        self.data.clone()
    }
}

#[derive(Clone)]
pub struct ResponseCache {
    cache: Arc<RwLock<HashMap<String, CacheEntry>>>,
    max_size: usize,
    default_ttl: Duration,
    hits: Arc<RwLock<usize>>,
    misses: Arc<RwLock<usize>>,
}

impl ResponseCache {
    pub fn new(max_size: usize, default_ttl_secs: u64) -> Self {
        Self {
            cache: Arc::new(RwLock::new(HashMap::new())),
            max_size,
            default_ttl: Duration::from_secs(default_ttl_secs),
            hits: Arc::new(RwLock::new(0)),
            misses: Arc::new(RwLock::new(0)),
        }
    }

    pub fn get(&self, key: &str) -> Option<String> {
        let mut cache = self.cache.write().unwrap();
        
        if let Some(entry) = cache.get_mut(key) {
            if entry.is_expired() {
                cache.remove(key);
                *self.misses.write().unwrap() += 1;
                None
            } else {
                *self.hits.write().unwrap() += 1;
                Some(entry.access())
            }
        } else {
            *self.misses.write().unwrap() += 1;
            None
        }
    }

    pub fn set(&self, key: &str, value: String) {
        self.set_with_ttl(key, value, self.default_ttl);
    }

    pub fn set_with_ttl(&self, key: &str, value: String, ttl: Duration) {
        let mut cache = self.cache.write().unwrap();
        
        // Evict if at capacity
        if cache.len() >= self.max_size && !cache.contains_key(key) {
            self.evict_lru(&mut cache);
        }
        
        cache.insert(key.to_string(), CacheEntry::new(value, ttl));
    }

    fn evict_lru(&self, cache: &mut HashMap<String, CacheEntry>) {
        if let Some((lru_key, _)) = cache
            .iter()
            .min_by_key(|(_, entry)| entry.last_accessed)
        {
            let lru_key = lru_key.clone();
            cache.remove(&lru_key);
        }
    }

    pub fn invalidate(&self, key: &str) -> bool {
        let mut cache = self.cache.write().unwrap();
        cache.remove(key).is_some()
    }

    pub fn clear(&self) {
        let mut cache = self.cache.write().unwrap();
        cache.clear();
    }

    pub fn cleanup_expired(&self) {
        let mut cache = self.cache.write().unwrap();
        cache.retain(|_, entry| !entry.is_expired());
    }

    pub fn stats(&self) -> CacheStats {
        let cache = self.cache.read().unwrap();
        let hits = *self.hits.read().unwrap();
        let misses = *self.misses.read().unwrap();
        
        CacheStats {
            size: cache.len(),
            max_size: self.max_size,
            hits,
            misses,
            hit_rate: if hits + misses > 0 {
                hits as f64 / (hits + misses) as f64
            } else {
                0.0
            },
        }
    }

    pub fn generate_key(tool: &str, params: &serde_json::Value) -> String {
        let mut hasher = DefaultHasher::new();
        tool.hash(&mut hasher);
        params.to_string().hash(&mut hasher);
        format!("cache_{:x}", hasher.finish())
    }
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct CacheStats {
    pub size: usize,
    pub max_size: usize,
    pub hits: usize,
    pub misses: usize,
    pub hit_rate: f64,
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;

    #[test]
    fn test_cache_set_get() {
        let cache = ResponseCache::new(10, 60);
        cache.set("key1", "value1".to_string());
        
        assert_eq!(cache.get("key1"), Some("value1".to_string()));
        assert_eq!(cache.get("key2"), None);
    }

    #[test]
    fn test_cache_expiry() {
        let cache = ResponseCache::new(10, 1);
        cache.set_with_ttl("key1", "value1".to_string(), Duration::from_millis(100));
        
        assert_eq!(cache.get("key1"), Some("value1".to_string()));
        
        thread::sleep(Duration::from_millis(150));
        assert_eq!(cache.get("key1"), None);
    }

    #[test]
    fn test_cache_lru_eviction() {
        let cache = ResponseCache::new(3, 60);
        
        cache.set("key1", "value1".to_string());
        thread::sleep(Duration::from_millis(10));
        cache.set("key2", "value2".to_string());
        thread::sleep(Duration::from_millis(10));
        cache.set("key3", "value3".to_string());
        
        // Access key1 to make it more recent
        cache.get("key1");
        
        // This should evict key2 (least recently used)
        cache.set("key4", "value4".to_string());
        
        assert_eq!(cache.get("key1"), Some("value1".to_string()));
        assert_eq!(cache.get("key2"), None);
        assert_eq!(cache.get("key3"), Some("value3".to_string()));
        assert_eq!(cache.get("key4"), Some("value4".to_string()));
    }

    #[test]
    fn test_cache_stats() {
        let cache = ResponseCache::new(10, 60);
        cache.set("key1", "value1".to_string());
        
        cache.get("key1"); // hit
        cache.get("key2"); // miss
        cache.get("key1"); // hit
        
        let stats = cache.stats();
        assert_eq!(stats.hits, 2);
        assert_eq!(stats.misses, 1);
        assert!((stats.hit_rate - 0.666).abs() < 0.01);
    }

    #[test]
    fn test_generate_key() {
        let params = serde_json::json!({"path": "/test"});
        let key1 = ResponseCache::generate_key("fs_read", &params);
        let key2 = ResponseCache::generate_key("fs_read", &params);
        let key3 = ResponseCache::generate_key("fs_write", &params);
        
        assert_eq!(key1, key2);
        assert_ne!(key1, key3);
    }
}
