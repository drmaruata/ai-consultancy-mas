-- =============================================================================
-- AI Consultancy MAS v3.0 — Security Fixes Migration
-- =============================================================================
-- Addresses Supabase linter warnings:
-- 1. Adds explicit RLS policies for backend tables.
-- 2. Secures function search paths.
-- 3. Revokes public execution on SECURITY DEFINER functions.
-- =============================================================================

-- 1. Enable RLS and add Service Role policies for backend-only tables
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE episodic_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE ip_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access on agents" 
    ON agents FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access on audit_log" 
    ON audit_log FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access on episodic_memory" 
    ON episodic_memory FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access on ip_registry" 
    ON ip_registry FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access on kb_documents" 
    ON kb_documents FOR ALL USING (auth.role() = 'service_role');

-- 2. Secure function search_path
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER 
LANGUAGE plpgsql
SET search_path = ''
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

-- 3. Revoke public execution on default SECURITY DEFINER functions if they exist
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'rls_auto_enable') THEN
        REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM PUBLIC;
        REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM anon;
        REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM authenticated;
    END IF;
END
$$;
