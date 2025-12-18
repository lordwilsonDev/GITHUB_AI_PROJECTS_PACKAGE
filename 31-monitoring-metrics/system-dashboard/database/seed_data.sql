-- VY COGNITIVE SOVEREIGNTY STACK - SEED DATA
-- Initial service registry
-- Created: December 17, 2025

-- Insert all monitored services
INSERT INTO services (name, url, port, category, description) VALUES
    ('love-engine', 'http://localhost:8001/health', 8001, 'core', 'AI Safety & Validation System'),
    ('jarvis-m1', 'http://localhost:8002/health', 8002, 'core', 'M1 Hardware Optimization Engine'),
    ('lcrs-system', 'http://localhost:8003/health', 8003, 'core', 'Emotional Intelligence System'),
    ('level33-sovereign', 'http://localhost:8004/health', 8004, 'automation', 'Physical Automation Platform'),
    ('nanoapex', 'http://localhost:8005/health', 8005, 'vision', 'Computer Vision & Orchestration'),
    ('sovereign-brain', 'http://localhost:8006/health', 8006, 'core', 'AGI Brain Module - Recursive Planning'),
    ('sovereign-heart', 'http://localhost:8007/health', 8007, 'core', 'AGI Heart Module - Execution Engine'),
    ('moie-os', 'http://localhost:8008/health', 8008, 'cognitive', 'Mixture of Inversion Experts OS'),
    ('metadata-universe', 'http://localhost:8009/health', 8009, 'knowledge', 'Knowledge Architecture System'),
    ('cord-project', 'http://localhost:8010/health', 8010, 'coordination', 'Multi-Agent Coordination Platform');

-- Insert initial system event
INSERT INTO system_events (event_type, event_data) VALUES
    ('SYSTEM_INITIALIZED', json_object(
        'version', '1.0.0',
        'services_count', 10,
        'timestamp', datetime('now')
    ));
