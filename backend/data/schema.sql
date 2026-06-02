-- ============================================================
-- TONATIVE SME BOT - SUPABASE DATABASE SCHEMA
-- ============================================================
-- Run this in your Supabase SQL Editor (Dashboard > SQL Editor)
-- ============================================================

-- SME Profiles table
CREATE TABLE IF NOT EXISTS sme_profiles (
    phone_number TEXT PRIMARY KEY,
    state TEXT NOT NULL DEFAULT 'new',
    business_name TEXT,
    business_type TEXT,
    location_city TEXT,
    location_state TEXT,
    business_stage TEXT,
    monthly_revenue TEXT,
    employee_count INTEGER,
    cac_registered BOOLEAN,
    biggest_challenge TEXT,
    language TEXT DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversation history table
CREATE TABLE IF NOT EXISTS conversations (
    id BIGSERIAL PRIMARY KEY,
    phone_number TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast conversation lookups
CREATE INDEX IF NOT EXISTS idx_conversations_phone
    ON conversations (phone_number, created_at);

-- Index for profile lookups
CREATE INDEX IF NOT EXISTS idx_profiles_state
    ON sme_profiles (state);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE sme_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- Allow the service role (your backend) full access
CREATE POLICY "Service role full access on profiles"
    ON sme_profiles FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role full access on conversations"
    ON conversations FOR ALL
    USING (true)
    WITH CHECK (true);
