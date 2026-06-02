# AI Consultancy Agency — Multi-Agent System (MAS) v3.0

> **Status:** Phase 3 — Legal Vertical (Sprint 3.1 Complete)
> **Classification:** Internal — Confidential
> **Version:** 3.0.0

## Overview

An autonomous AI consultancy operated by a **24-agent Multi-Agent System** (MVP scope, scaling to 43) across 3 active industry verticals and shared business operations. The system is designed to deliver consulting-grade deliverables autonomously — from contract review to NABH gap analysis to logistics demand forecasting — with human oversight gates at critical decision points.

**Active Verticals:**
- **Healthcare** — CDSS architecture, ABDM/NQAS/NABH compliance, EHR integration, clinical analytics
- **Logistics & Supply Chain** — Demand forecasting, route optimisation, ERP integration, trade compliance
- **Legal & Compliance** — Contract review, regulatory watch (SEBI/RBI/MCA), compliance auditing, M&A due diligence, dispute resolution

**Planned Vertical:**
- **EdTech & Competitive Exams** — Adaptive learning, mock tests, B2C flywheel *(Phase 4)*

---

## Architecture

```
ai-healthcare-consultancy/
│
├── agents/                            # Layer 0 & 1 Agents
│   ├── ceo_orchestrator/              # Layer 0
│   ├── business_ops/                  # Layer 1 — Sales, Finance, Account Growth, HR
│   └── shared_services/               # Layer 2 — Quality & Compliance
│
├── shared_services/                   # Core shared libraries
│   ├── agent_framework/               # BaseAgent, AgentConfig, AgentContext, enums
│   ├── llm_router/                    # Multi-LLM fallback router
│   ├── memory/                        # 4-layer memory architecture
│   ├── messaging/                     # Kafka producer/consumer, typed schemas, topic registry
│   ├── ip_registry/                   # IP asset tracking and billing
│   ├── kb_validity/                   # KB confidence decay engine
│   └── observability.py               # OpenTelemetry observability
│
├── verticals/                         # Vertical-specific agents and workflows
│   ├── healthcare/                    # Layer 3+4 Healthcare agents
│   ├── logistics/                     # Layer 3+4 Logistics agents
│   ├── legal/                         # Layer 3+4 Legal agents
│   ├── edtech/                        # Layer 3+4 EdTech agents
│   └── workflows/                     # Upstash Workflow DAG definitions
│
├── infra/                             # Docker, Supabase migrations
├── knowledge_bases/                   # Domain-specific knowledge documents
├── tests/                             # Unit and integration tests
├── scripts/                           # Sprint validation scripts
├── docs/                              # PRD, architecture decision records
└── pyproject.toml
```

---

## Agent Inventory

### Layer 0 — CEO Orchestrator (1 agent)
| Agent | Tier | Reasoning |
|---|---|---|
| CEO Orchestrator | Tier 0 | Plan-and-Execute |

### Layer 1 — Business Operations (4 agents)
| Agent | Tier | Reasoning |
|---|---|---|
| Sales Agent | Tier 1 | Plan-and-Execute |
| Finance Agent | Tier 1 | Plan-and-Execute |
| Account Growth Agent | Tier 1 | Plan-and-Execute |
| HR / Ops Agent | Tier 1 | Plan-and-Execute |

### Layer 2 — Shared Services (1 agent)
| Agent | Tier | Reasoning |
|---|---|---|
| Quality & Compliance Agent | Tier 2 | Plan-and-Execute |

### Healthcare Vertical (4 agents)
| Agent | Tier | Reasoning |
|---|---|---|
| Healthcare Vertical Manager | Tier 1 | Plan-and-Execute |
| Clinical AI Agent | Tier 2 | Plan-and-Execute |
| EHR Integration Agent | Tier 2 | Plan-and-Execute |
| Regulatory Compliance Agent | Tier 2 | Plan-and-Execute |

### Logistics Vertical (7 agents)
| Agent | Tier | Reasoning |
|---|---|---|
| Logistics Vertical Manager | Tier 1 | Plan-and-Execute |
| Demand Forecaster Agent | Tier 2 | Plan-and-Execute |
| Route Optimizer Agent | Tier 2 | Plan-and-Execute |
| Inventory Agent | Tier 2 | Plan-and-Execute |
| Supply Chain Agent | Tier 2 | Plan-and-Execute |
| Trade Compliance Agent | Tier 2 | Plan-and-Execute |
| ERP Integration Agent | Tier 2 | Plan-and-Execute |

### Legal Vertical (7 agents)
| Agent | Tier | Reasoning |
|---|---|---|
| Legal Vertical Manager | Tier 3 | Plan-and-Execute |
| Contract Analysis Agent | Tier 2 | Plan-and-Execute |
| Legal Research Agent | Tier 2 | Plan-and-Execute |
| Policy Drafting Agent | Tier 2 | Plan-and-Execute |
| Litigation Support Agent | Tier 3 | ReAct |
| Risk Assessment Agent | Tier 3 | ReAct |
| Regulatory Watch Agent | Tier 4 | ReAct |

> **Total implemented: 24 agents** (43 planned at full scale)

---

## Implementation Progress

| Phase | Sprint | Status | Description |
|---|---|---|---|
| Phase 0 | — | ✅ Done | Core framework: BaseAgent, LLM router, 4-layer memory, Kafka messaging, IP registry, KB validity |
| Phase 1 | Sprint 1.1 | ✅ Done | CEO Orchestrator, Business Ops agents (Sales, Finance, Account Growth, HR) |
| Phase 1 | Sprint 1.2 | ✅ Done | Healthcare vertical (Vertical Manager, Clinical AI, EHR Integration, Regulatory Compliance) + Upstash Workflow DAG |
| Phase 2 | Sprint 2.1 | ✅ Done | Client Retention cron workflow, CHS scoring, escalation engine |
| Phase 2 | Sprint 2.2 | ✅ Done | Logistics vertical (7 agents) + Upstash Workflow integration |
| Phase 2 | Sprint 2.3 | ✅ Done | Client portal foundations, Supabase integration |
| Phase 3 | Sprint 3.1 | ✅ Done | Legal vertical (7 agents), KB Supersession pipeline, Regulatory Scraper (mocked MVP), Mandatory legal disclaimer enforcement |
| Phase 3 | Sprint 3.2 | 🔲 Next | Legal Upstash Workflow DAG (`legal_project.py`) |
| Phase 4 | — | 🔲 Planned | EdTech vertical, Finance vertical, full Kafka broker, production hardening |

---

## Getting Started

### Prerequisites

- Python 3.12+
- `.env` file with credentials (see `.env.example`)

```env
# LLM Providers
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
GOOGLE_GENERATIVE_AI_API_KEY=...

# Upstash
UPSTASH_VECTOR_REST_URL=...
UPSTASH_VECTOR_REST_TOKEN=...
UPSTASH_REDIS_REST_URL=...
UPSTASH_REDIS_REST_TOKEN=...
UPSTASH_WORKFLOW_URL=...

# Supabase
SUPABASE_URL=...
SUPABASE_KEY=...
```

### Installation

```bash
# Install all dependencies (including dev tools)
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all unit tests
pytest

# Run with coverage
pytest --cov=packages --cov-report=term-missing

# Type checking (strict mode)
python -m mypy packages scripts

# Linting
ruff check packages scripts
```

### Validation Scripts

Each sprint has a dedicated E2E validation script:

```bash
# Phase 1 — Business Ops
python -m scripts.test_sprint1_1_business_ops

# Phase 1 — Healthcare DAG
python -m scripts.test_sprint1_2_healthcare_dag

# Phase 2 — Client Retention
python -m scripts.test_sprint2_1_retention

# Phase 2 — Full E2E
python -m scripts.test_phase2_e2e

# Upstash connectivity
python -m scripts.test_upstash_connections

# Phase 3 — Legal Regulatory Scraper Pipeline
python -m scripts.test_sprint3_1_scraper_pipeline
```

---

## Core Guardrails

Every agent in the system is subject to the following mandatory guardrails enforced at the `BaseAgent` level — **these cannot be bypassed by subclasses**:

| Guardrail | Mechanism |
|---|---|
| Token budget enforcement | Hard cap in `BaseAgent.run()` — escalates if exceeded |
| KB validity check | Agents query confidence scores before citing documents |
| PII detection | Configurable per-agent; blocks output containing PII |
| Blocked output patterns | Regex-filtered phrases (e.g. "I guarantee this complies") |
| Mandatory legal disclaimer | Injected in `BaseAgent.report()` for `Vertical.LEGAL` — **cannot be bypassed** |
| Audit trail | Every execution logged via `AuditLogMessage` to Kafka |
| IP registry tracking | All IP assets consumed in a task are recorded for billing |

---

## Documentation

- [Implementation Plan](docs/AI_Consultancy_MAS_PRD_v3.md) — Product Requirements Document v3.0
