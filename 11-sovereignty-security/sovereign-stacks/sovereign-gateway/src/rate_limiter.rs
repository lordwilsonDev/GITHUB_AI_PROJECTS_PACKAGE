// Rate Limiter: Token Bucket Algorithm for Request Throttling
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

#[derive(Clone)]
pub struct TokenBucket {
    capacity: usize,
    tokens: usize,
    refill_rate: usize, // tokens per second
    last_refill: Instant,
}

impl TokenBucket {
    pub fn new(capacity: usize, refill_rate: usize) -> Self {
        Self {
            capacity,
            tokens: capacity,
            refill_rate,
            last_refill: Instant::now(),
        }
    }

    pub fn try_consume(&mut self, tokens: usize) -> bool {
        self.refill();
        
        if self.tokens >= tokens {
            self.tokens -= tokens;
            true
        } else {
            false
        }
    }

    fn refill(&mut self) {
        let now = Instant::now();
        let elapsed = now.duration_since(self.last_refill).as_secs_f64();
        let new_tokens = (elapsed * self.refill_rate as f64) as usize;
        
        if new_tokens > 0 {
            self.tokens = (self.tokens + new_tokens).min(self.capacity);
            self.last_refill = now;
        }
    }

    pub fn available_tokens(&mut self) -> usize {
        self.refill();
        self.tokens
    }
}

#[derive(Clone)]
pub struct RateLimiter {
    buckets: Arc<Mutex<HashMap<String, TokenBucket>>>,
    default_capacity: usize,
    default_refill_rate: usize,
}

impl RateLimiter {
    pub fn new(capacity: usize, refill_rate: usize) -> Self {
        Self {
            buckets: Arc::new(Mutex::new(HashMap::new())),
            default_capacity: capacity,
            default_refill_rate: refill_rate,
        }
    }

    pub fn check_rate_limit(&self, key: &str, tokens: usize) -> Result<(), String> {
        let mut buckets = self.buckets.lock().unwrap();
        
        let bucket = buckets
            .entry(key.to_string())
            .or_insert_with(|| TokenBucket::new(self.default_capacity, self.default_refill_rate));
        
        if bucket.try_consume(tokens) {
            Ok(())
        } else {
            Err(format!(
                "Rate limit exceeded. Available tokens: {}",
                bucket.available_tokens()
            ))
        }
    }

    pub fn get_available_tokens(&self, key: &str) -> usize {
        let mut buckets = self.buckets.lock().unwrap();
        
        buckets
            .entry(key.to_string())
            .or_insert_with(|| TokenBucket::new(self.default_capacity, self.default_refill_rate))
            .available_tokens()
    }

    pub fn cleanup_old_buckets(&self, max_age: Duration) {
        let mut buckets = self.buckets.lock().unwrap();
        let now = Instant::now();
        
        buckets.retain(|_, bucket| {
            now.duration_since(bucket.last_refill) < max_age
        });
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;

    #[test]
    fn test_token_bucket_consume() {
        let mut bucket = TokenBucket::new(10, 5);
        assert!(bucket.try_consume(5));
        assert_eq!(bucket.tokens, 5);
        assert!(bucket.try_consume(5));
        assert_eq!(bucket.tokens, 0);
        assert!(!bucket.try_consume(1));
    }

    #[test]
    fn test_token_bucket_refill() {
        let mut bucket = TokenBucket::new(10, 10);
        bucket.try_consume(10);
        assert_eq!(bucket.tokens, 0);
        
        thread::sleep(Duration::from_millis(1100));
        bucket.refill();
        assert!(bucket.tokens >= 10);
    }

    #[test]
    fn test_rate_limiter() {
        let limiter = RateLimiter::new(5, 1);
        
        assert!(limiter.check_rate_limit("user1", 3).is_ok());
        assert!(limiter.check_rate_limit("user1", 2).is_ok());
        assert!(limiter.check_rate_limit("user1", 1).is_err());
        
        assert!(limiter.check_rate_limit("user2", 5).is_ok());
    }
}
