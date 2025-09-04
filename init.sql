-- Initialize PostgreSQL database for CubePlus Trading Simulator

-- Create database if not exists (handled by docker-compose)
-- CREATE DATABASE cubeplus_trading;

-- Create user if not exists (handled by docker-compose)
-- CREATE USER cubeplus_user WITH PASSWORD 'CubePlus@2024';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE cubeplus_trading TO cubeplus_user;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';