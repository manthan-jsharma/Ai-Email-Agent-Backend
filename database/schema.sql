-- AI Email Agent Database Schema for Supabase

-- Users and Authentication
CREATE TABLE IF NOT EXISTS user_credentials (
    user_email VARCHAR(255) PRIMARY KEY,
    credentials JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Email Storage
CREATE TABLE IF NOT EXISTS emails (
    id VARCHAR(255) PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    thread_id VARCHAR(255) NOT NULL,
    subject TEXT,
    sender VARCHAR(255),
    recipient VARCHAR(255),
    body TEXT,
    date_received TIMESTAMP,
    label_ids TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Responses
CREATE TABLE IF NOT EXISTS ai_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_email VARCHAR(255) NOT NULL,
    original_email_id VARCHAR(255) NOT NULL,
    thread_id VARCHAR(255) NOT NULL,
    ai_response TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'generated',
    draft_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES user_credentials(user_email),
    FOREIGN KEY (original_email_id) REFERENCES emails(id)
);

-- User Settings
CREATE TABLE IF NOT EXISTS user_settings (
    user_email VARCHAR(255) PRIMARY KEY,
    auto_draft BOOLEAN DEFAULT FALSE,
    auto_send BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES user_credentials(user_email)
);

-- Gmail Watch Subscriptions
CREATE TABLE IF NOT EXISTS gmail_watches (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    history_id VARCHAR(255),
    expiration TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES user_credentials(user_email)
);

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_emails_user_email ON emails(user_email);
CREATE INDEX IF NOT EXISTS idx_emails_thread_id ON emails(thread_id);
CREATE INDEX IF NOT EXISTS idx_emails_date_received ON emails(date_received DESC);
CREATE INDEX IF NOT EXISTS idx_ai_responses_user_email ON ai_responses(user_email);
CREATE INDEX IF NOT EXISTS idx_ai_responses_status ON ai_responses(status);

-- Row Level Security Policies
ALTER TABLE user_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE gmail_watches ENABLE ROW LEVEL SECURITY;

-- Policies for user_credentials
CREATE POLICY "Users can view their own credentials" 
ON user_credentials FOR SELECT 
USING (auth.uid()::text = user_email);

CREATE POLICY "Users can update their own credentials" 
ON user_credentials FOR UPDATE 
USING (auth.uid()::text = user_email);

-- Policies for emails
CREATE POLICY "Users can view their own emails" 
ON emails FOR SELECT 
USING (auth.uid()::text = user_email);

CREATE POLICY "Users can insert their own emails" 
ON emails FOR INSERT 
WITH CHECK (auth.uid()::text = user_email);

-- Policies for ai_responses
CREATE POLICY "Users can view their own AI responses" 
ON ai_responses FOR SELECT 
USING (auth.uid()::text = user_email);

CREATE POLICY "Users can update their own AI responses" 
ON ai_responses FOR UPDATE 
USING (auth.uid()::text = user_email);

CREATE POLICY "Users can insert their own AI responses" 
ON ai_responses FOR INSERT 
WITH CHECK (auth.uid()::text = user_email);

-- Policies for user_settings
CREATE POLICY "Users can view their own settings" 
ON user_settings FOR SELECT 
USING (auth.uid()::text = user_email);

CREATE POLICY "Users can update their own settings" 
ON user_settings FOR UPDATE 
USING (auth.uid()::text = user_email);

CREATE POLICY "Users can insert their own settings" 
ON user_settings FOR INSERT 
WITH CHECK (auth.uid()::text = user_email);

-- Policies for gmail_watches
CREATE POLICY "Users can view their own Gmail watches" 
ON gmail_watches FOR SELECT 
USING (auth.uid()::text = user_email);

CREATE POLICY "Users can update their own Gmail watches" 
ON gmail_watches FOR UPDATE 
USING (auth.uid()::text = user_email);
