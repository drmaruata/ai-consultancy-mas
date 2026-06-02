# Secret Management & Rotation Runbook

## Overview
This document outlines the standard operating procedure for rotating secrets across the MAS Consultancy Agency platform. All secrets must be rotated every **90 days** or immediately following any suspected compromise.

## Scope
- Redpanda Kafka Credentials (SASL/SCRAM)
- Supabase Database Roles (Service Role, Postgres Role)
- Upstash Credentials (Redis, Vector, QStash)
- LLM API Keys (Anthropic, OpenAI, Google, OpenRouter)

## 1. General Principles
- **No hardcoded secrets:** Never commit any secrets to the repository. All secrets must be stored in the Secret Manager.
- **Automated sync:** Secrets should be automatically synced to GitHub Actions environments.
- **Zero-downtime rotation:** Where possible, rotate credentials by creating a secondary credential, updating the application configuration, and then revoking the primary credential after the application has fully restarted and connected successfully.

## 2. Rotation Procedures (90-Day Cadence)

### 2.1 Redpanda (Kafka)
1. Log in to the Redpanda Cloud console.
2. Navigate to **Security** -> **Users**.
3. Create a new user (e.g., `mas_service_v2`) with the exact same ACLs as the current user.
4. Update the Secret Manager with the new username and password.
5. Trigger a rolling restart of all agents connected to Redpanda.
6. Verify all connections are re-established.
7. Delete the old user from the Redpanda console.

### 2.2 Supabase
1. Log in to the Supabase dashboard.
2. Navigate to **Project Settings** -> **API**.
3. Re-generate the `service_role` secret.
4. Update the Secret Manager with the new `service_role` JWT.
5. Supabase Postgres password can be rotated under **Project Settings** -> **Database**.
6. Restart any running applications and agents.

### 2.3 Upstash (Redis, Vector, QStash)
1. Log in to the Upstash console.
2. Navigate to the respective service (Redis, Vector, or QStash).
3. In the database/index settings, use the **Reset Password / Token** functionality.
4. Note that Upstash token reset causes immediate invalidation of the old token. Ensure maintenance mode is enabled if necessary to avoid dropped requests.
5. Update the Secret Manager with the new tokens and restart services.

### 2.4 LLM APIs
1. Log in to the provider dashboard (Anthropic, OpenAI, etc.).
2. Generate a new API Key.
3. Update the Secret Manager.
4. Restart the LLM Router and verify successful connections.
5. Delete the old API Key from the provider dashboard.

## 3. Incident Response
If a secret is leaked or suspected to be compromised:
1. Immediately revoke the secret at the provider level.
2. Update the Secret Manager.
3. Inform the security team and initiate a post-mortem review.
