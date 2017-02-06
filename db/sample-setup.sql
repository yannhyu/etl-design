--etl=> select CURRENT_USER;
--You are now connected to database "etl" as user "test_user".

--CREATE DATABASE IF NOT EXISTS etl;
--CREATE USER test_user WITH PASSWORD 'med';
--GRANT ALL PRIVILEGES ON DATABASE "etl" to test_user;

--USE etl;
--\c etl
--CONNECT TO etl;

CREATE EXTENSION pgcrypto; 

CREATE TABLE IF NOT EXISTS ins00 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data JSONB,
    created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_ins00_data_updated BEFORE UPDATE ON ins00
  FOR EACH ROW EXECUTE PROCEDURE update_modified_column();


CREATE INDEX idx_ins00_performance_data ON ins00 USING gin(data);