-- VY COGNITIVE SOVEREIGNTY STACK - MONITORING DATABASE SCHEMA
-- Created: December 17, 2025

-- Services table: Registry of all monitored services
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    port INTEGER NOT NULL,
    description TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Health checks table: Historical health check data
CREATE TABLE IF NOT EXISTS health_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('UP', 'DOWN', 'DEGRADED', 'UNKNOWN')),
    response_time_ms REAL,
    status_code INTEGER,
    error_message TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_health_checks_service_time 
    ON health_checks(service_id, checked_at DESC);

-- Metrics table: Performance metrics over time
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

-- Create index for metrics queries
CREATE INDEX IF NOT EXISTS idx_metrics_service_name_time 
    ON metrics(service_id, metric_name, recorded_at DESC);

-- Alerts table: Alert history and status
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL CHECK(alert_type IN ('DOWN', 'SLOW', 'ERROR', 'DEGRADED', 'RECOVERED')),
    message TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('INFO', 'WARNING', 'CRITICAL')),
    resolved BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolved_by TEXT,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

-- Create index for active alerts
CREATE INDEX IF NOT EXISTS idx_alerts_active 
    ON alerts(resolved, created_at DESC);

-- System events table: General system events
CREATE TABLE IF NOT EXISTS system_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    event_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dashboard config table: Store dashboard configuration
CREATE TABLE IF NOT EXISTS dashboard_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default configuration
INSERT OR IGNORE INTO dashboard_config (key, value) VALUES
    ('poll_interval_seconds', '30'),
    ('metrics_retention_days', '30'),
    ('alert_retention_days', '90'),
    ('slow_response_threshold_ms', '5000'),
    ('dashboard_version', '1.0.0');

-- Create view for latest service status
CREATE VIEW IF NOT EXISTS latest_service_status AS
SELECT 
    s.id,
    s.name,
    s.url,
    s.port,
    s.category,
    s.description,
    hc.status,
    hc.response_time_ms,
    hc.checked_at,
    hc.error_message
FROM services s
LEFT JOIN health_checks hc ON s.id = hc.service_id
WHERE hc.id = (
    SELECT id FROM health_checks 
    WHERE service_id = s.id 
    ORDER BY checked_at DESC 
    LIMIT 1
)
OR hc.id IS NULL;

-- Create view for active alerts
CREATE VIEW IF NOT EXISTS active_alerts AS
SELECT 
    a.id,
    a.service_id,
    s.name as service_name,
    a.alert_type,
    a.message,
    a.severity,
    a.created_at,
    CAST((julianday('now') - julianday(a.created_at)) * 24 * 60 AS INTEGER) as minutes_ago
FROM alerts a
JOIN services s ON a.service_id = s.id
WHERE a.resolved = 0
ORDER BY a.created_at DESC;

-- Create view for service uptime (last 24 hours)
CREATE VIEW IF NOT EXISTS service_uptime_24h AS
SELECT 
    s.id,
    s.name,
    COUNT(CASE WHEN hc.status = 'UP' THEN 1 END) * 100.0 / COUNT(*) as uptime_percent,
    COUNT(*) as total_checks,
    COUNT(CASE WHEN hc.status = 'UP' THEN 1 END) as up_checks,
    COUNT(CASE WHEN hc.status = 'DOWN' THEN 1 END) as down_checks,
    AVG(hc.response_time_ms) as avg_response_time_ms
FROM services s
LEFT JOIN health_checks hc ON s.id = hc.service_id
WHERE hc.checked_at >= datetime('now', '-24 hours')
GROUP BY s.id, s.name;

-- Trigger to update service updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_service_timestamp 
AFTER UPDATE ON services
FOR EACH ROW
BEGIN
    UPDATE services SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger to log system events on alert creation
CREATE TRIGGER IF NOT EXISTS log_alert_creation 
AFTER INSERT ON alerts
FOR EACH ROW
BEGIN
    INSERT INTO system_events (event_type, event_data)
    VALUES ('ALERT_CREATED', json_object(
        'alert_id', NEW.id,
        'service_id', NEW.service_id,
        'alert_type', NEW.alert_type,
        'severity', NEW.severity
    ));
END;

-- Trigger to log system events on alert resolution
CREATE TRIGGER IF NOT EXISTS log_alert_resolution 
AFTER UPDATE OF resolved ON alerts
FOR EACH ROW
WHEN NEW.resolved = 1 AND OLD.resolved = 0
BEGIN
    INSERT INTO system_events (event_type, event_data)
    VALUES ('ALERT_RESOLVED', json_object(
        'alert_id', NEW.id,
        'service_id', NEW.service_id,
        'alert_type', NEW.alert_type,
        'duration_minutes', CAST((julianday(NEW.resolved_at) - julianday(NEW.created_at)) * 24 * 60 AS INTEGER)
    ));
END;

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (version) VALUES (1);
