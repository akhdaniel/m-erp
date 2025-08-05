-- Create databases for different microservices
CREATE DATABASE user_auth_db;
CREATE DATABASE company_partner_db;
CREATE DATABASE menu_access_db;
CREATE DATABASE audit_db;
CREATE DATABASE inventory_db;
CREATE DATABASE sales_db;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE user_auth_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE company_partner_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE menu_access_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE audit_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE sales_db TO postgres;