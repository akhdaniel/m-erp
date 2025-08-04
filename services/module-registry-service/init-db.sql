-- Initialize Module Registry Database

-- Create database if it doesn't exist (this is handled by Docker environment)
-- CREATE DATABASE IF NOT EXISTS module_registry_db;

-- Grant privileges to user
GRANT ALL PRIVILEGES ON DATABASE module_registry_db TO mruser;

-- Connect to the database
\c module_registry_db;

-- Enable UUID extension (if needed in the future)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for performance optimization
-- These will be created by Alembic migrations, but we can prepare the database

-- Log the initialization
SELECT 'Module Registry Database initialized successfully' as status;