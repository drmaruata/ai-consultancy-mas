-- Phase 0 Seed: IP Registry placeholder entries (Healthcare)
-- Uses actual ip_registry schema columns from 001_foundation.sql
INSERT INTO ip_registry (name, asset_type, vertical, reusability_score, tags, description, deliverable_path, status)
VALUES 
  (
    'Healthcare Data Pipeline Template',
    'Template',
    'healthcare',
    0.85,
    ARRAY['data', 'pipeline', 'etl'],
    'Reusable ETL pipeline template for ingesting EHR data into a Supabase-backed analytics store.',
    'templates/hc-data-pipeline.zip',
    'active'
  ),
  (
    'Patient Consent Form Generator',
    'Product',
    'healthcare',
    0.72,
    ARRAY['legal', 'forms', 'compliance', 'dpdp'],
    'Configurable patient consent form generator compliant with DPDP Act 2023 and ABDM requirements.',
    'products/patient-consent-generator',
    'active'
  ),
  (
    'Clinical Trial Tracker Accelerator',
    'Accelerator',
    'healthcare',
    0.90,
    ARRAY['clinical', 'trials', 'tracker', 'nabh'],
    'Accelerator for tracking clinical trial milestones, adverse events, and NABH audit readiness.',
    'accelerators/clinical-trial-tracker.zip',
    'active'
  );
