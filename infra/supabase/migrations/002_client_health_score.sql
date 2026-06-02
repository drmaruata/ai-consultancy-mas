-- Migration 002: Client Health Score (CHS) Calculation RPC & Batch Processing

-- 1. Ensure `clients` table exists with required CHS columns
CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status TEXT DEFAULT 'active',
    health_score INT DEFAULT 100,
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Ensure `audit_log` table exists
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id),
    action TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Create the Historical Tracking Table
CREATE TABLE IF NOT EXISTS client_health_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id),
    score INT NOT NULL,
    calculated_at TIMESTAMPTZ DEFAULT now()
);

-- =========================================================================
-- SECURITY: DPDP Compliance & Row Level Security (PRD Section 20)
-- =========================================================================

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE client_health_scores ENABLE ROW LEVEL SECURITY;

-- Only service roles (the agents/cron) can insert or read all audit logs
CREATE POLICY "Service Role Full Access on audit_log"
ON audit_log FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Only service roles can insert or read health scores
CREATE POLICY "Service Role Full Access on client_health_scores"
ON client_health_scores FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Optionally, if clients authenticate, they can only view their own scores
CREATE POLICY "Clients can view their own health scores"
ON client_health_scores FOR SELECT TO authenticated USING (auth.uid() = client_id);

-- =========================================================================
-- CHS RPC: Batch Calculation
-- =========================================================================

-- Create a custom return type for the Agent
DROP TYPE IF EXISTS chs_calculation_result CASCADE;
CREATE TYPE chs_calculation_result AS (
    client_id UUID,
    previous_chs INT,
    new_chs INT,
    is_alert_triggered BOOLEAN
);

-- The Batch RPC Function
CREATE OR REPLACE FUNCTION calculate_weekly_chs()
RETURNS SETOF chs_calculation_result
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    client_record RECORD;
    result_record chs_calculation_result;
    
    -- 7-Factor Variables
    score_login NUMERIC;
    score_response NUMERIC;
    score_satisfaction NUMERIC;
    score_payment NUMERIC;
    score_acceptance NUMERIC;
    score_breadth NUMERIC;
    score_inbound NUMERIC;
    final_chs INT;
BEGIN
    -- Loop through all active clients (Solves N+1 problem)
    FOR client_record IN SELECT id, health_score FROM clients WHERE status = 'active'
    LOOP
        -- 1. Portal login frequency (20% weight) | Target: 3+ logins/week
        SELECT LEAST(COUNT(*) * 33.33, 100) INTO score_login
        FROM audit_log 
        WHERE client_id = client_record.id AND action = 'portal_login' AND created_at >= (NOW() - INTERVAL '7 days');

        -- 2. Response time (20% weight) | Target: < 4 hours
        SELECT COALESCE(GREATEST(100 - (AVG((metadata->>'response_time_hours')::NUMERIC) * 5), 0), 100) INTO score_response
        FROM audit_log
        WHERE client_id = client_record.id AND action = 'client_response' AND created_at >= (NOW() - INTERVAL '30 days');

        -- 3. Satisfaction Score (25% weight) | Target: 5.0 rating
        SELECT COALESCE((AVG((metadata->>'rating')::NUMERIC) / 5.0) * 100, 100) INTO score_satisfaction
        FROM audit_log
        WHERE client_id = client_record.id AND action = 'feedback_submitted' AND created_at >= (NOW() - INTERVAL '90 days');

        -- 4. Payment Timeliness (15% weight) | Target: 0 days late
        SELECT COALESCE(GREATEST(100 - (AVG((metadata->>'days_late')::NUMERIC) * 2), 0), 100) INTO score_payment
        FROM audit_log
        WHERE client_id = client_record.id AND action = 'invoice_paid' AND created_at >= (NOW() - INTERVAL '90 days');

        -- 5. Deliverable Acceptance (10% weight) | Target: 100% first-pass
        SELECT COALESCE((COUNT(CASE WHEN metadata->>'status' = 'accepted' THEN 1 END)::NUMERIC / NULLIF(COUNT(*), 0)) * 100, 100) INTO score_acceptance
        FROM audit_log
        WHERE client_id = client_record.id AND action = 'deliverable_review';

        -- 6. Cross-vertical breadth (5% weight) | Target: 2+ verticals
        SELECT LEAST(COUNT(DISTINCT metadata->>'vertical') * 50, 100) INTO score_breadth
        FROM audit_log
        WHERE client_id = client_record.id AND action = 'engagement_started';

        -- 7. Proactive Inbound (5% weight) | Target: 2+ per month
        SELECT LEAST(COUNT(*) * 50, 100) INTO score_inbound
        FROM audit_log
        WHERE client_id = client_record.id AND action = 'proactive_contact' AND created_at >= (NOW() - INTERVAL '30 days');

        -- Calculate final weighted score
        final_chs := ROUND(
            (COALESCE(score_login, 0) * 0.20) +
            (COALESCE(score_response, 0) * 0.20) +
            (COALESCE(score_satisfaction, 0) * 0.25) +
            (COALESCE(score_payment, 0) * 0.15) +
            (COALESCE(score_acceptance, 0) * 0.10) +
            (COALESCE(score_breadth, 0) * 0.05) +
            (COALESCE(score_inbound, 0) * 0.05)
        );

        -- Update main client record
        UPDATE clients SET health_score = final_chs, updated_at = NOW() WHERE id = client_record.id;

        -- Persist the result to history table
        INSERT INTO client_health_scores (client_id, score) VALUES (client_record.id, final_chs);

        -- Prepare return payload for the Ops/HR Agent
        result_record.client_id := client_record.id;
        result_record.previous_chs := COALESCE(client_record.health_score, 100);
        result_record.new_chs := final_chs;
        result_record.is_alert_triggered := (final_chs < 65 AND COALESCE(client_record.health_score, 100) >= 65);

        RETURN NEXT result_record;
    END LOOP;
END;
$$;
