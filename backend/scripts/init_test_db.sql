-- Initialize test database with required PostgreSQL extensions

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for encryption functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enable vector operations for AI/ML features (if needed)
-- Note: pgvector may not be available in all environments
-- CREATE EXTENSION IF NOT EXISTS "vector";

-- Create test schema
CREATE SCHEMA IF NOT EXISTS test;

-- Grant permissions to test user
GRANT ALL PRIVILEGES ON DATABASE ma_saas_test TO test_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO test_user;
GRANT ALL PRIVILEGES ON SCHEMA test TO test_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO test_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO test_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO test_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO test_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO test_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO test_user;

-- Create test configuration table
CREATE TABLE IF NOT EXISTS test_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO test_config (key, value) VALUES ('initialized', 'true');
INSERT INTO test_config (key, value) VALUES ('version', '1.0.0');
