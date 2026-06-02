-- =============================================================================
-- AI Consultancy MAS v3.0 — Foundation Migration
-- =============================================================================
-- Creates all core tables for the MAS: agents, clients, engagements, tasks,
-- deliverables, episodic memory, IP registry, KB documents, and audit log.
-- Includes Row Level Security (RLS) policies for multi-tenant data isolation.
-- =============================================================================

-- ── Enable required extensions ──────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Agents Registry ─────────────────────────────────────────────────────────
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL UNIQUE,           -- e.g. 'healthcare-clinical-ai'
    name TEXT NOT NULL,
    tier TEXT NOT NULL,                       -- 'tier_0' through 'tier_4'
    vertical TEXT NOT NULL,                   -- 'all', 'healthcare', 'logistics', 'legal', 'edtech'
    reasoning_mode TEXT NOT NULL,             -- 'plan_and_execute' or 'react'
    description TEXT DEFAULT '',
    config JSONB NOT NULL DEFAULT '{}',       -- Full AgentConfig as JSON
    status TEXT NOT NULL DEFAULT 'active',    -- 'active', 'disabled', 'maintenance'
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_agents_tier ON agents(tier);
CREATE INDEX idx_agents_vertical ON agents(vertical);
CREATE INDEX idx_agents_status ON agents(status);

-- ── Clients ─────────────────────────────────────────────────────────────────
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT NOT NULL,
    contact_name TEXT,
    contact_email TEXT,
    vertical TEXT NOT NULL,
    tier TEXT DEFAULT 'standard',             -- 'standard', 'premium', 'enterprise'
    client_health_score NUMERIC DEFAULT 100.0,
    data_sovereignty TEXT DEFAULT 'cloud',    -- 'cloud' or 'air_gapped'
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_clients_vertical ON clients(vertical);
CREATE INDEX idx_clients_tier ON clients(tier);
CREATE INDEX idx_clients_chs ON clients(client_health_score);

-- ── Engagements ─────────────────────────────────────────────────────────────
CREATE TABLE engagements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id),
    vertical TEXT NOT NULL,
    engagement_type TEXT NOT NULL,            -- 'consulting', 'implementation', 'audit', 'retainer'
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',    -- 'draft', 'active', 'paused', 'completed', 'cancelled'
    pricing JSONB DEFAULT '{}',              -- Dynamic pricing breakdown
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_engagements_client ON engagements(client_id);
CREATE INDEX idx_engagements_status ON engagements(status);
CREATE INDEX idx_engagements_vertical ON engagements(vertical);

-- ── Tasks ───────────────────────────────────────────────────────────────────
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID REFERENCES engagements(id),
    assigned_agent_id TEXT NOT NULL,          -- References agents.agent_id
    parent_task_id UUID REFERENCES tasks(id),
    task_type TEXT NOT NULL,
    description TEXT DEFAULT '',
    priority INTEGER NOT NULL DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    status TEXT NOT NULL DEFAULT 'pending',   -- 'pending', 'assigned', 'in_progress', 'completed', 'failed', 'escalated'
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    depends_on UUID[] DEFAULT '{}',
    confidence NUMERIC,
    tokens_used INTEGER DEFAULT 0,
    duration_ms INTEGER,
    deadline TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tasks_engagement ON tasks(engagement_id);
CREATE INDEX idx_tasks_agent ON tasks(assigned_agent_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);

-- ── Deliverables ────────────────────────────────────────────────────────────
CREATE TABLE deliverables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id),
    engagement_id UUID REFERENCES engagements(id),
    client_id UUID REFERENCES clients(id),
    vertical TEXT NOT NULL,
    deliverable_type TEXT NOT NULL,
    content TEXT,                             -- The actual deliverable content
    content_path TEXT,                        -- Or a storage path reference
    qa_tier TEXT NOT NULL DEFAULT 'class_b',  -- 'class_a', 'class_b', 'class_c'
    qa_status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'revision'
    quality_score NUMERIC,
    confidence NUMERIC,
    sources_cited TEXT[] DEFAULT '{}',
    ip_assets_used UUID[] DEFAULT '{}',
    review_notes TEXT,
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_deliverables_task ON deliverables(task_id);
CREATE INDEX idx_deliverables_engagement ON deliverables(engagement_id);
CREATE INDEX idx_deliverables_qa_status ON deliverables(qa_status);

-- ── Episodic Memory ─────────────────────────────────────────────────────────
CREATE TABLE episodic_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    task_id UUID NOT NULL,
    client_id UUID,
    vertical TEXT,
    action_type TEXT NOT NULL,               -- 'plan', 'execute', 'reflect', 'escalate'
    input_summary TEXT,
    output_summary TEXT,
    quality_score NUMERIC,
    tokens_used INTEGER DEFAULT 0,
    duration_ms INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_episodic_agent ON episodic_memory(agent_id);
CREATE INDEX idx_episodic_task ON episodic_memory(task_id);
CREATE INDEX idx_episodic_vertical ON episodic_memory(vertical);
CREATE INDEX idx_episodic_created ON episodic_memory(created_at DESC);

-- ── IP Registry ─────────────────────────────────────────────────────────────
CREATE TABLE ip_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    vertical TEXT NOT NULL,
    asset_type TEXT NOT NULL,                -- 'template', 'accelerator', 'product'
    description TEXT,
    reusability_score NUMERIC DEFAULT 0.0 CHECK (reusability_score BETWEEN 0 AND 1),
    times_used INTEGER DEFAULT 0,
    source_engagement_id UUID REFERENCES engagements(id),
    deliverable_path TEXT,
    tags TEXT[] DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'active',   -- 'active', 'deprecated', 'draft'
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ip_vertical ON ip_registry(vertical);
CREATE INDEX idx_ip_asset_type ON ip_registry(asset_type);
CREATE INDEX idx_ip_reusability ON ip_registry(reusability_score DESC);
CREATE INDEX idx_ip_tags ON ip_registry USING GIN(tags);

-- ── KB Documents (metadata — content stored in vector DB) ───────────────────
CREATE TABLE kb_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    vertical TEXT NOT NULL,
    domain TEXT NOT NULL,                    -- e.g. 'NABH', 'BNS_2023', 'DGFT'
    decay_rate TEXT NOT NULL DEFAULT 'medium', -- 'fast', 'medium', 'slow'
    validity_days INTEGER NOT NULL,
    initial_confidence NUMERIC NOT NULL DEFAULT 1.0,
    current_confidence NUMERIC NOT NULL DEFAULT 1.0,
    superseded_by UUID REFERENCES kb_documents(id),
    superseded_at TIMESTAMPTZ,
    source_url TEXT,
    content_hash TEXT,                       -- SHA-256 of the content for change detection
    vector_db_id TEXT,                       -- Reference to the vector DB entry
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_validated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_kb_vertical ON kb_documents(vertical);
CREATE INDEX idx_kb_domain ON kb_documents(domain);
CREATE INDEX idx_kb_confidence ON kb_documents(current_confidence);
CREATE INDEX idx_kb_decay_rate ON kb_documents(decay_rate);

-- ── Leads (Sales Pipeline) ──────────────────────────────────────────────────
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,                    -- 'inbound_email', 'website', 'referral', 'tender'
    company_name TEXT,
    contact_name TEXT,
    contact_email TEXT,
    vertical TEXT,
    status TEXT NOT NULL DEFAULT 'new',      -- 'new', 'qualified', 'proposal_sent', 'negotiation', 'won', 'lost'
    qualification_score NUMERIC,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_vertical ON leads(vertical);

-- ── Proposals ───────────────────────────────────────────────────────────────
CREATE TABLE proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id),
    content TEXT,
    pricing JSONB DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'draft',    -- 'draft', 'sent', 'accepted', 'rejected'
    ip_assets_used UUID[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_proposals_lead ON proposals(lead_id);
CREATE INDEX idx_proposals_status ON proposals(status);

-- ── Client Health Score History ─────────────────────────────────────────────
CREATE TABLE client_health_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id),
    score NUMERIC NOT NULL,
    login_frequency_score NUMERIC DEFAULT 0,
    response_time_score NUMERIC DEFAULT 0,
    satisfaction_score NUMERIC DEFAULT 0,
    payment_timeliness_score NUMERIC DEFAULT 0,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_chs_client ON client_health_history(client_id);
CREATE INDEX idx_chs_computed ON client_health_history(computed_at DESC);

-- ── Audit Log ───────────────────────────────────────────────────────────────
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    task_id TEXT,
    action TEXT NOT NULL,                    -- 'task_started', 'task_completed', 'escalation', 'error', etc.
    result_state TEXT,
    tokens_used INTEGER DEFAULT 0,
    elapsed_ms INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_agent ON audit_log(agent_id);
CREATE INDEX idx_audit_task ON audit_log(task_id);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_created ON audit_log(created_at DESC);

-- ── Row Level Security ──────────────────────────────────────────────────────
-- Enable RLS on all client-facing tables.
-- Policies will be refined based on Supabase Auth roles.

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE engagements ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE deliverables ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE proposals ENABLE ROW LEVEL SECURITY;
ALTER TABLE client_health_history ENABLE ROW LEVEL SECURITY;

-- Service role (backend agents) can access everything
CREATE POLICY "Service role full access on clients"
    ON clients FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on engagements"
    ON engagements FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on tasks"
    ON tasks FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on deliverables"
    ON deliverables FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on leads"
    ON leads FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on proposals"
    ON proposals FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on client_health_history"
    ON client_health_history FOR ALL
    USING (auth.role() = 'service_role');

-- ── Updated-at trigger ──────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_agents_updated_at
    BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_engagements_updated_at
    BEFORE UPDATE ON engagements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ip_registry_updated_at
    BEFORE UPDATE ON ip_registry
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at
    BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_proposals_updated_at
    BEFORE UPDATE ON proposals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
