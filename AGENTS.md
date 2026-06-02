# AGENTS.md — AI Consultancy MAS v3.0

> **Sources:** PRD v3.0 · README (Sprint 3.1 Complete) · skills-lock.json (v1)
> **Purpose:** Authoritative context file for all AI coding agents working in this repository.
> **Current build:** 24 agents implemented · Phase 3 Sprint 3.2 is next
> **Full-scale target:** 43 agents across 6 layers
> **Classification:** Internal — Confidential

---

## 1. What This System Is

An **Autonomous AI Consultancy Agency** operated by a Multi-Agent System (MAS). It delivers AI consulting, automation, and advisory services across four Indian industry verticals — **Healthcare**, **Logistics & Supply Chain**, **Legal & Compliance**, and **EdTech & Competitive Exams** — running end-to-end from lead acquisition and tender bidding through delivery, finance, and self-improvement.

**Active verticals (implemented):** Healthcare · Logistics · Legal
**Planned vertical:** EdTech & Competitive Exams *(Phase 4)*
**MVP agent count:** 24 implemented · 43 at full scale

---

## 2. Implementation Status

| Phase | Sprint | Status | Description |
|---|---|---|---|
| Phase 0 | — | ✅ Done | Core framework: BaseAgent, LLM router, 4-layer memory, Kafka messaging, IP registry, KB validity |
| Phase 1 | Sprint 1.1 | ✅ Done | CEO Orchestrator + Business Ops agents (Sales, Finance, Account Growth, HR) |
| Phase 1 | Sprint 1.2 | ✅ Done | Healthcare vertical + Upstash Workflow DAG |
| Phase 2 | Sprint 2.1 | ✅ Done | Client Retention cron, CHS scoring, escalation engine |
| Phase 2 | Sprint 2.2 | ✅ Done | Logistics vertical (7 agents) + Upstash Workflow integration |
| Phase 2 | Sprint 2.3 | ✅ Done | Client portal foundations, Supabase integration |
| Phase 3 | Sprint 3.1 | ✅ Done | Legal vertical (7 agents), KB Supersession pipeline, Regulatory Scraper (mocked MVP), mandatory legal disclaimer enforcement |
| **Phase 3** | **Sprint 3.2** | 🔲 **Next** | **Legal Upstash Workflow DAG (`legal_project.py`)** |
| Phase 4 | — | 🔲 Planned | EdTech vertical, Finance vertical, full Kafka broker, production hardening |
| Phase 5 | — | 🔲 Planned | Air-gapped LLM deployments, Gov. Tender Bidding Agent, Affiliate network |

---

## 3. Architecture Layers

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

## 6. Core Design Patterns

### 6.1 Reasoning Architecture by Tier

| Tier | Pattern | Notes |
|---|---|---|
| Tier 0–2 | **Plan-and-Execute** | Produce an explicit plan before executing any action |
| Tier 3 (most) | **Plan-and-Execute** | Vertical Managers coordinate via DAG |
| Tier 3 (Litigation Support, M&A DD) | **ReAct** | Iterative Reason → Act → Observe loops |
| Tier 4 (Regulatory Watch) | **ReAct** | Continuous monitoring with act-on-detect cycles |

> ⚠️ The PRD describes a simpler Tier 0–3 = Plan-and-Execute / Tier 4 = ReAct split. The README reflects the **actual implementation**: ReAct is used where iterative reasoning matters regardless of strict tier — Litigation Support, Risk Assessment, and Regulatory Watch all use ReAct.

### 6.2 IP Registry Check (Mandatory — All Tier 0–3 agents)

Before spawning any new engagement workflow:
1. Query `shared_services/ip_registry/` for reusable assets matching the client use case.
2. If `reusability_score >= 0.7` → load asset as base; skip bespoke generation.
3. If no match → generate bespoke, then submit result for IP candidacy scoring post-engagement.
4. All IP assets consumed in a task are recorded in the IP Registry for billing via `shared_services/ip_registry/`.

### 6.3 KB Validity Decay

Every document in the semantic memory (`shared_services/memory/semantic.py`) carries a `validity_metadata_envelope`:

```json
{
  "domain": "ABDM",
  "decay_rate": "fast",
  "validity_days": 180,
  "confidence_score": 0.95,
  "last_verified": "2026-01-15"
}
```

- Confidence decays **logarithmically** over time.
- Documents with `confidence_score < 0.7` **cap the agent's output confidence** — never produce high-confidence outputs citing decayed sources.
- **Supersession events** (published by Regulatory Watch Agent on `regulatory.update.{vertical}`) drop affected documents to `confidence_score = 0` immediately.
- Output `confidence_score` must be **floored at the minimum confidence** of all KB documents used.

### 6.4 Agent Execution Modes

- **Reactive** — Event-driven via Kafka message bus
- **Proactive** — Cron-scheduled (Regulatory Watch, CHS computation via `retention_cron.py`)
- **Collaborative** — DAG-based parallel workflows via Upstash Workflow (`workflow_engine/`)
- **Reflective** — Post-task self-evaluation feeding back into the Self-Improvement Engine
- **Flywheel** — B2C EdTech data loop *(Phase 4)*

---

## 7. Kafka Message Bus

Kafka runs in **stub mode** (no live broker) for the MVP. Full broker deployment is Phase 4. All inter-agent event contracts are defined now in `shared_services/messaging/`.

### Key Topics

```
task.assigned                    → New task dispatched to an agent
deliverable.ready                → Agent output ready for QA
deliverable.approved             → QA passed; cleared for client delivery
client.health.alert              → CHS dropped below 65 threshold
regulatory.update.healthcare     → New regulatory change (Healthcare KB)
regulatory.update.logistics      → New regulatory change (Logistics KB)
regulatory.update.legal          → New regulatory change (Legal KB); triggers KB supersession
regulatory.update.edtech         → New regulatory change (EdTech KB)
mas.health.report                → Weekly CEO Orchestrator intelligence digest
mas.oversight.approved           → Human approval granted for gated action
tender.screened                  → Gov. Tender Agent has qualified an opportunity (Phase 5)
tender.ready_for_approval        → Bid package complete; awaiting human sign-off (Phase 5)
affiliate.commission.due         → Affiliate payout trigger (Phase 5)
```

**Rule:** Agents MUST NOT call each other via HTTP/RPC. All coordination goes through Kafka topics. If you are writing inter-agent interaction code, it MUST use producers/consumers from `shared_services/messaging/`.

---

## 8. Memory Architecture

| Type | Module | Backend | Description |
|---|---|---|---|
| Working Memory | `core/memory/working.py` | Context window | Ephemeral; scoped to current task execution |
| Episodic Memory | `core/memory/episodic.py` | Supabase (PostgreSQL) | Structured logs of past tasks; powers Self-Improvement Engine |
| Semantic Memory | `core/memory/semantic.py` | Upstash Vector | Vector KB with validity metadata envelopes; hybrid dense + sparse |
| Procedural Memory | `core/memory/procedural.py` | Git-versioned | Versioned system prompts and workflow templates |

---

## 9. Quality & Compliance Pipeline (Tiered)

All client-facing deliverables route through the Quality & Compliance Agent (`agents/shared_services/`) before delivery. Every deliverable passed to QA **must include an explicit `qa_class` field** (`A`, `B`, or `C`). Do not default silently.

| Class | Trigger | Validation | SLA |
|---|---|---|---|
| **A** | Pattern-matched, low-risk content | Lightweight rule check | < 2 minutes |
| **B** | Standard consulting deliverables | Full LLM validation + domain rules | < 15 minutes |
| **C** | Healthcare clinical content · Legal opinion-class outputs | LLM validation + **mandatory human review gate** | Async — awaits `mas.oversight.approved` |

---

## 10. Human Oversight — Mandatory Approval Gates

The following operations **must not** be executed autonomously. The workflow MUST pause and await the `mas.oversight.approved` Kafka event before proceeding:

1. Contract signing > ₹10 lakh.
2. Government / public sector tender portal submissions *(Phase 5)*.
3. Healthcare clinical recommendations or clinical-class outputs (Class C QA).
4. Legal opinion-class outputs (Class C QA).
5. Dynamic pricing outputs > 2.5× base rate.

When generating gated outputs, the agent must:
- Set `approval_required: true` on the deliverable payload
- Publish to `deliverable.ready` and halt
- Await `mas.oversight.approved` before continuing
- Write a complete record to the audit log via `AuditLogMessage`

---

## 11. BaseAgent Guardrails (Cannot Be Bypassed by Subclasses)

These are enforced at the `BaseAgent` level in `shared_services/agent_framework/`:

| Guardrail | Mechanism |
|---|---|
| **Token budget enforcement** | Hard cap in `BaseAgent.run()` — escalates if exceeded |
| **KB validity check** | Agents query `confidence_score` before citing any KB document |
| **PII detection** | Configurable per-agent; blocks output containing detected PII |
| **Blocked output patterns** | Regex-filtered phrases (e.g. `"I guarantee this complies"`) |
| **Mandatory legal disclaimer** | Injected in `BaseAgent.report()` for `Vertical.LEGAL` — **cannot be bypassed by any Legal vertical subclass** |
| **Audit trail** | Every execution logged via `AuditLogMessage` to Kafka |
| **IP registry tracking** | All IP assets consumed in a task recorded for billing |

---

## 12. Agent Inventory (24 Implemented · 43 Full Scale)

### Layer 0 — CEO Orchestrator

| # | Agent | Tier | Reasoning | Status |
|---|---|---|---|---|
| 1 | CEO Orchestrator | Tier 0 | Plan-and-Execute | ✅ Active |

### Layer 1 — Business Operations

| # | Agent | Tier | Reasoning | Status |
|---|---|---|---|---|
| 2 | Sales Agent | Tier 1 | Plan-and-Execute | ✅ Active |
| 3 | Finance Agent | Tier 1 | Plan-and-Execute | ✅ Active |
| 4 | Account Growth Agent | Tier 1 | Plan-and-Execute | ✅ Active |
| 5 | HR / Ops Agent | Tier 1 | Plan-and-Execute | ✅ Active |
| — | Marketing Agent | Tier 1 | Plan-and-Execute | 🔲 PRD v3.0 — not yet implemented |
| — | Market Intelligence Agent | Tier 1 | Plan-and-Execute | 🔲 PRD v3.0 — not yet implemented |
| — | Gov. Tender Bidding Agent | Tier 1 | Plan-and-Execute | 🔲 Phase 5 |

### Layer 2 — Shared Services

| # | Agent | Tier | Reasoning | Status |
|---|---|---|---|---|
| 6 | Quality & Compliance Agent | Tier 2 | Plan-and-Execute | ✅ Active |
| — | Memory & Knowledge Agent | Tier 2 | — | 🔲 Implemented as `core/` library, not a standalone agent yet |
| — | Self-Improvement Engine | Tier 2 | — | 🔲 Planned |

### Healthcare Vertical (Layer 3+4)

| # | Agent | Tier | Reasoning | Status |
|---|---|---|---|---|
| 7 | Healthcare Vertical Manager | Tier 1 | Plan-and-Execute | ✅ Active |
| 8 | Clinical AI Agent | Tier 2 | Plan-and-Execute | ✅ Active |
| 9 | EHR Integration Agent | Tier 2 | Plan-and-Execute | ✅ Active |
| 10 | Regulatory Compliance Agent | Tier 2 | Plan-and-Execute | ✅ Active |
| — | Health Analytics Agent | Tier 4 | — | 🔲 PRD v3.0 — planned |
| — | Pharma Supply Agent | Tier 4 | — | 🔲 PRD v3.0 — planned |
| — | Patient Engagement Agent | Tier 4 | — | 🔲 PRD v3.0 — planned |

### Logistics Vertical (Layer 3+4)

| # | Agent | Tier | Reasoning | Status |
|---|---|---|---|---|
| 11 | Logistics Vertical Manager | Tier 1 | Plan-and-Execute | ✅ Active |
| 12 | Demand Forecaster Agent | Tier 2 | Plan-and-Execute | ✅ Active |
| 13 | Route Optimizer Agent | Tier 2 | Plan-and-Execute | ✅ Active |
| 14 | Inventory Agent | Tier 2 | Plan-and-Execute | ✅ Active |
| 15 | Supply Chain Agent | Tier 2 | Plan-and-Execute | ✅ Active |
| 16 | Trade Compliance Agent | Tier 2 | Plan-and-Execute | ✅ Active |
| 17 | ERP Integration Agent | Tier 2 | Plan-and-Execute | ✅ Active |

### Legal Vertical (Layer 3+4)

| # | Agent | Tier | Reasoning | Status |
|---|---|---|---|---|
| 18 | Legal Vertical Manager | Tier 3 | Plan-and-Execute | ✅ Active |
| 19 | Contract Analysis Agent | Tier 2 | Plan-and-Execute | ✅ Active |
| 20 | Legal Research Agent | Tier 2 | Plan-and-Execute | ✅ Active |
| 21 | Policy Drafting Agent | Tier 2 | Plan-and-Execute | ✅ Active |
| 22 | Litigation Support Agent | Tier 3 | **ReAct** | ✅ Active |
| 23 | Risk Assessment Agent | Tier 3 | **ReAct** | ✅ Active |
| 24 | Regulatory Watch Agent | Tier 4 | **ReAct** | ✅ Active |

### EdTech Vertical *(Phase 4 — Not Yet Implemented)*

| Agent | Reasoning | Notes |
|---|---|---|
| EdTech Vertical Manager | Plan-and-Execute | B2B + B2C tracks |
| Curriculum Design Agent | Plan-and-Execute | Dynamic current affairs pipeline (UPSC Polity/Economics/Ethics) |
| Assessment Agent | Plan-and-Execute | MCQ generation, IRT calibration |
| Adaptive Tutor Agent | Plan-and-Execute | SM-2 spaced repetition; B2C flywheel engine |
| Exam Strategist Agent | Plan-and-Execute | Macro study plans |
| Performance Analytics Agent | Plan-and-Execute | Cohort intelligence; anonymised B2B data |
| LMS Integration Agent | Plan-and-Execute | Next.js + Tailwind + Flutter + Supabase architecture |

---

## 13. Vertical-Specific Rules

### Healthcare

- Clinical AI Agent outputs **must always** include: `"Guardrail: This is a system-level architectural recommendation, not a clinical diagnosis or medical opinion."`
- NQAS pre-assessment outputs → Class C QA (human review gate mandatory).
- KB domains and decay rates:

| Source | Decay Rate | Validity (days) |
|---|---|---|
| ABDM (ABHA, HIP, HIU) | Fast | 180 |
| NMC Act 2020 | Fast | 180 |
| NABH 4th Edition | Medium | 365 |
| NQAS | Medium | 365 |
| DPDP Act 2023 | Fast | 180 |

### Legal

- **ALL** Legal vertical outputs must include the mandatory disclaimer, injected by `BaseAgent.report()`:
  > *"This output is generated by an AI system for informational and analytical purposes only. It does not constitute legal advice. Consult a qualified legal practitioner before acting on any information herein."*
- Legal opinion-class outputs → Class C QA mandatory.
- Regulatory Watch Agent is the **primary publisher of KB supersession events**. On a new SEBI/RBI/MCA circular: publish `regulatory.update.legal`, which triggers the KB Validity Engine to zero out affected documents.

| Source | Decay Rate | Validity (days) |
|---|---|---|
| BNS 2023 | Fast | 180 |
| Companies Act | Fast | 180 |
| SEBI LODR | Fast | 180 |
| RBI Master Directions | Fast | 180 |
| DPDP Act 2023 | Fast | 180 |

### Logistics

| Source | Decay Rate | Validity (days) |
|---|---|---|
| DGFT, Customs Tariff, GST/e-way, Warehousing | Medium | 365 |

### EdTech *(Phase 4)*

- Dynamic current affairs pipeline maps daily news, Economic Survey releases, and Supreme Court judgments to UPSC syllabus nodes.
- Multi-source verification required; editorial/opinion content filtered automatically.
- Anonymisation Pipeline (Agent 43) must run before any B2C aspirant data is exported as B2B cohort intelligence.

---

## 14. Workflow Engine (Upstash Workflow)

DAG definitions live in `verticals/workflows/`. Each vertical gets its own DAG file.

| File | Status | Description |
|---|---|---|
| `healthcare_project.py` | ✅ Done | Healthcare vertical engagement workflow |
| `ceo_weekly_report.py` | ✅ Done | CEO weekly intelligence digest |
| `retention_cron.py` | ✅ Done | Client Health Score computation + escalation |
| `worker.py` | ✅ Done | Upstash Workflow worker entrypoint |
| `legal_project.py` | 🔲 **Sprint 3.2** | Legal vertical engagement workflow — **this is the next file to build** |
| `logistics_project.py` | 🔲 Planned | Logistics vertical engagement workflow |

---

## 15. Running & Validation

### Installation

```bash
pip install -e ".[dev]"
```

### Tests

```bash
pytest                                          # All unit tests
pytest --cov=packages --cov-report=term-missing # With coverage
python -m mypy packages scripts                 # Type checking (strict)
ruff check packages scripts                     # Linting
```

### Sprint Validation Scripts

```bash
python -m scripts.test_sprint1_1_business_ops       # Phase 1 — Business Ops
python -m scripts.test_sprint1_2_healthcare_dag      # Phase 1 — Healthcare DAG
python -m scripts.test_sprint2_1_retention           # Phase 2 — Client Retention
python -m scripts.test_phase2_e2e                    # Phase 2 — Full E2E
python -m scripts.test_upstash_connections           # Upstash connectivity check
python -m scripts.test_sprint3_1_scraper_pipeline    # Phase 3 — Legal Regulatory Scraper
```

---

## 16. Skills

This project uses the Antigravity IDE autoskills system. Skills are locked in `skills-lock.json` at the repo root and are always available in the workspace. They encode project-specific patterns, conventions, and best practices that override generic coding instincts.

### 16.1 The Mandatory Protocol

**Before writing or editing any code**, the coding agent MUST:

1. Identify which skills are relevant to the task using the dispatch table below.
2. Load every relevant skill.
3. Read the skill fully before producing any code.
4. Apply the skill's conventions — do not deviate without an explicit reason documented in a comment.

This protocol is not optional. Skipping it and writing code from general knowledge is the primary source of style drift, inconsistency, and rework in this codebase.

### 16.2 Skill Registry

| Skill ID | Source | Load When |
|---|---|---|
| `fastapi-python` | `mindrally/skills` | Writing or editing any FastAPI route, middleware, dependency, lifespan handler, or background task in `packages/` |
| `fastapi-templates` | `wshobson/agents` | Scaffolding a new FastAPI agent service, adding router structure, or wiring agent endpoints into `worker.py` |
| `pydantic` | `bobmatnyc/claude-mpm-skills` | Defining or editing any Pydantic `BaseModel` — agent I/O schemas, Kafka message schemas, memory envelope models, API request/response bodies |
| `python-executor` | `inferen-sh/skills` | Writing agent execution logic (`BaseAgent.run()`, task dispatch, tool calls, async execution flows) |
| `python-testing-patterns` | `wshobson/agents` | Writing or editing any file under `tests/` or `scripts/` — unit tests, integration tests, sprint validation scripts |

### 16.3 Task → Skill Dispatch

Use this table to determine which skills to load for common tasks in this repo:

| Task | Skills to Load |
|---|---|
| New agent class (any vertical) | `python-executor` · `pydantic` |
| New agent input/output schema | `pydantic` |
| New FastAPI route or dependency | `fastapi-python` · `pydantic` |
| New agent service endpoint / router | `fastapi-python` · `fastapi-templates` · `pydantic` |
| New Upstash Workflow DAG (`workflow_engine/`) | `python-executor` · `fastapi-python` |
| New Kafka producer or consumer (`core/messaging/`) | `python-executor` · `pydantic` |
| New memory module (`core/memory/`) | `python-executor` · `pydantic` |
| New unit test or sprint validation script | `python-testing-patterns` |
| Editing `BaseAgent` or `AgentConfig` | `python-executor` · `pydantic` |
| Editing any existing Pydantic schema | `pydantic` |
| Any task touching ≥ 2 of the above | Load all matching skills before starting |

### 16.4 When Multiple Skills Apply

Load all of them. Read them in this order: `pydantic` → `python-executor` → `fastapi-python` → `fastapi-templates` → `python-testing-patterns`. Where skills conflict, prefer the more specific one (e.g. `fastapi-templates` over `fastapi-python` for scaffolding a full new service).

---

## 17. Critical Rules for AI Coding Agents

When generating code in this repository, the following rules are non-negotiable:

0. **Load relevant skills before writing any code.** Consult Section 16 to identify which skills apply to the task. Read every relevant skill in full before producing output. Do not write code from general knowledge when a skill is available — the skill is the source of truth for patterns and conventions in this codebase.

1. **No direct HTTP/RPC between agents.** All coordination uses Kafka producers/consumers from `shared_services/messaging/`. Imports from `shared_services/messaging/` only.

2. **Upstash Workflow for DAGs — not LangGraph, not Temporal.** The PRD references LangGraph and Temporal; the actual implementation uses Upstash Workflow. All new workflow DAGs go in `verticals/workflows/`.

3. **Upstash Vector for semantic memory — not Pinecone, not Weaviate.** Any vector DB code uses `shared_services/memory/semantic.py` backed by Upstash Vector.

4. **IP Registry check is mandatory before new engagements.** Any code initiating a new consulting workflow must call `shared_services/ip_registry/` before spawning bespoke generation.

5. **KB documents must carry validity envelopes.** Any insert into Upstash Vector must include the `validity_metadata_envelope` schema from `shared_services/kb_validity/`. Never insert bare documents.

6. **Approval gates must block — not advise.** Workflow code at a human approval gate must PAUSE and AWAIT `mas.oversight.approved`. Do not fire-and-forget approval checks.

7. **Legal disclaimer is not opt-in.** The mandatory disclaimer is injected in `BaseAgent.report()` for `Vertical.LEGAL`. Do not add it manually in subclasses — and do not bypass or override the `report()` method for Legal vertical agents.

8. **No clinical diagnosis logic.** Clinical AI Agent outputs system-level architectural recommendations only. Any code branching toward individual patient-level diagnosis must be removed.

9. **`qa_class` must be explicit.** Every deliverable payload passed to the Quality & Compliance Agent must include `qa_class: "A" | "B" | "C"`. Do not default silently.

10. **Output confidence must propagate downward.** When an agent's output derives from multiple KB documents, set `output.confidence_score = min(source_doc.confidence_score for all sources)`.

11. **Pydantic v2 for all I/O.** All agent inputs and outputs are modelled as Pydantic v2 `BaseModel` schemas. No raw dicts for structured data.

12. **mypy strict compliance.** All new code must pass `python -m mypy packages scripts` in strict mode before being considered done.

13. **Air-gapped paths are branches, not patches.** When implementing LLM calls, always branch on `deployment_mode: "cloud" | "airgapped"`. Do not conditionally patch URLs into cloud LLM code paths.

---

## 18. PRD v3.0 Roadmap Items (Not Yet Implemented)

These items are defined in the PRD but have no corresponding code yet. Do not reference them as if they exist:

- Government Tender Bidding Agent *(Phase 5)*
- High-Ticket Affiliate Marketing revenue engine *(Phase 5)*
- Air-gapped / on-premise LLM deployments *(Phase 5)*
- Marketing Agent and Market Intelligence Agent *(Phase 4)*
- Self-Improvement Engine as a standalone agent *(Phase 4)*
- Dynamic Pricing Engine *(Phase 4)*
- EdTech vertical — all 7 agents *(Phase 4)*
- Client-facing Next.js portals and Flutter mobile app *(Phase 4)*
- Full Redpanda Cloud Serverless (primary), Confluent Cloud (flagged as IBM-owned)*

---

## 19. Glossary

| Term | Definition |
|---|---|
| MAS | Multi-Agent System |
| DAG | Directed Acyclic Graph — task dependency structure for parallel execution |
| KB Validity Decay | Logarithmic decay of a KB document's `confidence_score` over time |
| Supersession | Regulatory Watch Agent marks a KB document as replaced; sets `confidence_score = 0` |
| IP Registry | Catalogue of reusable consulting deliverables (`Template \| Accelerator \| Product`) |
| CHS | Client Health Score (0–100 weekly metric); triggers Account Growth Agent if < 65 |
| NQAS | National Quality Assurance Standards — public hospital accreditation |
| ABDM | Ayushman Bharat Digital Mission |
| DPDP | Digital Personal Data Protection Act 2023 |
| Air-gapped | Systems physically isolated from external networks (Phase 5 deployment option) |
| Hybrid AI Architecture | Cloud LLM APIs + air-gapped on-premise open-source LLMs (Phase 5) |
| B2C Flywheel | EdTech loop: aspirant data → Adaptive Tutor improvement → anonymised B2B cohort intelligence |
| IRT | Item Response Theory — adaptive test calibration |
| SM-2 | Spaced Repetition algorithm used by Adaptive Tutor Agent |
| Plan-and-Execute | Agentic pattern: produce full task plan, then execute step-by-step |
| ReAct | Agentic pattern: interleaved Reason → Act → Observe cycles |
| QStash | Upstash's message queue powering Upstash Workflow |
| Upstash Workflow | Serverless durable workflow engine replacing LangGraph/Temporal in this implementation |

---

*This file is derived from PRD v3.0, README (Sprint 3.1), and skills-lock.json (v1). When any source changes, regenerate this file. Do not manually patch individual sections without updating the source documents.*
