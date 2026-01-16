-- Migration: Add refresh_token fields to users table
-- Date: 2026-01-16
-- Description: Add refresh_token and refresh_token_expires_at columns to support OAuth token refresh

-- Add refresh_token column
ALTER TABLE users
ADD COLUMN IF NOT EXISTS refresh_token TEXT;

-- Add refresh_token_expires_at column
ALTER TABLE users
ADD COLUMN IF NOT EXISTS refresh_token_expires_at TIMESTAMPTZ;

-- Add comment for documentation
COMMENT ON COLUMN users.refresh_token IS 'OAuth refresh token for automatic token renewal';
COMMENT ON COLUMN users.refresh_token_expires_at IS 'Expiration timestamp for refresh token';
