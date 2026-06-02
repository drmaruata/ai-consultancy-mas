# Implementation Plan
## AI Consultancy Agency — Multi-Agent System (MAS) v4.0

---

> **Document Status:** Active
> **Version:** 4.0 (Updated from v3.0)
> **Based On:** PRD v3.0 — AI Consultancy Agency MAS (Single Source of Truth)
> **Prepared By:** Founding Team
> **Classification:** Internal — Confidential
> **Key Changes from v3.0:** Tech stack corrections (Upstash Kafka removed — discontinued March 2025; Redpanda Cloud Serverless added as primary Kafka recommendation; Confluent Cloud flagged as IBM-owned; on-premise LLMs updated to Llama 4 / Mis tral Small 4); expanded phase tasks with sub-tasks, dependencies, and Definition of Done; added Agent Implementation Framework, Observability Plan, and Testing Strategy sections.

---

## Table of Contents

1. [Executive Overview](#1-executive-overview)
2. [Implementation Principles](#2-implementation-principles)
3. [Document Governance & PRD Alignment](#3-document-governance--prd-alignment)
4. [Team & Roles](#4-team--roles)
5. [Tech Stack Specifications](#5-tech-stack-specifications)
6. [Agent Implementation Framework (Standard Recipe)](#6-agent-implementation-framework-standard-recipe)
7. [Pre-Phase Setup Checklist](#7-pre-phase-setup-checklist)
8. [Phase 0 — Foundation (Weeks 1–4)](#8-phase-0--foundation-weeks-14)
9. [Phase 1 — First Revenue (Weeks 5–8)](#9-phase-1--first-revenue-weeks-58)
10. [Phase 2 — Growth Engines (Weeks 9–14)](#10-phase-2--growth-engines-weeks-914)
11. [Phase 3 — Full Vertical Coverage (Weeks 15–22)](#11-phase-3--full-vertical-coverage-weeks-1522)
12. [Phase 4 — Intelligence Layer (Months 6–9)](#12-phase-4--intelligence-layer-months-69)
13. [Phase 5 — Hybrid AI & Institutional Scale (Month 10+)](#13-phase-5--hybrid-ai--institutional-scale-month-10)
14. [Agent Build Priority Registry](#14-agent-build-priority-registry)
15. [Infrastructure Deployment Plan](#15-infrastructure-deployment-plan)
16. [Knowledge Base (KB) Setup Plan](#16-knowledge-base-kb-setup-plan)
17. [Human Oversight Implementation](#17-human-oversight-implementation)
18. [Observability & Monitoring Plan](#18-observability--monitoring-plan)
19. [Testing Strategy](#19-testing-strategy)
20. [KPI Tracking & Milestones](#20-kpi-tracking--milestones)
21. [Risk Register & Mitigation Actions](#21-risk-register--mitigation-actions)
22. [Master Timeline Gantt Summary](#22-master-timeline-gantt-summary)

---

## 1. Executive Overview

The MAS v3.0 is a **43-agent autonomous AI consultancy** delivering services across four industry verticals: Healthcare, Logistics & Supply Chain, Legal & Compliance, and EdTech & Competitive Exams. The system runs end-to-end business operations — from client acquisition to delivery, billing, and self-improvement — with a human oversight layer retaining control over commercial commitments and high-stakes outputs.

This implementation plan translates the PRD's phased build strategy into a granular, sprint-based roadmap covering infrastructure setup, agent development, vertical activation, knowledge base construction, and institutional scaling. It spans **~14 months** across 5 phases of progressive complexity, with each phase gated by explicit exit criteria that must be met before proceeding.

### Key Objectives

| Objective | Target |
|-----------|--------|
| First autonomous revenue delivery | Week 8 |
| All 4 verticals active simultaneously | Month 6 |
| Air-gapped hybrid LLM architecture live | Month 10 |
| Autonomous engagement closure rate | ≥ 60% by Year 1 |
| Active clients | ≥ 75 by Month 24 |

### v4.0 Tech Stack Corrections (Summary)

The following corrections have been applied in this version after service status verification (June 2026):

| Issue | Old Reference | Corrected Reference |
|-------|--------------|---------------------|
| Discontinued service | Upstash Kafka (shutdown March 11, 2025) | Redpanda Cloud Serverless (primary) or Amazon MSK Serverless |
| Acquired vendor | Confluent Cloud (now IBM-owned, March 17, 2026) | Flagged with vendor lock-in advisory; still usable but noted |
| Outdated LLMs | Llama 3, Mixtral | Llama 4, Mistral Small 4 (Mixtral family successor); Ollama/vLLM serving |
| Confirmed active | Upstash Workflow (QStash — GA), Upstash Vector, Upstash Redis, Context7 MCP | No changes — all confirmed operational |

---

## 2. Implementation Principles

These guiding principles govern all build decisions across phases:

1. **PRD is the Single Source of Truth.** All agent specifications, KPIs, tech stack choices, and vertical scope are derived from PRD v3.0. Any deviation requires explicit rationale and must be documented.
2. **IP-First Delivery.** Before building bespoke solutions, always check the IP Registry. Re-use accelerates delivery and compounds ROI.
3. **Vertical Sequencing.** Healthcare activates first (highest margin, strongest differentiation); others follow in decreasing strategic complexity.
4. **Automation Before Scale.** No manual process should scale without an automated equivalent designed in parallel.
5. **KB Before Agent.** Each vertical's Knowledge Base must be seeded and validated before its agents activate in production.
6. **Oversight Gates Are Non-Negotiable.** All 6 mandatory human approval gates must be wired and tested before any relevant agent goes to production.
7. **Fail Fast on Hallucinations.** All agents traverse `Build → Unit Test → Integration Test → Staging → Human Review → Production`. Zero shortcuts.
8. **Incremental Agent Activation.** Agents are promoted to production only after passing the full testing pipeline.
9. **Verify Third-Party Services Before Building On Them.** All infrastructure services must be confirmed active and in their current pricing tier before integration work begins. (This principle was added after the Upstash Kafka deprecation gap in v3.0.)
10. **Observability From Day One.** Structured logging, distributed tracing, and agent performance metrics are configured at Phase 0, not retrofitted later.

---

## 3. Document Governance & PRD Alignment

### PRD Sections → Implementation Plan Mapping

| PRD Section | Implementation Plan Coverage |
|-------------|------------------------------|
| §4 Full MAS Topology | §6 Agent Implementation Framework; §14 Agent Build Priority Registry |
| §5–10 Vertical Agent Internals | Phase tasks in §8–13; KB seeding in §16 |
| §11 MAS Design Specification | §6 Agent Implementation Framework |
| §12 Memory Architecture | §15 Infrastructure Deployment Plan; §16 KB Setup |
| §13 Communication Architecture | §5.1 Message Bus; §15 Kafka Topic Architecture |
| §14 Human Oversight & Guardrails | §17 Human Oversight Implementation |
| §17 Technology Stack | §5 Tech Stack Specifications (all verified June 2026) |
| §18 Phased Build Plan | §8–13 Phases |
| §19 KPIs & Success Metrics | §20 KPI Tracking & Milestones |
| §20 Risks & Mitigations | §21 Risk Register & Mitigation Actions |
| Appendix A — Agent Registry v3.0 | §14 Agent Build Priority Registry |

### Change Control Protocol

Any modification to this plan that conflicts with PRD v3.0 must:
1. Be flagged with a `[DEVIATION]` tag and rationale
2. Be reviewed by the Founding Engineer and AI/ML Engineer
3. Be logged in the project's CHANGELOG before the next sprint

---

## 4. Team & Roles

| Role | Responsibilities | Phase Active |
|------|-----------------|--------------|
| **Founding Engineer / Architect** | Core infrastructure, event bus (Redpanda/Kafka), Upstash Workflow (QStash), IaC, CI/CD | Phase 0–5 |
| **AI/ML Engineer** | LLM prompt engineering, agent logic, ReAct/Plan-and-Execute frameworks, LLM Router | Phase 0–5 |
| **Backend Engineer** | Supabase schema, REST APIs, Finance Agent pricing service, integrations | Phase 1–5 |
| **Frontend Engineer** | Client portals (Next.js/Tailwind), Oversight Console (React), Flutter app | Phase 2–5 |
| **Domain Expert — Healthcare** | Clinical AI guardrails, NQAS/NABH/ABDM KB seeding and QA review | Phase 1–3 |
| **Domain Expert — Legal** | BNS/Companies Act/SEBI KB validation, disclaimer frameworks | Phase 3 |
| **Domain Expert — EdTech** | Curriculum mapping, IRT calibration, current affairs pipeline review | Phase 3–4 |
| **Human Oversight Officer** | Approval gate management, weekly MAS Health Report review | Phase 1–5 |
| **QA/Compliance Lead** | Tiered QA pipeline setup, Class C output review, security audits | Phase 1–5 |

---

## 5. Tech Stack Specifications

This section documents the confirmed-active services that constitute the MAS tech stack, aligned with PRD §17. All services have been verified as of June 2026.

### 5.1 Message Bus — Apache Kafka Protocol

The PRD specifies Apache Kafka as the inter-agent communication backbone. All agents publish and consume via Kafka topics; no direct HTTP/RPC calls between agents.

**Recommended Implementation: Redpanda Cloud Serverless**

Redpanda is a Kafka-compatible streaming platform that acts as a drop-in replacement for Apache Kafka clients with no protocol changes required. It eliminates JVM and ZooKeeper dependencies, which reduces operational overhead significantly.

| Option | Notes | Verdict |
|--------|-------|---------|
| **Redpanda Cloud Serverless** | Kafka-compatible, ~46% more cost-efficient than legacy options, no JVM/ZooKeeper, serverless pricing, independent company | ✅ **Primary Recommendation** |
| **Amazon MSK Serverless** | Fully managed Apache Kafka on AWS, serverless tier available, native AWS IAM integration | ✅ Alternative (if AWS-native) |
| **Self-hosted Apache Kafka** | Full control, free at runtime, higher ops overhead (requires K8s or VM management) | ✅ Alternative (ops-heavy) |
| ~~Upstash Kafka~~ | **DISCONTINUED March 11, 2025** | ❌ Do not use |
| **Confluent Cloud (now IBM Confluent)** | Most feature-complete Kafka platform; IBM completed acquisition March 17, 2026. Still operational but evaluate IBM vendor lock-in before committing | ⚠️ Use with caution |

**Setup Steps:**
- Create a Redpanda Cloud account at `cloud.redpanda.com`
- Provision a Serverless cluster (region: Mumbai `ap-south-1` for India-latency optimisation)
- Obtain bootstrap broker URL and SASL credentials
- Configure Kafka clients in agents using standard `confluent-kafka` Python library or `@confluentinc/kafka-javascript` — fully compatible with Redpanda

### 5.2 Workflow & DAG Execution — Upstash Workflow (QStash)

**Status: Confirmed GA and active (October 2025 GA launch; 99.97% uptime).**

Upstash Workflow is a durable, serverless DAG execution engine built on QStash. It handles multi-step agent orchestration with retry logic, failure recovery, and step-level observability.

- Docs: `upstash.com/docs/workflow`
- Use for: All multi-agent DAG pipelines across all 4 verticals
- Key feature for MAS: Step-based durable execution means a 10-step agent DAG survives transient LLM API failures without losing state
- Circuit breaker configuration: Set per-DAG timeout policies and dead-letter queues for each Vertical Manager workflow

### 5.3 Semantic Memory / Vector Store — Upstash Vector

**Status: Confirmed active.**

Upstash Vector is the semantic KB engine. It stores all KB documents with validity metadata envelopes and supports hybrid dense + sparse index for the KB validity decay system.

- Supports metadata filtering (for confidence score queries)
- DiskANN algorithm for high-recall, low-latency ANN search
- Each KB document is stored with: `{document_id, embedding, confidence_score, decay_rate, last_validated_at, vertical, superseded_by}`

### 5.4 Cache & Rate Limiting — Upstash Redis

**Status: Confirmed active.**

Used for: ephemeral agent state, LLM rate limit queues, session caching, and Upstash Workflow's internal state.

### 5.5 Relational Database — Supabase (PostgreSQL)

Used for: structured persistent data — agents, tasks, clients, IP Registry, episodic logs, pricing records, affiliate tracking, tender bids. Supabase RLS is active from Day 1 for all client-scoped tables.

### 5.6 LLM Access & Routing

| Provider | Use Case | Priority |
|----------|----------|----------|
| **Anthropic Claude API** | Primary backbone — complex reasoning, long-context | 1 (Primary) |
| **OpenAI GPT API** | Secondary — rate-limit fallback, function calling tasks | 2 |
| **Google Gemini API** | Tertiary — very long-context tasks (>200K tokens), multimodal | 3 |

**LLM Router Logic (to be built in Phase 0):**
- Route by: task complexity score, context length, estimated cost, vertical risk class
- Fallback chain: Claude → GPT → Gemini (if primary is rate-limited or unavailable)
- Track token spend per task; enforce per-task budget caps

### 5.7 On-Premise / Air-Gapped LLMs (Phase 5)

For DPDP-compliant Tier-1 Healthcare and Legal clients requiring zero external data transmission.

| Model | License | Notes |
|-------|---------|-------|
| **Llama 4 Scout/Maverick** | Meta Community License | Upgraded from Llama 3 — significantly improved reasoning; fine for most commercial deployments |
| **Mistral Small 4** | Apache 2.0 (fully open) | Production agents with function calling and structured JSON output; recommended for Legal/Healthcare tool use |
| **DeepSeek V3.1** | MIT (fully open) | High-quality alternative; strong multilingual performance |

**Serving Stack:**
- **Development / validation:** Ollama (single-binary local inference server)
- **Production air-gapped:** vLLM (production-grade tensor-parallel serving, OpenAI-compatible API)
- Agents consume the on-prem endpoint via the same LLM Router abstraction — no agent code changes required

### 5.8 Developer Tooling

| Tool | Purpose |
|------|---------|
| **GitHub (monorepo)** | Source control: `/agents`, `/shared-services`, `/verticals`, `/interfaces`, `/infra` |
| **GitHub Actions** | CI/CD — test, lint, build, deploy to staging and production |
| **OpenTelemetry** | Distributed tracing across all agent calls (details in §18) |
| **Axiom / Grafana** | Log aggregation and dashboarding |
| **Secret Manager (AWS SSM / Doppler)** | API keys, DB credentials — 90-day rotation policy |
| **Terraform or Pulumi** | Infrastructure as Code for Redpanda, Supabase, Upstash provisioning |

### 5.9 Frontend Stack

| Interface | Stack | Users |
|-----------|-------|-------|
| Hospital Portal | Next.js 15 + Tailwind CSS | B2B Healthcare clients |
| Ops Dashboard | Next.js 15 + Tailwind CSS | B2B Logistics clients |
| Legal Workspace | Next.js 15 + Tailwind CSS | B2B Legal clients |
| Learning Portal | Next.js 15 + Tailwind CSS | B2B EdTech clients |
| Internal Oversight Console | React 18 | Founders / operators |
| Aspirant App (B2C) | Flutter (latest stable) | Individual exam aspirants |

### 5.10 External Knowledge — Context7 MCP

**Status: Confirmed active. Ranked #1 MCP server in 2026 (54.1K GitHub stars, 15M+ all-time tool calls). GA; security vulnerability (ContextCrush) patched February 2026.**

Used by the AI/ML Engineer during agent development to fetch current, version-specific library documentation directly into the coding context. Prevents hallucinated API calls during agent prompt engineering and tool wiring.

---

## 6. Agent Implementation Framework (Standard Recipe)

Every agent in the MAS must be built using this standard pattern to ensure consistency, testability, and production-readiness.

### 6.1 Agent Anatomy

Each agent is composed of:

1. **System Prompt** (versioned in Supabase `agent_configs` table)
   - Role definition and constraints
   - Tool manifest and usage instructions
   - Domain pre-validation instruction: "Before generating output, check KB confidence scores for all referenced documents. If any score < 0.7, cap your output confidence accordingly."
   - Output format specification (JSON schema or structured text)
   - Mandatory disclaimer injection rules (for Legal and Healthcare agents)

2. **Tool Registry**
   - Redpanda producer (publish deliverables and status events)
   - Supabase client (read/write tasks, clients, IP Registry)
   - Upstash Vector client (semantic KB lookups)
   - Upstash Redis client (ephemeral state, distributed locks)
   - LLM Router client (model selection and fallback)
   - Vertical-specific tools (FHIR client, ERP API client, SCC Online client, etc.)

3. **Reasoning Mode** (as specified in PRD §11.2)
   - Layers 0–3 agents: **Plan-and-Execute** with mandatory Phase 0 IP Registry check
   - Layer 4 agents: **ReAct** (Reason + Act)
   - All agents: **Domain Pre-validation** before QA handoff

4. **State Machine**
   - `IDLE → TASK_RECEIVED → IP_REGISTRY_CHECK → PLANNING → EXECUTING → QA_SUBMITTED → DONE / ESCALATED`
   - State is persisted to Supabase `tasks` table at each transition

5. **Episodic Logger**
   - All task inputs, reasoning traces, tool calls, and outputs logged to `episodic_logs`
   - Powers the Self-Improvement Engine post-engagement evaluations

### 6.2 Agent Promotion Pipeline

```
LOCAL DEV → unit tests pass
    ↓
STAGING → integration tests pass + QA review (Class A minimum)
    ↓
HUMAN REVIEW → Founding Engineer + AI/ML Engineer sign-off
    ↓
PRODUCTION
```

No agent skips any stage. Regression: any production agent that fails a health check reverts to staging automatically.

### 6.3 Prompt Versioning Protocol

- All system prompts stored in Supabase `agent_configs` with `version`, `authored_by`, `created_at`, `is_active` columns
- The Self-Improvement Engine's A/B tests create candidate prompt versions in staging, never directly in production
- Prompt changes in production require Gate G6 (Founder/Engineering review)

---

## 7. Pre-Phase Setup Checklist

Complete this checklist before any Phase 0 sprint work begins. These are one-time provisioning and account setup tasks.

### Accounts & Access

- [ ] Register and verify **Redpanda Cloud** account; provision first cluster (region: Mumbai `ap-south-1`)
- [ ] Register and verify **Upstash** account; note: Upstash now offers Redis, Vector, QStash/Workflow — no Kafka
- [ ] Register **Supabase** account; create project; note connection strings
- [ ] Activate **Anthropic Claude API** — verify rate limits and tier
- [ ] Activate **OpenAI API** — verify rate limits
- [ ] Activate **Google Gemini API** — verify rate limits
- [ ] Register **GitHub** organisation; create monorepo with structure: `/agents`, `/shared-services`, `/verticals`, `/interfaces`, `/infra`
- [ ] Register secret management service (recommend **Doppler** for simplicity or **AWS SSM Parameter Store**)

### Infrastructure as Code

- [ ] Set up **Terraform** (or Pulumi) workspace for infrastructure provisioning
- [ ] Write IaC modules for: Redpanda cluster, Supabase project, Upstash resources (Redis, Vector, QStash)
- [ ] Commit all IaC to `/infra` directory in monorepo; peer-review before apply

### Environments

- [ ] Create three named environments: `local`, `staging`, `production`
- [ ] Configure GitHub Actions workflows for: `test` (on PR), `deploy-staging` (on merge to `main`), `deploy-production` (manual trigger with sign-off gate)
- [ ] Confirm staging environment mirrors production config exactly (same services, sandbox API keys)

### Developer Access

- [ ] All team members have GitHub repo access with branch protection on `main`
- [ ] All team members have read access to Redpanda staging cluster
- [ ] API keys distributed via secret manager — never committed to Git

---

## 8. Phase 0 — Foundation (Weeks 1–4)

**Goal:** All infrastructure is live, verified, and monitored. Core MAS skeleton is operational. No vertical agents deployed yet.

**Phase Dependencies:** Pre-Phase Setup Checklist 100% complete.

---

### Week 1 — Infrastructure Provisioning

#### Task 1.1: Provision Kafka-Compatible Message Bus (Redpanda)

**Owner:** Founding Engineer
**Inputs:** Redpanda Cloud account, IaC modules
**Steps:**
1. Apply Terraform module to provision Redpanda Cloud Serverless cluster (Mumbai region)
2. Create initial topics with retention and partition configuration:

| Topic | Partitions | Retention | Notes |
|-------|-----------|-----------|-------|
| `task.assigned` | 6 | 7 days | CEO Orchestrator → Vertical Managers |
| `deliverable.ready` | 6 | 7 days | All agents → Quality & Compliance Agent |
| `client.health.alert` | 3 | 30 days | Ops/HR Agent → Account Growth Agent |
| `regulatory.update.healthcare` | 3 | 90 days | Regulatory Watch → Memory & Knowledge |
| `regulatory.update.logistics` | 3 | 90 days | Same |
| `regulatory.update.legal` | 3 | 90 days | Same |
| `regulatory.update.edtech` | 3 | 90 days | Same |
| `mas.health.report` | 1 | 365 days | CEO Orchestrator → Oversight Console |

3. Test producer/consumer round-trip using `kafkacat` (now `kcat`) against Redpanda endpoint
4. Configure SASL credentials in secret manager

**Acceptance Criteria:**
- [ ] All 8 topics created and verified in Redpanda console
- [ ] Producer→Consumer round-trip latency < 50ms from staging environment
- [ ] Credentials stored in secret manager (not in any config file)

---

#### Task 1.2: Provision Supabase

**Owner:** Backend Engineer
**Steps:**
1. Create Supabase project (region: `ap-south-1` for India latency)
2. Apply initial schema migration (Phase 0 tables):

```sql
-- Core tables (Phase 0)
agents (id, name, layer, vertical, status, config_version, created_at)
tasks (id, agent_id, status, state, input_payload, output_payload, created_at, completed_at)
clients (id, name, vertical, tier, created_at)
kb_documents (id, vertical, title, source_url, confidence_score, decay_rate, last_validated_at, superseded_by, embedding_id)
ip_registry (id, title, type, vertical, reusability_score, template_url, created_at)
episodic_logs (id, task_id, agent_id, reasoning_trace, tool_calls, output, quality_score, created_at)
agent_configs (id, agent_id, version, system_prompt, is_active, authored_by, created_at)
```

3. Enable Row-Level Security (RLS) on all tables — no exceptions
4. Create Supabase service role key; store in secret manager

**Acceptance Criteria:**
- [ ] All Phase 0 tables created with correct columns and types
- [ ] RLS policies active and tested for at least one table
- [ ] Migrations committed to `/infra/supabase/migrations/`

---

#### Task 1.3: Provision Upstash Services

**Owner:** Founding Engineer
**Steps:**
1. Create **Upstash Redis** database (region: Mumbai) — note the REST URL and token
2. Create **Upstash Vector** index (dimensions: 1536 for `text-embedding-3-small` compatibility; enable hybrid dense+sparse; metadata filtering enabled)
3. Create **Upstash QStash** project — note QStash token for Workflow integration
4. Verify all three services reachable from staging environment
5. Store all credentials in secret manager

**Acceptance Criteria:**
- [ ] Redis: `SET test "ok"` / `GET test` returns `"ok"` from staging
- [ ] Vector: Upsert and query a test vector returns correct nearest neighbour
- [ ] QStash: Publish a test message and verify receipt at a webhook endpoint

---

#### Task 1.4: Build LLM Router

**Owner:** AI/ML Engineer
**Location:** `/shared-services/llm-router/`
**Steps:**
1. Implement a Python `LLMRouter` class with the following interface:
   - `route(task: Task) → LLMClient` — selects provider based on task complexity, context length, estimated cost
   - `fallback(primary_client: LLMClient, error: Exception) → LLMClient` — ordered fallback: Claude → GPT → Gemini
2. Implement per-task token budget tracking (stores actual spend in `tasks.token_spend`)
3. Implement automatic throttling: if actual spend > budget by 20%, log a `cost.overrun` warning event to Redpanda

**Acceptance Criteria:**
- [ ] Unit tests cover: primary selection, fallback trigger, budget enforcement
- [ ] Router correctly falls back from Claude to GPT on simulated rate limit
- [ ] Token spend stored per task in `tasks` table

---

#### Task 1.5: Set Up GitHub Monorepo & CI/CD

**Owner:** Founding Engineer
**Steps:**
1. Initialise monorepo structure:
```
/
├── agents/             # Individual agent modules
├── shared-services/    # LLM Router, Redpanda client, Supabase client, Upstash clients
├── verticals/          # Vertical-specific logic (healthcare/, logistics/, legal/, edtech/)
├── interfaces/         # Frontend apps (portals, oversight-console, flutter-app)
├── infra/              # Terraform IaC, Supabase migrations
└── scripts/            # Utility scripts
```
2. Configure GitHub Actions:
   - `test.yml`: Run on every PR — lint (ruff for Python, eslint for JS/TS), unit tests, type checks
   - `deploy-staging.yml`: Run on merge to `main` — deploy all changed services to staging
   - `deploy-production.yml`: Manual trigger + required reviewer sign-off — deploy to production
3. Configure branch protection: `main` requires 1 reviewer approval + all CI checks passing
4. Set up dependabot for dependency updates

**Acceptance Criteria:**
- [ ] Monorepo structure created with README in each top-level directory
- [ ] CI pipeline runs successfully on a test PR
- [ ] Branch protection rules active on `main`

---

### Week 2 — Observability & Security Baseline

#### Task 2.1: Set Up Observability Stack

**Owner:** Founding Engineer
**Details:** See §18 Observability & Monitoring Plan for full specification.

**Steps:**
1. Instrument all services with **OpenTelemetry SDK** (Python for agents, TypeScript for frontends)
2. Configure OTLP exporter → **Axiom** (recommended for simplicity) or Grafana Cloud
3. Define standard span attributes for all agent calls:
   - `agent.name`, `agent.layer`, `task.id`, `llm.provider`, `llm.model`, `token.input`, `token.output`, `kb.confidence_min`
4. Set up **Grafana** dashboard (or Axiom dashboard) with:
   - Agent call volume
   - LLM latency by provider
   - Token spend per agent per day
   - Error rate by agent
5. Set up **alerting rules**: error rate > 5% for any agent → PagerDuty/Slack alert

**Acceptance Criteria:**
- [ ] At least one test agent call produces a trace visible in the observability dashboard
- [ ] Alert fires correctly on a simulated 10% error rate

---

#### Task 2.2: Secret Management & Rotation Policy

**Owner:** Founding Engineer + QA/Compliance Lead
**Steps:**
1. Configure all service credentials in secret manager with labels: `env:staging`, `env:production`, `service:<name>`, `rotate-after:90d`
2. Write a rotation runbook in the project wiki covering: Redpanda credentials, Supabase service role, Upstash tokens, LLM API keys
3. Set calendar reminders for 90-day key rotation across all services
4. Verify that zero API keys or DB credentials appear in any committed code or CI environment variables (use secret manager references only)

**Acceptance Criteria:**
- [ ] `git grep -r "sk-" .` returns zero results
- [ ] Rotation runbook published in project wiki

---

### Week 3–4: Core Agent Skeleton

#### Task 3.1: CEO Orchestrator Agent (Layer 0) — Skeleton

**Owner:** AI/ML Engineer
**Location:** `/agents/ceo-orchestrator/`
**Reasoning Mode:** Plan-and-Execute
**Steps:**
1. Implement system prompt v1: role as strategy layer, task routing, KPI monitoring
2. Implement `route_task(task: Task) → Topic` — routes incoming tasks to the correct Redpanda topic based on task type and vertical
3. Implement `publish_task(task: Task)` — publishes to `task.assigned` topic with structured payload
4. Implement basic health monitoring: read from `tasks` table, compute completion rates
5. Unit tests: routing logic covers all 4 verticals; health computation logic

**Acceptance Criteria:**
- [ ] Orchestrator receives a test task and publishes to the correct Kafka topic
- [ ] Routing logic tested for all 4 verticals and all Layer 1 agent types
- [ ] System prompt stored in `agent_configs` with version `1.0`

---

#### Task 3.2: Memory & Knowledge Agent — Skeleton with KB Ingestion Pipeline

**Owner:** AI/ML Engineer
**Location:** `/agents/memory-knowledge/`
**Steps:**
1. Implement `ingest_document(doc: KBDocument)`:
   - Chunk document (512-token chunks with 64-token overlap)
   - Generate embeddings via `text-embedding-3-small`
   - Upsert to Upstash Vector with metadata: `{confidence_score: 1.0, decay_rate, last_validated_at, vertical, source_url}`
   - Insert record to Supabase `kb_documents` table
2. Implement `search_kb(query: str, vertical: str, min_confidence: float = 0.7) → List[KBChunk]`:
   - Query Upstash Vector with metadata filter `confidence_score >= min_confidence`
   - Return ranked chunks with confidence scores
3. Implement `get_document_confidence(doc_id: str) → float`
4. Unit tests: ingestion pipeline, search with and without confidence filter

**Acceptance Criteria:**
- [ ] A test document ingested and retrievable via semantic search
- [ ] Search correctly filters out documents below confidence threshold
- [ ] Ingestion pipeline handles chunking and overlap correctly

---

#### Task 3.3: Quality & Compliance Agent — Class A Tier

**Owner:** AI/ML Engineer
**Location:** `/agents/quality-compliance/`
**Steps:**
1. Implement Class A QA tier (< 2 minutes, pattern-matched):
   - Mandatory field checks (does deliverable contain required sections?)
   - Forbidden content checks (hallucination markers, unsupported claim flags)
   - Disclaimer presence check for Legal and Healthcare outputs
2. Implement `process_deliverable(deliverable: Deliverable) → QAResult`:
   - `QAResult` contains: `class`, `passed`, `score`, `issues`, `escalation_required`
3. Consume from `deliverable.ready` Redpanda topic
4. Unit tests: pass case, fail case (missing disclaimer), escalation trigger

**Acceptance Criteria:**
- [ ] Class A QA processes a test deliverable in < 2 minutes
- [ ] Correctly identifies a missing mandatory disclaimer and flags for escalation
- [ ] QA results written to `tasks` table

---

#### Task 3.4: IP Registry Schema & Seed Data

**Owner:** Backend Engineer
**Steps:**
1. Extend Supabase schema with full `ip_registry` columns:
   - `id, title, type (Template|Accelerator|Product), vertical, reusability_score, file_url, tags, use_count, created_at, last_used_at`
2. Add REST endpoint: `GET /ip-registry?vertical=healthcare&min_score=0.7`
3. Seed 2–3 placeholder entries (Healthcare templates to be replaced with real assets in Phase 1)

**Acceptance Criteria:**
- [ ] REST endpoint returns correctly filtered assets
- [ ] Seed data inserted and queryable

---

#### Task 3.5: Human Oversight Console v0 (Read-Only Scaffold)

**Owner:** Frontend Engineer
**Location:** `/interfaces/oversight-console/`
**Steps:**
1. Initialise React 18 + TypeScript project
2. Implement read-only views:
   - **Agent Status Board:** List of all agents with status (idle/running/error), last task time
   - **Task Log Feed:** Real-time feed from `tasks` table via Supabase realtime subscription
   - **Infrastructure Status:** Ping indicators for Redpanda, Upstash services, LLM APIs
3. Deploy to staging

**Acceptance Criteria:**
- [ ] Console loads without errors and shows live task feed from staging DB
- [ ] Infrastructure status indicators correctly reflect service health

---

#### Task 3.6: Healthcare KB Seed v0

**Owner:** Domain Expert — Healthcare
**Steps:**
1. Gather source documents: ABDM Developer Docs (v2), ABHA Registration API spec, NMC Act 2020 text, NABH 4th Edition standards summary, DPDP Act 2023 (relevant healthcare sections)
2. Tag each document with: `vertical: healthcare`, `decay_rate: fast|medium`, `source_url`, `version`
3. Run ingestion pipeline (Task 3.2) for all documents
4. Manually verify 3 semantic search queries return relevant chunks with confidence = 1.0

**Acceptance Criteria:**
- [ ] ≥ 10 healthcare documents ingested into Upstash Vector
- [ ] All documents appear in Supabase `kb_documents` with correct metadata
- [ ] 3 verified semantic search queries return expected results

---

### Phase 0 Exit Criteria (All Must Pass Before Phase 1 Begins)

- [ ] Redpanda cluster live; all 8 topics created; producer/consumer verified
- [ ] Supabase live; all Phase 0 tables created; RLS active
- [ ] Upstash Redis, Vector, QStash all operational from staging
- [ ] LLM Router tested with Claude, GPT, and Gemini; fallback chain verified
- [ ] CEO Orchestrator routes a test task via Redpanda correctly
- [ ] Memory & Knowledge Agent ingests a document and returns a semantic search result
- [ ] Class A QA pipeline processes a test deliverable
- [ ] Observability dashboard showing traces for at least one agent call
- [ ] CI/CD deploys successfully to staging
- [ ] Healthcare KB v0 seeded with ≥ 10 documents

---

## 9. Phase 1 — First Revenue (Weeks 5–8)

**Goal:** The MAS autonomously acquires a lead, generates a proposal, prices it, and delivers a Healthcare engagement. First paying client or pilot secured by end of Week 8.

**Phase Dependencies:** All Phase 0 exit criteria met.

---

### Week 5–6: Business Ops Agents

#### Task 5.1: Sales Agent

**Owner:** AI/ML Engineer
**Location:** `/agents/sales/`
**Reasoning Mode:** Plan-and-Execute (with IP Registry Phase 0 check)
**Steps:**
1. Implement Phase 0 IP Registry check: before generating any proposal, query `GET /ip-registry?vertical=<vertical>` and pre-load reusable assets into context
2. Implement lead qualification logic: score inbound leads on 5 criteria (industry fit, GDPR/DPDP data sensitivity, budget signals, urgency, vertical match)
3. Implement proposal generator: uses IP Registry assets as building blocks; fills in client-specific gap analysis from KC search results
4. Implement follow-up sequence scheduler: publishes timed follow-up tasks to Redpanda `task.assigned`
5. Implement Sales → Finance Agent handoff: on proposal approval, publish `{proposal_id, client_id, scope}` to `task.assigned` with `agent_target: finance`

**Acceptance Criteria:**
- [ ] Sales Agent generates a valid Healthcare proposal using ≥ 1 IP Registry asset
- [ ] Lead scoring logic tested for all 4 verticals
- [ ] Proposal payload correctly routed to Finance Agent via Redpanda

---

#### Task 5.2: Finance Agent v1 — Dynamic Pricing Engine

**Owner:** AI/ML Engineer + Backend Engineer
**Location:** `/agents/finance/` + `/shared-services/pricing-service/`
**Steps:**
1. Build standalone Python pricing microservice (`/shared-services/pricing-service/`):
   - Input: `{vertical, scope_complexity, client_tier, geography, urgency, ip_reuse_pct}`
   - Variables: base rate by vertical, complexity multiplier (1.0–3.0), geography adjustment, urgency premium, IP reuse discount
   - Output: `{recommended_price, price_floor, price_ceiling, rationale}`
2. Implement Finance Agent wrapper:
   - Calls pricing microservice
   - Generates invoice via template
   - Tracks estimated API cost for the engagement
3. Implement Gate G1: if `recommended_price > ₹10,00,000`, publish to `oversight.approval_queue` and halt until human sign-off received
4. Implement Gate G5: if pricing output > 2.5× base rate, same escalation as G1

**Acceptance Criteria:**
- [ ] Pricing service returns correct outputs for 5 test cases (varying vertical, tier, complexity)
- [ ] Finance Agent receives a proposal and generates a priced invoice
- [ ] Gate G1 triggers correctly for a ₹15 lakh test proposal
- [ ] Gate G5 triggers correctly for a 3× base rate scenario

---

#### Task 5.3: Human Oversight Console — Approval Queue v1

**Owner:** Frontend Engineer
**Steps:**
1. Implement approval queue UI in the Oversight Console:
   - Lists all pending gate items from `oversight.approval_queue` Redpanda topic
   - Each item shows: agent, gate type, proposal/bid summary, timestamp
   - Actions: `Approve` (writes to `tasks.oversight_approved = true` and publishes resume event) and `Reject with Note`
2. Implement Supabase realtime listener so new gate items appear without page refresh

**Acceptance Criteria:**
- [ ] Approval queue shows a test Gate G1 item within 5 seconds of publication
- [ ] Approving/rejecting an item updates the task record and resumes the agent flow

---

### Week 7–8: Healthcare Vertical v1

#### Task 7.1: Vertical Manager Agent (Healthcare)

**Owner:** AI/ML Engineer
**Location:** `/agents/verticals/healthcare/vertical-manager/`
**Steps:**
1. Implement DAG coordination via Upstash Workflow:
   - Define healthcare engagement DAG: `[EHR_Integration → Regulatory_Compliance → Clinical_AI → Health_Analytics → QA_Class_B → Deliverable_Ready]`
   - Each DAG node publishes a subtask to `task.assigned` and waits for completion event
2. Implement KPI reporting: weekly summary of engagement metrics per client
3. Implement IP Registry check at engagement start

**Acceptance Criteria:**
- [ ] Vertical Manager orchestrates a 3-agent test DAG to completion via Upstash Workflow
- [ ] DAG correctly waits for each step before proceeding
- [ ] Failed DAG node triggers appropriate escalation

---

#### Task 7.2: Regulatory Compliance Agent (Healthcare)

**Owner:** AI/ML Engineer + Domain Expert — Healthcare
**Location:** `/agents/verticals/healthcare/regulatory-compliance/`
**Steps:**
1. Implement NQAS gap analysis workflow:
   - Accept input: `{hospital_type, current_score, department_list}`
   - Retrieve NQAS standards from KB (confidence filter: 0.7+)
   - Generate gap analysis deliverable for each department
2. Implement NABH pre-assessment workflow (same pattern)
3. Implement ABDM compliance checklist workflow
4. Wire mandatory medical disclaimer to ALL outputs: `"This report is for quality improvement purposes only and does not constitute clinical advice."`
5. Connect to Class B QA gate (Task 7.4)

**Acceptance Criteria:**
- [ ] Regulatory Compliance Agent generates a valid NQAS gap analysis for a test hospital profile
- [ ] Output contains mandatory disclaimer
- [ ] Class B QA gate applied to output

---

#### Task 7.3: EHR Integration Agent

**Owner:** AI/ML Engineer
**Location:** `/agents/verticals/healthcare/ehr-integration/`
**Steps:**
1. Implement FHIR R4 resource mapping guide generator (HL7 FHIR R4 spec in KB)
2. Implement HL7 v2 to FHIR R4 transformation architecture design workflow
3. Implement ABHA integration design guide generator (ABDM HIP/HIU patterns)
4. Implement HMIS setup workflow template
5. All outputs go through Class B QA

**Acceptance Criteria:**
- [ ] EHR Agent generates a valid FHIR R4 mapping guide for a test hospital HIS configuration
- [ ] ABHA integration guide cites current ABDM developer documentation (via KB lookup)

---

#### Task 7.4: Quality & Compliance Agent — Class B Tier

**Owner:** AI/ML Engineer
**Steps (extending Task 3.3):**
1. Implement Class B QA tier (< 15 minutes, full LLM validation):
   - Full LLM review of deliverable against KB-retrieved domain standards
   - Citation check: all regulatory citations verified against KB documents
   - Accuracy scoring: 0–100 quality score
   - Escalation to Class C if clinical recommendation detected
2. Update `agent_configs` for QA agent with Class B prompt version

**Acceptance Criteria:**
- [ ] Class B QA applied to an NQAS gap analysis in < 15 minutes
- [ ] Quality score computed and stored in `tasks` table
- [ ] Clinical recommendation correctly escalates to Class C flag

---

#### Task 7.5: End-to-End Simulation Test

**Owner:** Full Team
**Goal:** Validate the complete lead-to-delivery flow before onboarding real clients.
**Test Scenario:** Simulate a district hospital requesting NQAS pre-assessment.

Steps:
1. Insert test lead into Sales Agent
2. Verify Sales Agent generates proposal using IP Registry assets
3. Verify Finance Agent prices the proposal (should be < ₹10L for the simulated scope)
4. Manually trigger HC Vertical Manager with engagement parameters
5. Verify Regulatory Compliance Agent + EHR Integration Agent both complete tasks
6. Verify Class B QA applied and quality score stored
7. Verify deliverable published to `deliverable.ready` Redpanda topic
8. Verify episodic log entries created for all agent steps

**Acceptance Criteria:**
- [ ] Full flow completes without manual intervention
- [ ] All Redpanda topic events fire in correct order
- [ ] Quality score ≥ 70/100 on simulated NQAS gap analysis
- [ ] Episodic logs complete for all 5+ agent steps

---

### Phase 1 Exit Criteria

- [ ] Sales Agent generates a valid proposal using IP Registry assets
- [ ] Finance Agent prices a proposal with dynamic variables applied
- [ ] Healthcare Vertical Manager orchestrates a 3+ agent DAG successfully via Upstash Workflow
- [ ] NQAS gap analysis deliverable passes Class B QA
- [ ] Gate G1 approval gate triggers correctly for high-value contracts
- [ ] End-to-End simulation test passes
- [ ] First paying client or pilot engagement signed

---

## 10. Phase 2 — Growth Engines (Weeks 9–14)

**Goal:** Client retention tools activated; Logistics vertical live; platform scalability validated.

**Phase Dependencies:** All Phase 1 exit criteria met.

---

### Week 9–10: Retention & Growth Agents

#### Task 9.1: Ops / HR Agent — with Client Health Scoring (CHS)

**Owner:** AI/ML Engineer
**Location:** `/agents/ops-hr/`
**Steps:**
1. Implement weekly CHS computation (runs every Monday, cron-triggered via Upstash QStash):
   - Formula: `CHS = (login_frequency × 0.3) + (response_time_score × 0.2) + (satisfaction_score × 0.3) + (payment_timeliness × 0.2)` → 0–100
   - Pull data from: Supabase client activity logs, invoice payment records
2. Persist computed scores to `client_health_scores` table (Supabase)
3. Publish alert event: if `CHS < 65`, publish `{client_id, chs_score, chs_history}` to `client.health.alert` Redpanda topic
4. Implement vendor management workflows (SLA monitoring, vendor performance logs)

**Acceptance Criteria:**
- [ ] CHS computed for 3 test clients with correct weighted scores
- [ ] Alert fires on Redpanda for a client with CHS = 60 (< 65 threshold)
- [ ] Scores stored in `client_health_scores` with timestamp

---

#### Task 9.2: Account Growth Agent

**Owner:** AI/ML Engineer
**Location:** `/agents/account-growth/`
**Steps:**
1. Implement trigger: subscribe to `client.health.alert` Redpanda topic
2. On alert receipt, pull client engagement history from `episodic_logs`
3. Query IP Registry for cross-vertical or expansion opportunities matching client profile
4. Generate personalised upsell/cross-sell proposal draft
5. Publish draft to oversight console for human review before sending to client

**Acceptance Criteria:**
- [ ] Account Growth Agent fires within 60 seconds of a CHS alert being published
- [ ] Generated proposal references at least 1 IP Registry asset
- [ ] Draft routed to oversight console (not sent to client directly)

---

#### Task 9.3: Finance Agent Extension — Affiliate Tracking Schema

**Owner:** Backend Engineer
**Steps:**
1. Add Supabase tables:
   - `affiliate_partners (id, name, tier, commission_rate, referral_code, status, created_at)`
   - `affiliate_referrals (id, partner_id, client_id, referral_date, engagement_value, commission_earned, paid_at)`
2. Add REST endpoints: `POST /affiliates`, `GET /affiliates/:id/performance`
3. Wire Finance Agent to compute commission on new engagements where `client.referred_by` is set

**Acceptance Criteria:**
- [ ] Affiliate schema created in Supabase
- [ ] Finance Agent correctly computes commission for a test referral

---

### Week 11–13: Logistics Vertical

#### Task 11.1: Logistics KB Seed

**Owner:** AI/ML Engineer (with Domain Research)
**Documents to ingest:**
- DGFT Foreign Trade Policy 2023 (relevant chapters)
- Customs Tariff Act (ITC-HS codes reference)
- GSTN e-way bill rules (current version)
- Warehousing (Development & Regulation) Act 2007
- SAP S/4HANA Supply Chain API documentation
- Oracle SCM Cloud API reference
- IATA Dangerous Goods Regulations (summary)

**Steps:** Follow KB ingestion pipeline (§3.2). Tag all documents with `vertical: logistics`, appropriate `decay_rate`.

**Acceptance Criteria:**
- [ ] ≥ 15 logistics documents ingested
- [ ] Semantic search returns relevant DGFT results for query "export license requirements"

---

#### Task 11.2: Logistics Vertical — All 7 Agents

Build in the following dependency order:

| Agent | Location | Key Capability | QA Class |
|-------|----------|----------------|----------|
| Vertical Manager (Logistics) | `/agents/verticals/logistics/vertical-manager/` | DAG coordination via Upstash Workflow | N/A |
| Supply Chain Agent | `/agents/verticals/logistics/supply-chain/` | Visibility architecture, supplier risk scoring | Class B |
| Inventory Agent | `/agents/verticals/logistics/inventory/` | ABC-XYZ analysis, safety stock, multi-warehouse balancing | Class B |
| Demand Forecaster Agent | `/agents/verticals/logistics/demand-forecaster/` | ARIMA/Prophet ML via Python FastAPI microservice | Class B |
| Route Optimizer Agent | `/agents/verticals/logistics/route-optimizer/` | VRP solver integration, EV fleet transition feasibility | Class B |
| ERP Integration Agent | `/agents/verticals/logistics/erp-integration/` | SAP S/4HANA, Oracle SCM, Tally Prime connector architecture | Class B |
| Trade Compliance Agent | `/agents/verticals/logistics/trade-compliance/` | HS code classification, DGFT license checks, export promotions | Class B |

**Build Steps for each agent:**
1. Implement system prompt with domain-specific instructions and IP Registry Phase 0 check
2. Wire to Logistics KB (Upstash Vector with `vertical: logistics` filter)
3. Implement core tool(s) (domain-specific APIs or generators)
4. Implement Class B QA handoff
5. Write unit tests and integration test with Vertical Manager DAG
6. Deploy to staging and run sample engagement

**Demand Forecaster Agent — Special Instruction:**
Build as a FastAPI Python microservice (`/shared-services/demand-forecaster-service/`) that:
- Accepts time-series JSON payload
- Runs ARIMA and Prophet models
- Returns forecast with confidence intervals
- The Demand Forecaster Agent calls this service as a tool

**Acceptance Criteria:**
- [ ] All 7 Logistics agents pass unit tests
- [ ] Vertical Manager coordinates a 3-agent Logistics DAG to completion
- [ ] Demand Forecaster service returns a forecast for a 12-month test series
- [ ] Trade Compliance Agent correctly classifies 5 test HS codes
- [ ] Logistics Ops Dashboard accessible to at least 1 test client

---

#### Task 11.3: Ops Dashboard (Logistics Client Portal) — Scaffold

**Owner:** Frontend Engineer
**Location:** `/interfaces/ops-dashboard/`
**Steps:**
1. Initialise Next.js 15 + Tailwind CSS project
2. Implement: delivery tracking view, inventory alerts panel, demand forecast chart (Recharts), compliance status board
3. Supabase Realtime subscription for live task updates

**Acceptance Criteria:**
- [ ] Dashboard loads and displays test data from staging DB
- [ ] Live update fires within 3 seconds of a task status change in Supabase

---

### Week 13–14: Healthcare Vertical Expansion

#### Task 13.1: Remaining 4 Healthcare Agents

| Agent | Key Capability | Notes |
|-------|----------------|-------|
| Clinical AI Agent (with Bioinformatics) | CDSS design, genomic pipeline architecture, ICU early-warning model design | **Guardrail:** No individual patient diagnosis. Mandatory disclaimer on ALL outputs. Class C QA gate. |
| Health Analytics Agent | Bed management dashboards, mortality analysis, infection control reporting | Class B QA |
| Pharma Supply Agent | EML stock optimisation, FEFO tracking, cold chain monitoring architecture | Class B QA |
| Patient Engagement Agent | Multilingual NLP chatbot design, ABHA PHR integration architecture, post-discharge automation | Class B QA |

**Build steps:** Follow §6.1 Agent Anatomy for each; wire to Healthcare KB; wire to appropriate QA class.

---

#### Task 13.2: Quality & Compliance Agent — Class C Tier

**Owner:** QA/Compliance Lead + AI/ML Engineer
**Steps:**
1. Implement Class C QA gate (human review required):
   - Triggered by: Clinical AI outputs, Legal opinion-class outputs
   - Publishes item to `oversight.approval_queue` (Gate G3 for healthcare, Gate G4 for legal)
   - Halts deliverable delivery until human expert approves
   - Human reviewer sees: full deliverable, QA Class A + B scores, KB citations
2. Implement Class C notification: email + Oversight Console alert to Domain Expert

**Acceptance Criteria:**
- [ ] Class C gate fires on a Clinical AI output
- [ ] Deliverable held until human approval received
- [ ] Approval action in Oversight Console resumes delivery

---

### Phase 2 Exit Criteria

- [ ] CHS computed weekly for all active clients; alerts firing correctly
- [ ] Account Growth Agent drafts a cross-sell proposal autonomously on CHS alert
- [ ] All 7 Logistics vertical agents operational and passing QA
- [ ] Logistics Ops Dashboard accessible to pilot client
- [ ] All 7 Healthcare agents operational (including expansion agents)
- [ ] Class C QA gate enforced for clinical content
- [ ] Demand Forecaster microservice deployed and tested

---

## 11. Phase 3 — Full Vertical Coverage (Weeks 15–22)

**Goal:** Legal and EdTech verticals live. KB validity decay system active. B2C flywheel initiated.

**Phase Dependencies:** All Phase 2 exit criteria met.

---

### Week 15–17: Legal & Compliance Vertical

#### Task 15.1: Legal KB Seed

**Owner:** Domain Expert — Legal
**Documents to ingest:**
- Bharatiya Nyaya Sanhita (BNS) 2023 — full text
- Companies Act 2013 (consolidated, with 2024 amendments)
- SEBI LODR Regulations 2015 (current version from SEBI website)
- RBI Master Directions (key directions: Digital Lending, PPI, Account Aggregator)
- DPDP Act 2023 — full text
- SEBI circular index (current year) — Regulatory Watch Agent seed data

All tagged `vertical: legal`, `decay_rate: fast` (180-day decay for all regulatory documents).

**Acceptance Criteria:**
- [ ] ≥ 20 legal documents ingested
- [ ] Semantic search returns relevant BNS 2023 results for query "theft punishment"

---

#### Task 15.2: Legal Vertical — All 7 Agents

| Agent | Location | Key Capability |
|-------|----------|----------------|
| Vertical Manager (Legal) | `/agents/verticals/legal/vertical-manager/` | DAG coordination; **MANDATORY DISCLAIMER appended to ALL outputs** |
| Contract Analysis Agent | `/agents/verticals/legal/contract-analysis/` | AI redlining, clause extraction, change-of-control detection |
| Regulatory Watch Agent | `/agents/verticals/legal/regulatory-watch/` | SEBI/RBI/MCA portal scraping; **PRIMARY KB supersession publisher** |
| Legal Research Agent | `/agents/verticals/legal/legal-research/` | SCC Online and Manupatra API integrations; case law summarisation |
| Risk Assessment Agent | `/agents/verticals/legal/risk-assessment/` | DPDP data protection risk heatmaps, exposure scoring |
| Policy Drafting Agent | `/agents/verticals/legal/policy-drafting/` | DPDP-compliant privacy policies, SaaS Terms of Service |
| Litigation Support Agent | `/agents/verticals/legal/litigation-support/` | Chronology construction, discovery request drafting |

**Legal Vertical Manager — Special Requirement:**
Every output from any Legal vertical agent must have this disclaimer appended before delivery:

> *"This document is prepared for informational purposes only and does not constitute legal advice. Consult a qualified legal professional before taking any action based on this analysis."*

**Regulatory Watch Agent — Special Requirement:**
This agent is the PRIMARY publisher of supersession events. Implementation:
1. Scheduled scraper (Upstash QStash cron, daily) hits: `sebi.gov.in/sebiweb/other/OtherAction.do?doListing=yes`, `rbi.org.in/Scripts/BS_ViewMasterDirections.aspx`, `mca.gov.in/content/mca/global/en/acts-rules/aci.html`
2. Detects new/amended instruments by comparing against `kb_documents.source_url` inventory
3. On detection: publishes `{vertical: "legal", new_document_url, supersedes_id}` to `regulatory.update.legal` Redpanda topic
4. Memory & Knowledge Agent consumes this event and:
   - Sets `superseded_id.confidence_score = 0.0` immediately
   - Triggers ingestion of the new document
   - Notifies all active Legal agents via ephemeral Redis flag

**Acceptance Criteria:**
- [ ] All 7 Legal agents pass unit tests
- [ ] Legal Vertical Manager DAG completes a contract analysis engagement end-to-end
- [ ] Regulatory Watch Agent detects a simulated new SEBI circular and drops KB confidence to 0
- [ ] All legal outputs contain mandatory disclaimer

---

### Week 18–20: EdTech Vertical & B2C Flywheel

#### Task 18.1: EdTech KB Seed

**Owner:** Domain Expert — EdTech
**Documents to ingest:**
- UPSC syllabus: GS Papers I–IV, Essay, Optional (static — slow decay 720d)
- NEET syllabus (Biology, Physics, Chemistry)
- JEE Main + Advanced syllabus
- NCERT textbooks (6–12, all subjects) — PDFs to text extraction
- Past 10 years UPSC Prelims + Mains question papers
- Supreme Court Judgments Index (seed from SCC Online summary feed)
- Current Affairs pipeline seed data (configured separately in Task 18.3)

**Acceptance Criteria:**
- [ ] ≥ 50 EdTech documents ingested (NCERT + syllabi + past papers)
- [ ] Static documents tagged `decay_rate: slow (720d)`, current affairs feed tagged `decay_rate: realtime`

---

#### Task 18.2: Real-Time Current Affairs Pipeline

**Owner:** AI/ML Engineer + Backend Engineer
**Location:** `/shared-services/current-affairs-pipeline/`
**Steps:**
1. Build scheduled ingestion job (Upstash QStash, daily at 06:00 IST):
   - Sources: The Hindu RSS, PIB daily release, Economic Survey (annual), RBI MPC minutes, SC recent judgment summaries
   - Fetch and deduplicate articles
   - Filter: discard pure editorial/opinion pieces (detect via NLP classifier)
   - Map remaining articles to UPSC syllabus nodes (GS I–IV topic taxonomy)
2. Ingest mapped articles into Upstash Vector with `decay_rate: realtime` (effectively permanent until manually removed)
3. Update `kb_documents` with article metadata

**Acceptance Criteria:**
- [ ] Pipeline runs on schedule and ingests ≥ 10 articles daily
- [ ] Editorial filter correctly removes ≥ 80% of pure opinion pieces in test set
- [ ] Articles mapped to correct GS syllabus nodes (validated by Domain Expert — EdTech)

---

#### Task 18.3: EdTech Vertical — All 7 Agents

| Agent | Key Capability | Notes |
|-------|----------------|-------|
| Vertical Manager (EdTech) | B2B project + B2C continuous service management | Manages both tracks simultaneously |
| Curriculum Design Agent (Dynamic) | Syllabus mapping + real-time current affairs integration | v3.0: Updates GS syllabus nodes daily via Task 18.2 pipeline |
| Assessment Agent | MCQ generation, mock test calibration via IRT | IRT calibration via Python microservice |
| Adaptive Tutor Agent | SM-2 spaced repetition, personalised learning paths | Core B2C flywheel engine |
| Exam Strategist Agent | Macro-level exam prep plans, timing strategies | Class B QA |
| Performance Analytics Agent | Score heatmaps, percentile rankings, cohort intelligence | **Anonymises B2C data before B2B syndication** |
| LMS Integration Agent | Next.js + Tailwind + Flutter + Supabase platform architecture design | v3.0: Deprecates Moodle recommendations |

**B2C Flywheel Implementation:**
1. Aspirant App (Flutter) collects: quiz responses, study session durations, topic performance scores
2. Adaptive Tutor Agent updates SM-2 spaced repetition intervals per user
3. Performance Analytics Agent aggregates anonymised cohort data: `{topic, avg_score, time_to_mastery, common_errors}` → strips all PII before writing to `cohort_intelligence` table
4. B2B EdTech clients purchase cohort intelligence reports from this table

**Acceptance Criteria:**
- [ ] All 7 EdTech agents pass unit tests
- [ ] Adaptive Tutor Agent generates a personalised study plan using SM-2 algorithm
- [ ] Performance Analytics Agent correctly anonymises a test dataset (zero PII fields in output)
- [ ] LMS Integration Agent generates a valid Next.js + Supabase architecture specification

---

#### Task 18.4: Flutter Aspirant App — Beta Launch

**Owner:** Frontend Engineer
**Location:** `/interfaces/flutter-app/`
**Steps:**
1. Implement core screens: Onboarding, Dashboard, Study Planner (Adaptive Tutor), Mock Test (Assessment Agent), Performance Charts
2. Connect to Supabase backend (auth via Supabase Auth, data via Supabase REST)
3. Submit to TestFlight (iOS) and Google Play Internal Testing track
4. Recruit 50 beta users from target aspirant communities

**Acceptance Criteria:**
- [ ] App available on TestFlight and Play Beta
- [ ] ≥ 20 active beta users in first week
- [ ] Adaptive Tutor generates personalised plans for all active users

---

### Week 20–22: KB Validity Decay & Shared Services Hardening

#### Task 20.1: KB Validity Decay Engine

**Owner:** AI/ML Engineer + Backend Engineer
**Steps:**
1. Implement `compute_decay(doc: KBDocument, current_date: datetime) → float`:
   - Formula: `confidence = max(0.0, initial_confidence × e^(-λ × days_since_validation))`
   - Decay constants (λ): Fast (180d half-life) = `ln(2)/180 ≈ 0.00385`, Medium (365d) = `0.00190`, Slow (720d) = `0.000963`
   - Floor at 0.0; never below
2. Run decay computation daily via Upstash QStash cron (04:00 IST daily)
3. Update `kb_documents.confidence_score` in Supabase for all documents
4. Update corresponding vector metadata in Upstash Vector
5. Implement confidence threshold cap: if `confidence_score < 0.7`, all agent outputs citing this document must append: `"[Warning: This citation is based on a document whose confidence score has decayed below 0.7. Verify against the latest official source.]"`

**Acceptance Criteria:**
- [ ] Decay computation correct for all 3 decay rate categories (verified against formula)
- [ ] Supabase and Upstash Vector both updated on daily cron run
- [ ] Confidence cap warning correctly appended to a test agent output citing a decayed document

---

#### Task 20.2: Self-Improvement Engine

**Owner:** AI/ML Engineer
**Location:** `/agents/self-improvement/`
**Steps:**
1. Implement post-engagement evaluator:
   - Triggered by: QA score written to completed task
   - Computes: delta between Class A and Class B scores; identifies failure categories
2. Implement IP candidacy scorer:
   - After each engagement, evaluate deliverable for reusability: score `{template_potential, accelerator_potential, product_potential}`
   - If any score > 0.8, write candidate to `ip_registry` with `status: candidate` for human review
3. Implement A/B prompt testing framework:
   - Creates candidate prompt versions in `agent_configs` with `status: staging`
   - Runs A/B test on staging engagements for 2 sprints
   - Promotes winning version if quality score delta > +5 points

**Acceptance Criteria:**
- [ ] Post-engagement evaluator produces a failure category report for a test engagement
- [ ] IP candidacy scorer correctly flags a high-reusability deliverable
- [ ] A/B test framework promotes a winning prompt in a simulated test run

---

### Phase 3 Exit Criteria

- [ ] All 4 verticals simultaneously delivering to at least 1 active client each
- [ ] KB validity decay running for all KB documents across all verticals
- [ ] Supersession events from Regulatory Watch Agent propagating correctly (KB confidence drops to 0)
- [ ] EdTech B2C Aspirant App publicly accessible on TestFlight and Play Beta
- [ ] B2C flywheel: anonymised performance data flowing to cohort intelligence table
- [ ] Self-Improvement Engine running post-engagement evaluations
- [ ] Real-Time Current Affairs Pipeline ingesting daily

---

## 12. Phase 4 — Intelligence Layer (Months 6–9)

**Goal:** Platform becomes self-improving and data-driven. Market intelligence, dynamic pricing v2, and weekly MAS Health Reports are fully automated.

**Phase Dependencies:** All Phase 3 exit criteria met.

---

### Month 6–7

#### Task M6.1: Market Intelligence Agent

**Owner:** AI/ML Engineer
**Location:** `/agents/market-intelligence/`
**Steps:**
1. Implement weekly scraping pipeline (Upstash QStash cron, every Sunday):
   - Competitor site monitoring: detect new service pages, pricing changes, case studies
   - VC funding tracker: Crunchbase / YourStory RSS for healthtech, legaltech, edtech funding rounds
   - Regulatory pipeline scanner: Ministry websites for upcoming rule changes
2. Compile weekly digest: `{competitor_moves, funding_intel, regulatory_pipeline, opportunities}`
3. Publish digest to `market.intel` Redpanda topic — consumed by CEO Orchestrator, Marketing Agent, Sales Agent

**Acceptance Criteria:**
- [ ] Market Intelligence Agent generates a structured digest for a test week
- [ ] Digest published to Redpanda and consumed by CEO Orchestrator

---

#### Task M6.2: CEO Orchestrator — Automated MAS Health Report

**Owner:** AI/ML Engineer
**Upgrade to existing CEO Orchestrator agent.**
**Steps:**
1. Implement weekly Monday report generator (Upstash QStash cron, every Monday 08:00 IST):
   - Pull: revenue snapshot from `pricing_records`, agent performance from `tasks`, CHS distribution from `client_health_scores`, KB health from `kb_documents`, market intel from `market.intel` Redpanda topic, affiliate performance from `affiliate_referrals`
2. Render report as structured JSON: `{report_date, revenue, agent_performance, client_health, kb_health, market_intel, affiliate_performance, tender_pipeline}`
3. Publish to `mas.health.report` Redpanda topic
4. Write rendered HTML report to Supabase `health_reports` table

**Acceptance Criteria:**
- [ ] CEO Orchestrator generates a complete health report every Monday
- [ ] All 7 report sections populated with non-null data
- [ ] Report visible in Oversight Console health report view

---

#### Task M6.3: Finance Agent — Dynamic Pricing v2

**Owner:** AI/ML Engineer + Backend Engineer
**Upgrade to pricing microservice.**
**Steps:**
1. Extend pricing microservice with 3 new signals:
   - `competitive_context`: adjusts ceiling based on Market Intelligence Agent's competitor pricing data
   - `client_lifetime_value`: applies LTV-based discount for high-LTV clients
   - `seasonal_demand`: adjusts urgency premium based on industry calendar (e.g., hospital accreditation cycles, tax season)
2. Implement A/B testing for pricing model variants: track win rate and margin by variant

**Acceptance Criteria:**
- [ ] Pricing v2 correctly incorporates all 5 original + 3 new signals
- [ ] A/B test framework tracks pricing variant performance
- [ ] Gate G5 re-tested with v2 pricing logic

---

#### Task M6.4: Oversight Console — MAS Health Report View

**Owner:** Frontend Engineer
**Steps:**
1. Add Health Report tab to Oversight Console:
   - Revenue trend (line chart)
   - Agent performance table (quality score, escalation rate, SLA adherence)
   - CHS distribution histogram
   - KB health table (documents near decay threshold)
   - Market intel summary
2. Set alert indicators: red badge on any section with critical findings

**Acceptance Criteria:**
- [ ] Health Report view renders all 7 sections correctly
- [ ] Alert badge appears when any agent's escalation rate > 15%

---

### Month 7–8

#### Task M7.1: Marketing Agent

**Owner:** AI/ML Engineer
**Location:** `/agents/marketing/`
**Steps:**
1. Implement weekly content pipeline:
   - Pull 1 completed engagement per vertical from `ip_registry` (recently approved)
   - Generate LinkedIn post draft (800–1200 words, domain-specific angle)
   - Queue for human review before publication
2. Implement IP-to-case-study pipeline:
   - On IP Registry asset reaching `reusability_score > 0.85`, auto-draft a case study
   - Draft includes: problem framing, approach, outcomes, redacted client name
3. Implement affiliate asset generator (for Phase 5 affiliate network):
   - Generates 3 promotional banner copy variants for each affiliate partner
   - Generates email nurture sequence for affiliate partner's audience

**Acceptance Criteria:**
- [ ] Marketing Agent generates LinkedIn post drafts for all 4 verticals
- [ ] Case study auto-drafted for a test IP Registry asset
- [ ] Affiliate assets generated for a test partner

---

#### Task M7.2: Remaining Shared Services — Agents 40–43

| Agent | Location | Function |
|-------|----------|----------|
| IP Registry Engine (40) | `/shared-services/ip-registry-engine/` | Automated reusability scoring; writes candidates to `ip_registry`; triggers IP-to-case-study |
| KB Validity Engine (41) | `/shared-services/kb-validity-engine/` | Scheduled daily decay computation; supersession event processor |
| Pricing Model Microservice (42) | `/shared-services/pricing-service/` | Already built in Phase 1; v2 extended in M6.3 |
| Anonymisation Pipeline (43) | `/shared-services/anonymisation-pipeline/` | PII stripping for EdTech B2C data before B2B syndication; must pass DPDP Act compliance review |

**Acceptance Criteria for each:**
- [ ] IP Registry Engine automatically scores 5 test deliverables; 2 correctly flagged as candidates
- [ ] KB Validity Engine runs daily and updates all document scores
- [ ] Anonymisation Pipeline passes DPDP compliance review by QA/Compliance Lead

---

### Month 8–9

#### Task M8.1: B2C Aspirant App — Full Public Launch

**Owner:** Frontend Engineer
**Steps:**
1. Complete beta feedback integrations
2. App Store review submission (iOS)
3. Google Play public release
4. In-app subscription integration (Razorpay or Google Play Billing for premium study plans)

**Acceptance Criteria:**
- [ ] App publicly available on App Store and Google Play
- [ ] Payment flow tested end-to-end for a ₹499/month test subscription

---

#### Task M8.2: Load & Stress Testing

**Owner:** Founding Engineer
**Steps:**
1. Use `locust` (Python) to simulate load across all 43 agents simultaneously
2. Simulate: 40 concurrent engagements across all 4 verticals
3. Measure: Redpanda topic throughput, Upstash Workflow execution latency, LLM Router queue depth, Supabase read/write latency under load
4. Identify bottlenecks; resolve before Phase 5

**Acceptance Criteria:**
- [ ] 40 concurrent engagement simulation completes without Redpanda topic lag > 5 seconds
- [ ] All Upstash Workflow DAGs complete correctly under load
- [ ] No LLM Router failures during the 20% cost overage throttle test

---

#### Task M8.3: Security Audit

**Owner:** QA/Compliance Lead
**Scope:**
1. Supabase RLS policies — verify no table is accessible without correct user context
2. PII stripping pipeline — verify zero PII in output of Anonymisation Pipeline (Agent 43)
3. API key rotation — rotate all keys; verify services still operational after rotation
4. Redpanda access control — verify topic-level ACLs are active for all topics
5. OWASP top-10 review for all client portal Next.js apps

**Acceptance Criteria:**
- [ ] All RLS policies audited and verified
- [ ] Zero PII leakage in Anonymisation Pipeline test
- [ ] All API keys rotated; all services verified operational post-rotation
- [ ] OWASP audit report produced; all Critical findings resolved

---

### Phase 4 Exit Criteria

- [ ] CEO Orchestrator delivers automated MAS Health Report every Monday
- [ ] Market Intelligence Agent digest delivered to relevant agents weekly
- [ ] Dynamic Pricing v2 active for all new proposals
- [ ] Marketing Agent publishing content autonomously per vertical
- [ ] All 43 agents operational and passing integration tests
- [ ] Load test passed (40 concurrent engagements)
- [ ] Security audit passed
- [ ] B2C Aspirant App publicly live

---

## 13. Phase 5 — Hybrid AI & Institutional Scale (Month 10+)

**Goal:** Air-gapped LLM infrastructure for Tier-1 clients. Government Tender Bidding Agent active. High-Ticket Affiliate Marketing network live.

**Phase Dependencies:** All Phase 4 exit criteria met.

---

### Month 10–11: Hybrid AI Deployment

#### Task M10.1: Air-Gapped LLM Architecture Design

**Owner:** Founding Engineer + AI/ML Engineer
**Steps:**
1. Design and document the air-gapped deployment architecture:
   - Client hardware spec (minimum: 2× NVIDIA A100 80GB or equivalent for Llama 4 Scout / Mistral Small 4)
   - Network isolation requirements: no outbound calls to any external API
   - vLLM serving stack setup on client hardware
   - OpenAI-compatible API endpoint configuration (so LLM Router requires zero changes)
2. Produce deployment runbook: step-by-step hardware setup, vLLM install, model download (via USB/SFTP if air-gapped), API configuration, health check verification

**Model Recommendations:**
- **Llama 4 Scout** (Meta Community License): 109B total, 17B active via MoE — capable reasoning on 2× A100 setup
- **Mistral Small 4** (Apache 2.0): Production-ready, excellent function calling, recommended for Legal contracts and Healthcare compliance (smaller hardware footprint than Llama 4)
- **DeepSeek V3.1** (MIT): High-quality alternative; evaluate against Mistral Small 4 in pilot

**Acceptance Criteria:**
- [ ] Deployment runbook reviewed and approved by Founding Engineer
- [ ] Hardware requirements documented clearly for client procurement team
- [ ] vLLM serving stack tested locally with Mistral Small 4

---

#### Task M10.2: On-Premise LLM Wrapper

**Owner:** AI/ML Engineer
**Steps:**
1. Build `OnPremLLMClient` class that:
   - Implements the same interface as the cloud LLM clients in the LLM Router
   - Calls local vLLM endpoint (`http://localhost:8000/v1/chat/completions`)
   - Tracks token usage locally (no external API for usage data)
2. Update LLM Router: add `on_prem` as a fourth routing option
3. Routing condition: if `client.data_sensitivity == "air_gapped"`, always route to `on_prem`; never fall back to cloud

**Acceptance Criteria:**
- [ ] `OnPremLLMClient` passes all LLM Router unit tests
- [ ] LLM Router correctly routes an air-gapped client task to the on-prem endpoint
- [ ] No cloud API calls made during an air-gapped routing test (verified via network logs)

---

#### Task M10.3: Stricter QA for On-Prem Outputs

**Owner:** AI/ML Engineer + QA/Compliance Lead
**Rationale:** Open-source LLMs have higher hallucination rates than frontier cloud models. All on-prem outputs require stricter validation.
**Steps:**
1. Implement on-prem QA profile: Class B minimum for ALL outputs (not just domain-specific)
2. Add additional hallucination detection step: cross-check all regulatory citations against KB
3. Flag outputs with confidence < 0.75 for human review regardless of output class

**Acceptance Criteria:**
- [ ] On-prem output QA profile applied correctly in 5 test cases
- [ ] Citation hallucination correctly detected in a deliberately flawed test output

---

#### Task M10.4: Tier-1 Pilot Deployment

**Owner:** Domain Expert (Healthcare or Legal) + Founding Engineer
**Goal:** Deploy air-gapped stack with one Tier-1 client.
**Steps:**
1. Identify pilot client (target: large private hospital or legal firm with DPDP-driven data sovereignty requirements)
2. Execute deployment runbook
3. Run 2-week parallel operation: compare on-prem vs cloud outputs for quality parity
4. Collect client feedback; document gaps for improvement sprint

**Acceptance Criteria:**
- [ ] Air-gapped deployment operational at pilot client site
- [ ] On-prem quality scores within 10% of cloud model scores on matched engagements
- [ ] Zero external API calls confirmed during 2-week parallel period

---

### Month 11–12: Government Tender Bidding Agent

#### Task M11.1: GEM Portal & eProcure Monitoring

**Owner:** AI/ML Engineer + Backend Engineer
**Steps:**
1. Set up Upstash QStash cron (daily 09:00 IST) to scrape:
   - `gem.gov.in` — AI/consulting category tenders
   - `eprocure.gov.in` — healthcare IT, logistics, education tenders
   - State government procurement portals (Manipur, Mizoram, Meghalaya as priority states given regional context)
2. Parse tender listings: extract `{tender_id, title, issuing_authority, deadline, bid_value, eligibility_criteria, document_url}`
3. Store all listings in Supabase `tender_listings` table
4. Filter pipeline: discard tenders where value < ₹5 lakh or deadline < 5 days

**Acceptance Criteria:**
- [ ] Scraper runs daily and populates `tender_listings` with ≥ 10 new listings per week
- [ ] Eligibility filter correctly removes tenders below threshold

---

#### Task M11.2: Government Tender Bidding Agent

**Owner:** AI/ML Engineer
**Location:** `/agents/gov-tender-bidding/`
**Steps:**
1. Implement RFP parser: extract requirements sections from tender PDF documents
2. Implement eligibility checker: cross-reference RFP eligibility criteria against agency profile (turnover, past experience from `ip_registry`, registrations)
3. Implement IP Registry mapping: for eligible tenders, map RFP requirements to existing IP assets
4. Implement bid package compiler (coordinates with Finance Agent and Vertical Manager):
   - Technical Bid: generated by relevant Vertical Manager based on RFP scope
   - Financial Bid: generated by Finance Agent (with government payment cycle buffer of 30%)
   - Compliance checklist: auto-populated from eligibility criteria
5. Implement **Gate G2**: all generated bid packages published to `oversight.approval_queue` — mandatory human review before submission

**KPI Tracking:**
- Tenders screened per week: target ≥ 20
- Bid package generation time: target ≤ 48 hours from tender detection
- Tender win rate: target ≥ 15%

**Acceptance Criteria:**
- [ ] Tender Bidding Agent correctly parses 5 test RFP PDFs
- [ ] Eligibility checker correctly rejects 2 ineligible tenders in test set
- [ ] Complete bid package (Technical + Financial) generated for 1 test tender within 48 hours
- [ ] Gate G2 fires and holds submission pending human approval

---

### Month 12–14: Affiliate Marketing Network & Scale

#### Task M12.1: Affiliate Network Launch

**Owner:** Marketing/BD + Marketing Agent
**Steps:**
1. Identify and onboard ≥ 3 affiliate partners (target: EdTech SaaS tools, compliance automation vendors, HR tech platforms)
2. Configure affiliate tiers in `affiliate_partners` table (Bronze/Silver/Gold with corresponding commission rates)
3. Assign referral codes; integrate referral tracking into client onboarding flow
4. Marketing Agent auto-generates promotional assets for each partner (banners, email copy, case study excerpts)

**Acceptance Criteria:**
- [ ] ≥ 3 affiliate partners onboarded and active
- [ ] Referral tracking correctly attributes a test client to a partner
- [ ] Commission computed correctly for a test referral engagement

---

#### Task M12.2: Finance Agent — Affiliate Payout Automation

**Owner:** Backend Engineer
**Steps:**
1. Implement automated monthly payout trigger: computes commissions owed per partner from `affiliate_referrals`
2. Generate payout summary report for human approval
3. After human approval, trigger payout via Razorpay Payouts API

**Acceptance Criteria:**
- [ ] Monthly payout report generated accurately for 3 test partners
- [ ] Human approval gate implemented before any payout API call

---

### Phase 5 Exit Criteria

- [ ] First air-gapped client deployment live and operational for ≥ 2 weeks
- [ ] Government Tender Bidding Agent screening ≥ 20 tenders/week
- [ ] First government tender bid submitted (with Gate G2 human approval)
- [ ] Affiliate network live with ≥ 3 partners
- [ ] Affiliate revenue tracking and payout automation live
- [ ] Human oversight ratio declining toward < 20% target

---

## 14. Agent Build Priority Registry

All 43 agents ordered by implementation priority. Agents 40–43 are internal subsystem controllers under Layer 2.

| Priority | # | Agent Name | Phase | Layer | Key Dependency |
|----------|---|-----------|-------|-------|----------------|
| 1 | 1 | CEO Orchestrator | 0 | L0 | Redpanda live |
| 2 | 9 | Memory & Knowledge Agent | 0 | L2 | Upstash Vector live |
| 3 | 10 | Quality & Compliance Agent | 0–1 | L2 | Memory & Knowledge Agent |
| 4 | 2 | Sales Agent | 1 | L1 | IP Registry schema; CEO Orchestrator |
| 5 | 4 | Finance Agent | 1 | L1 | Pricing microservice; Sales Agent |
| 6 | 12 | Vertical Manager (Healthcare) | 1 | L3 | Upstash Workflow; Finance Agent |
| 7 | 14 | Regulatory Compliance Agent (HC) | 1 | L4 | Healthcare KB seeded; QA Class B |
| 8 | 15 | EHR Integration Agent | 1 | L4 | Healthcare KB seeded |
| 9 | 5 | Ops / HR Agent + CHS | 2 | L1 | Supabase client activity tables |
| 10 | 6 | Account Growth Agent | 2 | L1 | CHS engine; Redpanda `client.health.alert` |
| 11 | 19 | Vertical Manager (Logistics) | 2 | L3 | Logistics KB seeded |
| 12 | 20 | Supply Chain Agent | 2 | L4 | Logistics KB; Vertical Manager |
| 13 | 21 | Inventory Agent | 2 | L4 | Logistics KB; Vertical Manager |
| 14 | 22 | Route Optimizer Agent | 2 | L4 | Logistics KB |
| 15 | 23 | Demand Forecaster Agent | 2 | L4 | Demand Forecaster microservice |
| 16 | 24 | ERP Integration Agent | 2 | L4 | SAP/Oracle API docs in KB |
| 17 | 25 | Trade Compliance Agent | 2 | L4 | Logistics KB (DGFT, ITC-HS) |
| 18 | 13 | Clinical AI Agent (+ Bioinformatics) | 2 | L4 | Healthcare KB; Class C QA gate |
| 19 | 16 | Health Analytics Agent | 2 | L4 | Healthcare KB |
| 20 | 17 | Pharma Supply Agent | 2 | L4 | Healthcare KB |
| 21 | 18 | Patient Engagement Agent | 2 | L4 | Healthcare KB |
| 22 | 26 | Vertical Manager (Legal) | 3 | L3 | Legal KB seeded |
| 23 | 27 | Contract Analysis Agent | 3 | L4 | Legal KB |
| 24 | 28 | Regulatory Watch Agent | 3 | L4 | KB supersession event pipeline live |
| 25 | 29 | Legal Research Agent | 3 | L4 | SCC Online / Manupatra API access |
| 26 | 30 | Risk Assessment Agent | 3 | L4 | Legal KB (DPDP Act) |
| 27 | 31 | Policy Drafting Agent | 3 | L4 | Legal KB |
| 28 | 32 | Litigation Support Agent | 3 | L4 | Legal KB |
| 29 | 33 | Vertical Manager (EdTech) | 3 | L3 | EdTech KB seeded |
| 30 | 34 | Curriculum Design Agent (Dynamic) | 3 | L4 | Real-Time Current Affairs Pipeline |
| 31 | 35 | Assessment Agent | 3 | L4 | EdTech KB; IRT microservice |
| 32 | 36 | Adaptive Tutor Agent | 3 | L4 | EdTech KB; Flutter app backend |
| 33 | 37 | Exam Strategist Agent | 3 | L4 | EdTech KB |
| 34 | 38 | Performance Analytics Agent | 3 | L4 | Anonymisation Pipeline (43) |
| 35 | 39 | LMS Integration Agent | 3 | L4 | EdTech KB |
| 36 | 11 | Self-Improvement Engine | 3 | L2 | Episodic logs populated; A/B framework |
| 37 | 40 | IP Registry Engine | 3–4 | L2 sub | Self-Improvement Engine |
| 38 | 7 | Market Intelligence Agent | 4 | L1 | Scraping infrastructure |
| 39 | 3 | Marketing Agent (+ Affiliate) | 4 | L1 | IP Registry Engine; Market Intelligence |
| 40 | 41 | KB Validity Engine | 4 | L2 sub | KB Validity Decay algorithm implemented |
| 41 | 42 | Pricing Model Microservice | 1/4 | L2 sub | Built Phase 1; upgraded Phase 4 |
| 42 | 43 | Anonymisation Pipeline | 4 | L2 sub | DPDP compliance review |
| 43 | 8 | Gov. Tender Bidding Agent | 5 | L1 | GEM/eProcure monitoring; Gate G2 |

---

## 15. Infrastructure Deployment Plan

### Deployment Environments

| Environment | Purpose | Promotion Criteria |
|-------------|---------|-------------------|
| **Local Dev** | Individual agent development | Unit tests pass; no hardcoded secrets |
| **Staging** | Integration testing, E2E flows | Integration tests pass; Class A QA review complete; peer code review approved |
| **Production** | Live client-facing operations | Human Oversight sign-off; load tested; security reviewed |

### Redpanda (Kafka-Compatible) Topic Architecture

| Topic | Partitions | Publisher | Consumer(s) | Retention |
|-------|-----------|-----------|-------------|-----------|
| `task.assigned` | 6 | CEO Orchestrator | All Vertical Managers, Layer 1 Agents | 7 days |
| `deliverable.ready` | 6 | All vertical agents | Quality & Compliance Agent | 7 days |
| `client.health.alert` | 3 | Ops/HR Agent | Account Growth Agent | 30 days |
| `regulatory.update.healthcare` | 3 | Regulatory Watch Agent (HC) | Memory & Knowledge Agent | 90 days |
| `regulatory.update.logistics` | 3 | Regulatory Watch Agent (Log.) | Memory & Knowledge Agent | 90 days |
| `regulatory.update.legal` | 3 | Regulatory Watch Agent (Legal) | Memory & Knowledge Agent | 90 days |
| `regulatory.update.edtech` | 3 | Curriculum Design Agent pipeline | Memory & Knowledge Agent | 90 days |
| `mas.health.report` | 1 | CEO Orchestrator | Oversight Console, Human Officers | 365 days |
| `oversight.approval_queue` | 3 | Various (Sales, Finance, Clinical AI, Legal VM, Tender Agent) | Human Oversight Console | 365 days |
| `market.intel` | 3 | Market Intelligence Agent | CEO Orchestrator, Marketing Agent, Sales Agent | 30 days |

### Supabase Schema Priorities (Full Schedule)

| Table(s) | Phase |
|----------|-------|
| `agents`, `tasks`, `clients`, `agent_configs` | Phase 0 |
| `kb_documents`, `ip_registry`, `episodic_logs` | Phase 0 |
| `pricing_records`, `oversight_approvals` | Phase 1 |
| `client_health_scores` | Phase 2 |
| `cohort_intelligence`, `current_affairs_index` | Phase 3 |
| `health_reports`, `market_intel_digests` | Phase 4 |
| `affiliate_partners`, `affiliate_referrals` | Phase 4 |
| `tender_listings`, `tender_bids`, `tender_results` | Phase 5 |

### Security Architecture

- **Supabase RLS:** Active from Phase 0 on all tables. All client data isolated by `client_id`.
- **Redpanda ACLs:** Topic-level access control — agents only have produce/consume rights to their designated topics.
- **API Key Rotation:** Every 90 days; managed via secret manager with automated reminders.
- **Air-Gapped Deployments (Phase 5):** Zero external API calls. Validated via network egress monitoring.
- **PII Stripping (Agent 43):** Active before any data crosses client or vertical boundaries.
- **DPDP Compliance:** Anonymisation Pipeline reviewed by QA/Compliance Lead before production activation.

---

## 16. Knowledge Base (KB) Setup Plan

KB seeding must precede vertical agent activation by at least 1 sprint (i.e., complete KB seeding in the sprint before the vertical's first agent goes to staging).

### KB Seeding Schedule

| Vertical | Documents to Seed | Decay Rate | Target Seed Date |
|----------|------------------|------------|--------------------|
| **Healthcare** | ABDM/ABHA/HIP/HIU standards (v2), NMC Act 2020, NABH 4th Ed., NQAS standards, DPDP Act 2023, ICMR guidelines, HL7 FHIR R4 | Fast (180d) for regulatory / Medium (365d) for standards | Week 3 (Phase 0) |
| **Logistics** | DGFT Foreign Trade Policy, Customs Tariff Act (ITC-HS), GST e-way bill rules, Warehousing Act, SAP S/4HANA Supply Chain API docs, Oracle SCM API, IATA regulations | Medium (365d) | Week 10 (Phase 2) |
| **Legal** | BNS 2023, Companies Act 2013 (consolidated), SEBI LODR, RBI Master Directions, DPDP Act 2023, SEBI circular index | Fast (180d) for all | Week 14 (Phase 3) |
| **EdTech (Static)** | UPSC syllabus (GS I–IV, Optionals), NEET/JEE syllabi, NCERT textbooks 6–12, past 10yr question papers | Slow (720d) | Week 17 (Phase 3) |
| **EdTech (Real-time)** | Daily news (The Hindu RSS, PIB), Economic Survey, SC judgment summaries, RBI MPC minutes | Real-time pipeline | Week 18 (Phase 3) |

### KB Validity Decay Constants

| Decay Category | λ (per day) | Half-life | Domain Examples | Confidence Threshold |
|----------------|-------------|----------|----------------|----------------------|
| **Fast** | 0.00385 | 180 days | ABDM, NMC Act, DPDP Act, SEBI circulars, RBI Directions | < 0.7 → cap output confidence |
| **Medium** | 0.00190 | 365 days | NABH 4th Ed., NQAS, GST rules, Companies Act | < 0.7 → cap output confidence |
| **Slow** | 0.000963 | 720 days | NCERT, FHIR R4 spec, UPSC static syllabus | < 0.7 → cap output confidence |
| **Real-time** | N/A (live pipeline) | Always fresh | Current affairs, daily news, SC judgments | Always fresh |

### KB Supersession Protocol (Full Flow)

1. **Regulatory Watch Agent** detects new regulation or amendment on SEBI/RBI/MCA portals
2. Publishes `{vertical, new_doc_url, supersedes_doc_id}` to `regulatory.update.{vertical}` Redpanda topic
3. **Memory & Knowledge Agent** consumes the event:
   - Sets `superseded_doc_id.confidence_score = 0.0` in both Supabase and Upstash Vector — immediately
   - Triggers ingestion of `new_doc_url`
   - Sets ephemeral Redis flag: `kb:supersession:{vertical}:{doc_id}` (TTL: 7 days) for agent awareness
4. All agents consuming KB perform domain pre-validation check:
   - If any retrieved document has `confidence_score < 0.7`, applies output confidence cap warning
5. KB Health section of weekly MAS Health Report surfaces all supersession events from the past week

---

## 17. Human Oversight Implementation

### Mandatory Approval Gates

All 6 gates must be wired, tested, and confirmed operational before the relevant agent is promoted to production.

| Gate | # | Trigger Condition | Agent | Human Action | Implementation Status |
|------|---|------------------|-------|-------------|----------------------|
| G1 | 1 | Contract value > ₹10,00,000 | Sales Agent / Finance Agent | Review and sign off before proposal sent | Phase 1 |
| G2 | 2 | Government/public sector tender submission | Gov. Tender Bidding Agent | Review full bid package; approve or reject with notes | Phase 5 |
| G3 | 3 | Healthcare clinical recommendation (Class C output) | Clinical AI / Regulatory Compliance Agent | Domain expert review and sign-off | Phase 2 |
| G4 | 4 | Legal opinion-class output (Class C output) | Legal Vertical Manager | Legal domain expert review and sign-off | Phase 3 |
| G5 | 5 | Dynamic pricing output > 2.5× base rate | Finance Agent | Human pricing approval before proposal delivery | Phase 1 |
| G6 | 6 | Core agent behaviour / prompt version change | Self-Improvement Engine | Founder / Engineering review before promotion to production | Phase 3 |

### Oversight Console Features (by Phase)

| Feature | Phase |
|---------|-------|
| Read-only agent status board and task log | Phase 0 |
| Approval queue (G1, G5 gates) | Phase 1 |
| Agent performance dashboard | Phase 2 |
| CHS alerts and client risk view | Phase 2 |
| Class C clinical/legal review interface (G3, G4) | Phase 2–3 |
| KB decay and supersession alerts | Phase 3 |
| Weekly MAS Health Report view | Phase 4 |
| Tender bid review and approval (G2) | Phase 5 |

### Weekly MAS Health Report Structure

Auto-generated by CEO Orchestrator every Monday 08:00 IST. Contains:

1. **Revenue Snapshot** — pipeline value, closed revenue, MRR, MoM growth
2. **Agent Performance** — quality scores by agent, escalation rate, SLA adherence per vertical
3. **Client Health** — CHS distribution, CHS < 65 alerts with client names, churn risk rating
4. **KB Health** — documents approaching decay threshold (< 0.75), supersession events this week
5. **Market Intelligence** — competitor moves, regulatory pipeline highlights, VC funding signals
6. **Affiliate Performance** — partner activity, referrals generated, commissions owing
7. **Tender Pipeline** — tenders screened this week, bids submitted, win/loss tracker

---

## 18. Observability & Monitoring Plan

### Instrumentation Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Tracing | OpenTelemetry SDK (Python + TypeScript) | Distributed traces across all agent calls |
| Log aggregation | Axiom (recommended) or Grafana Loki | Structured log search and alerting |
| Metrics | Prometheus + Grafana (or Axiom dashboards) | Time-series metrics for SLA monitoring |
| Error tracking | Sentry | Exception capture and aggregation |
| Uptime monitoring | UptimeRobot or Grafana Synthetic Monitoring | Endpoint health checks for all portals |

### Standard Span Attributes (All Agent Calls)

Every agent invocation must emit an OpenTelemetry span with:

```
agent.name          (e.g., "regulatory-compliance-healthcare")
agent.layer         (0–4)
task.id             (UUID from tasks table)
llm.provider        (anthropic|openai|google|on_prem)
llm.model           (e.g., "claude-opus-4-6")
token.input         (count)
token.output        (count)
token.cost_usd      (computed)
kb.confidence_min   (lowest confidence score of any KB doc cited)
qa.class            (A|B|C)
qa.score            (0–100 or null if not yet QA'd)
oversight.gate      (gate number if triggered, else null)
```

### Key Dashboards

1. **Agent Health Dashboard:** Per-agent error rate, latency, quality score (7-day rolling)
2. **LLM Cost Dashboard:** Token spend by provider, by agent, by vertical (daily/weekly/monthly)
3. **KB Health Dashboard:** Distribution of document confidence scores; documents below 0.7
4. **Business KPI Dashboard:** Active clients, revenue pipeline, CHS distribution
5. **Infrastructure Status Board:** Redpanda topic lag, Upstash latencies, Supabase DB load

### Alert Rules

| Alert | Threshold | Channel | Severity |
|-------|-----------|---------|----------|
| Agent error rate | > 5% (5-min window) | Slack #alerts | High |
| LLM API cost overage | > 20% of per-task budget | Slack #cost-alerts | Medium |
| KB document confidence | Any document < 0.6 | Oversight Console + Slack | Medium |
| Redpanda consumer lag | > 1000 messages on any topic | Slack #infra | High |
| Supabase connection pool | > 80% utilisation | Slack #infra | High |
| Oversight gate unacknowledged | > 4 hours | Email + Slack | Critical |

---

## 19. Testing Strategy

### Testing Pyramid (per Agent)

1. **Unit Tests** (fastest, most numerous):
   - Prompt output parsing logic
   - KB search and confidence filtering
   - Pricing formula correctness
   - QA tier classification logic

2. **Integration Tests** (per vertical):
   - Agent correctly publishes to / consumes from Redpanda topics
   - Upstash Workflow DAG completes a 3-agent pipeline end-to-end
   - KB supersession event propagates correctly

3. **E2E Simulation Tests** (per phase):
   - Full engagement flow: lead → proposal → pricing → delivery → QA → oversight (where applicable)
   - Run against staging environment with real (but test-mode) LLM API calls

4. **Load Tests** (Phase 4):
   - 40 concurrent engagements as described in Task M8.2
   - Topic throughput, Workflow DAG completion rate, latency percentiles

### Test Data Management

- All test clients, test documents, and test engagements are tagged `env: staging` in Supabase
- Staging DB is seeded from a canonical fixture dataset (committed to `/infra/fixtures/`)
- Production DB never uses test data

### QA Test Matrix (per Agent Promotion)

Before any agent is promoted to production, the following must pass:

| Test | Passing Criterion |
|------|------------------|
| Unit tests | 100% pass |
| Integration tests | 100% pass |
| E2E simulation (1 engagement) | Completes without errors; quality score ≥ 70/100 |
| Oversight gates | All relevant gates trigger correctly |
| KB confidence filter | Correctly filters decayed documents |
| Disclaimer injection | All required disclaimers present in outputs |
| Episodic logging | Complete log written for all task steps |

---

## 20. KPI Tracking & Milestones

### Business KPIs

| KPI | Month 3 | Month 6 | Month 12 | Month 24 |
|-----|---------|---------|---------|---------|
| Active clients | 3 | 15 | 40 | 75 |
| Autonomous engagement closure | 30% | 50% | 60% | 85% |
| Retainer conversion rate | 10% | 20% | 35% | 35%+ |
| Expansion revenue (% of total) | — | 10% | 20% | 30% |
| Affiliate revenue (% of MRR) | — | — | 5% | 15% |
| Gov. tender contracts secured | — | — | 3 | 10 |

### Agent Performance KPIs

| KPI | Target |
|-----|--------|
| Average quality score | ≥ 82/100 |
| Escalation rate | ≤ 15% (Y1) → ≤ 10% (Y2) |
| Human oversight ratio | < 20% (Y1) → < 10% (Y2) |
| QA turnaround — Class A | < 2 minutes |
| QA turnaround — Class B | < 15 minutes |
| Tender bid generation time | ≤ 48 hours |
| Tenders screened per week | ≥ 20 |
| Tender win rate | ≥ 15% |

### Knowledge & IP KPIs

| KPI | Target |
|-----|--------|
| IP Registry assets | ≥ 10 by M3; ≥ 30 by M12 |
| IP reuse rate | ≥ 25% (Y1) → ≥ 40% (Y2) |
| Delivery time reduction from IP reuse | ≥ 35% |
| KB documents with valid confidence (≥ 0.7) | ≥ 95% at all times |
| Self-improvement quality score gain | +15%/quarter (Y1) → +20%/quarter (Y2) |

### Master Milestone Checklist

| Milestone | Target Date |
|-----------|------------|
| All infrastructure live and verified | End of Week 4 |
| Observability dashboard active | End of Week 2 |
| First client proposal generated autonomously | End of Week 6 |
| First paying engagement delivered | End of Week 8 |
| Logistics vertical live | End of Week 13 |
| All 4 verticals delivering simultaneously | End of Month 6 |
| B2C Aspirant App publicly launched | Month 8 |
| Full 43-agent system operational | Month 9 |
| Load test passed (40 concurrent engagements) | Month 9 |
| Security audit complete | Month 9 |
| First Tier-1 air-gapped deployment | Month 11 |
| Government Tender Bidding Agent live | Month 11 |
| First government tender bid submitted | Month 12 |
| Affiliate network live with ≥ 3 partners | Month 12 |
| 75 active clients | Month 24 |

---

## 21. Risk Register & Mitigation Actions

| # | Risk | Severity | Likelihood | Phase | Mitigation | Owner |
|---|------|----------|-----------|-------|-----------|-------|
| R1 | Hallucinated regulatory information | Critical | Medium | All | KB validity decay caps output confidence; Tiered QA mandatory; Domain Pre-validation before QA handoff | QA/Compliance Lead |
| R2 | Open-source LLM hallucinations (air-gapped) | High | Medium | Phase 5 | Stricter QA profile for on-prem outputs (Class B minimum for ALL outputs); citation cross-check step; enhanced hallucination detection | AI/ML Engineer |
| R3 | Tender compliance failure | Critical | Medium | Phase 5 | Mandatory Gate G2 human review of ALL bid packages before portal submission; compliance checklist generated and reviewed | Human Oversight Officer |
| R4 | Legal liability / patient safety breach | Critical | Low | Phase 1+ | No individual patient diagnosis (guardrail); mandatory disclaimers on ALL clinical and legal outputs; Gate G3/G4 human review for Class C; legal indemnity clause in client contracts | Domain Experts |
| R5 | Current affairs pipeline noise (EdTech) | Medium | High | Phase 3+ | Multi-source verification; editorial/opinion filtering NLP classifier; Domain Expert — EdTech reviews pipeline calibration weekly | AI/ML Engineer |
| R6 | Runaway API costs | High | Medium | All | Per-task token budget enforced by LLM Router; automatic throttling at 20% overage; daily cost dashboard reviewed by Founding Engineer | Founding Engineer |
| R7 | Data breach / DPDP non-compliance | High | Low | Phase 1+ | Supabase RLS active from Day 1; Agent 43 PII stripping; air-gapped deployments for sensitive clients; 90-day key rotation; OWASP audit Phase 4 | QA/Compliance Lead |
| R8 | KB document staleness undetected | Medium | Medium | Phase 3+ | KB Validity Engine runs daily; weekly KB health report surfaces decayed docs; Regulatory Watch Agent auto-publishes supersession events | AI/ML Engineer |
| R9 | Agent coordination failure / DAG deadlock | Medium | Low | Phase 2+ | Upstash Workflow QStash timeout policies per DAG node; circuit breakers; CEO Orchestrator monitors DAG completion SLAs; dead-letter queue for failed tasks | Founding Engineer |
| R10 | Affiliate partner brand/ethics violations | Low | Medium | Phase 4+ | Marketing Agent monitors affiliate content compliance; brand guidelines enforced via automated content review before asset delivery | Marketing Agent / Human |
| R11 | Message bus vendor risk | Medium | Low | All | **Primary broker (Redpanda Cloud Serverless) is independent and Kafka-compatible.** All agents use standard Kafka protocol clients — migration to self-hosted Kafka or MSK requires zero code changes. Maintain IaC for self-hosted fallback. | Founding Engineer |
| R12 | LLM provider outage / rate limits | Medium | Medium | All | LLM Router fallback chain (Claude → GPT → Gemini); per-task budget caps prevent runaway retries; ephemeral Redis queue buffers tasks during brief outages | AI/ML Engineer |

---

## 22. Master Timeline Gantt Summary

```
WEEK/MONTH     W1   W2   W3   W4  |  W5   W6   W7   W8  |  W9  W10  W11  W12  W13  W14
               ─────────────────────────────────────────────────────────────────────────
INFRASTRUCTURE ████ ████ ████ ████ │                      │
OBSERVABILITY  ████ ████           │                      │
CORE AGENTS              ████ ████ │                      │
KB SEEDING (HC)          ████ ████ │                      │
SALES AGENT                        │ ████ ████            │
FINANCE AGENT                      │ ████ ████            │
HC VERTICAL v1                     │      ████ ████       │
QA CLASS B/C                       │           ████       │
E2E SIM TEST                       │                ████  │
OPS/CHS AGENT                      │                      │ ████ ████
ACCOUNT GROWTH                     │                      │      ████
KB SEED (LOG)                      │                      │           ████ ████
LOGISTICS V7                       │                      │           ████ ████ ████
HC EXPANSION                       │                      │                ████ ████

MONTH          M4   M5   M6   M7  |  M8   M9  | M10  M11  M12  M13  M14+
               ─────────────────────────────────────────────────────────────
LEGAL VERTICAL ████ ████           │           │
EDTECH VERTICAL     ████ ████      │           │
CURR AFFAIRS PIPE   ████ ████      │           │
KB VALIDITY DECAY   ████ ████      │           │
SELF-IMPROVE ENGINE      ████      │           │
MARKET INTEL AGENT            ████ │           │
MARKETING AGENT               ████ ████        │
DYNAMIC PRICING v2            ████ ████        │
MAS HEALTH REPORT             ████ ████        │
LOAD + SEC AUDIT               │   ████        │
B2C APP PUBLIC LAUNCH          │   ████        │
ALL 43 AGENTS LIVE             │   ████        │
AIR-GAPPED LLM                 │           │ ████ ████
GOV TENDER AGENT               │           │      ████ ████
AFFILIATE NETWORK              │           │           ████ ████
INSTITUTIONAL SCALE            │           │                ████ ████
```

---

## Appendix: Tech Stack Quick Reference (Verified June 2026)

| Service | Status | Role in MAS |
|---------|--------|-------------|
| **Redpanda Cloud Serverless** | ✅ Active — primary recommendation | Kafka-compatible message bus (replaces Upstash Kafka) |
| ~~Upstash Kafka~~ | ❌ DISCONTINUED March 11, 2025 | Do not use |
| **Confluent Cloud (now IBM Confluent)** | ⚠️ Operational; IBM-owned since March 17, 2026 | Alternative message bus option; evaluate lock-in |
| **Amazon MSK Serverless** | ✅ Active | Alternative message bus option (AWS-native) |
| **Upstash Workflow (QStash)** | ✅ GA — confirmed active | DAG orchestration for multi-agent pipelines |
| **Upstash Vector** | ✅ Confirmed active | Semantic KB with validity metadata |
| **Upstash Redis** | ✅ Confirmed active | Ephemeral state, caching, rate limiting |
| **Context7 MCP** | ✅ Active (#1 MCP in 2026, 54.1K GitHub stars; security patch applied Feb 2026) | Live library docs for agent development |
| **Supabase** | ✅ Active | Relational DB, RLS, Realtime subscriptions |
| **Llama 4 Scout / Maverick** | ✅ Current — Meta Community License | On-premise LLM for air-gapped deployments (replaces Llama 3) |
| **Mistral Small 4** | ✅ Current — Apache 2.0 | On-premise LLM for air-gapped deployments (replaces Mixtral as primary) |
| **vLLM** | ✅ Active | Production on-premise LLM serving |

---

*End of Document — MAS v4.0 Implementation Plan*
*Next review date: Before Phase 1 kickoff, or on any PRD update*
