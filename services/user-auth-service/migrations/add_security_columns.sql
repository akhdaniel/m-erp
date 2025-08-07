-- Add security-related columns to users table

-- Add failed login tracking columns
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_failed_login TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMPTZ;

-- Update existing records to have password_changed_at set to created_at
UPDATE users 
SET password_changed_at = created_at 
WHERE password_changed_at IS NULL;

-- Add a comment for clarity
COMMENT ON COLUMN users.failed_login_attempts IS 'Number of consecutive failed login attempts';
COMMENT ON COLUMN users.last_failed_login IS 'Timestamp of the last failed login attempt';
COMMENT ON COLUMN users.password_changed_at IS 'Timestamp when the password was last changed';