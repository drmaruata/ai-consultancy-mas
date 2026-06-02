MAS PRD version 3.0.

```markdown
# Product Requirements Document
## AI Consultancy Agency — Multi-Agent System (MAS)

---

> **Document status:** Draft v3.0
> **Prepared by:** Founding Team
> **Last updated:** 2026
> **Classification:** Internal — Confidential
> **Supersedes:** PRD v2.0

---

## Changelog

| # | Improvement | Sections Affected | Version |
|---|-------------|-------------------|---------|
| I11 | Hybrid AI Architecture (Cloud API + Air-gapped On-Premise LLMs) | §17, §20 | v3.0 |
| I12 | Multi-LLM Cloud Diversification (Anthropic, OpenAI, Google Gemini) | §17 | v3.0 |
| I13 | Public Health Expansion (NQAS) & Bioinformatics Capability | §7, §16 | v3.0 |
| I14 | Hospital Operational IP Productization (Evacuation Protocols) | §7 | v3.0 |
| I15 | Dynamic Current Affairs Data Pipeline for EdTech (UPSC/Polity/Economics) | §10, §16 | v3.0 |
| I16 | Modernized EdTech LMS Stack (Next.js, Tailwind, Flutter, Supabase) | §10, §17 | v3.0 |
| I17 | Government Tender Bidding Agent (New Layer 1 Agent) | §4, §5, §11, App. A | v3.0 |
| I18 | High-Ticket Affiliate Marketing Revenue Engine | §5, §19 | v3.0 |
| I1-I10 | Integration of Account Growth Agent, Dynamic Pricing, KB Validity Decay, Client Health Scoring, Parallel QA, EdTech B2C Flywheel, Market Intel Agent, DAG scheduling, IP Registry, and Proactive MAS Health Report | Multiple | v2.0 |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Vision & Strategic Goals](#2-vision--strategic-goals)
3. [Scope & Industry Verticals](#3-scope--industry-verticals)
4. [Full MAS Topology — v3.0](#4-full-mas-topology--v30)
5. [Shared Platform Agents](#5-shared-platform-agents)
6. [Shared Services Layer](#6-shared-services-layer)
7. [Healthcare Vertical — Agent Internals](#7-healthcare-vertical--agent-internals)
8. [Logistics & Supply Chain Vertical — Agent Internals](#8-logistics--supply-chain-vertical--agent-internals)
9. [Legal & Compliance Vertical — Agent Internals](#9-legal--compliance-vertical--agent-internals)
10. [EdTech & Competitive Exam Vertical — Agent Internals](#10-edtech--competitive-exam-vertical--agent-internals)
11. [MAS Design Specification](#11-mas-design-specification)
12. [Memory Architecture](#12-memory-architecture)
13. [Communication Architecture](#13-communication-architecture)
14. [Human Oversight & Guardrails](#14-human-oversight--guardrails)
15. [Inter-Vertical Synergies](#15-inter-vertical-synergies)
16. [Domain Knowledge Bases](#16-domain-knowledge-bases)
17. [Technology Stack](#17-technology-stack)
18. [Phased Build Plan](#18-phased-build-plan)
19. [KPIs & Success Metrics](#19-kpis--success-metrics)
20. [Risks & Mitigations](#20-risks--mitigations)
21. [Appendix A — Agent Registry v3.0](#appendix-a--agent-registry-v30)
22. [Appendix B — Glossary](#appendix-b--glossary)

---

## 1. Executive Summary

This document defines the v3.0 product requirements for an **Autonomous AI Consultancy Agency** operated by a Multi-Agent System (MAS). The agency delivers AI consulting, automation, and advisory services across four high-value Indian industry verticals: **Healthcare**, **Logistics & Supply Chain**, **Legal & Compliance**, and **EdTech & Competitive Exams**.

The MAS runs the company end-to-end — acquiring clients, bidding on tenders, delivering consulting engagements, managing finances and operations, and continuously improving its own performance through a self-learning feedback loop. A human oversight layer retains approval authority over commercial commitments, novel client types, and core agent behaviour changes.

**v3.0 additions** elevate the agency to a market-leading, enterprise-grade consultancy. This includes a **Hybrid AI Architecture** allowing for air-gapped secure deployments, deep expansion into the public healthcare sector (NQAS), real-time dynamic data ingestion for EdTech, and autonomous institutional revenue capture via a dedicated Government Tender Bidding Agent and High-Ticket Affiliate Marketing integrations.

**Total agent count (v3.0):** 43 specialised agents across 6 architectural layers.

---

## 2. Vision & Strategic Goals

### Vision Statement

To build the world's first fully autonomous AI consultancy that operates, learns, and scales without linear headcount growth — delivering enterprise-grade AI advisory to Indian healthcare, logistics, legal, and education sectors, while autonomously compounding its own revenue, knowledge, and market position.

### Strategic Goals — v3.0

| Goal | Description | Year 1 Target | Year 2 Target |
|------|-------------|---------------|---------------|
| Autonomous revenue | Agency closes and delivers without human intervention | ≥ 60% of engagements | ≥ 85% |
| Public Sector Penetration | Institutional contracts secured autonomously via continuous tender bidding | ≥ 3 contracts | ≥ 10 contracts |
| Data Sovereignty | Compliance for sensitive clients via air-gapped on-premise LLMs | Pilot phase | ≥ 25% of Tier-1 clients |
| Passive Revenue | Revenue generated via automated high-ticket affiliate structures | 5% of MRR | ≥ 15% of MRR |
| Multi-vertical delivery | Simultaneous active delivery across all 4 verticals | By Month 6 | Stable |
| Self-improvement | Agent performance improves each sprint | +15% quality score/quarter | +20% |
| Human oversight ratio | Fraction of decisions requiring human approval | < 20% | < 10% |

---

## 3. Scope & Industry Verticals

The MAS focuses on four verticals chosen for high AI adoption potential, regulatory complexity, data availability, and complementary cross-vertical use cases.

### Vertical Summary

| Vertical | Target Clients | Core AI Use Cases | Strategic Differentiator |
|----------|---------------|-------------------|--------------------------|
| **Healthcare** | Hospitals, labs, clinics, pharma, **public health systems** | CDSS, ABDM/NQAS compliance, clinical analytics, bioinformatics | Secure Air-gapped AI options |
| **Logistics** | 3PLs, manufacturers, e-commerce, exporters | Demand forecasting, inventory, routing, ERP | Supply chain visibility IP |
| **Legal & Compliance** | Law firms, corporate legal, fintechs | Contract review, regulatory watch, litigation | Secure Air-gapped AI options |
| **EdTech** | Coaching institutes, ed-platforms, aspirants | Adaptive learning, mock tests, UPSC/NEET | **B2C Data Flywheel + Real-time Current Affairs** |

---

## 4. Full MAS Topology — v3.0

### 4.1 Architecture Overview

```text
┌───────────────────────────────────────────────────────────────────────────────┐
│                         LAYER 0 — ORCHESTRATION                               │
│                    ┌────────────────────────────┐                             │
│                    │      CEO Orchestrator      │                             │
│                    │  Strategy · KPIs ·         │                             │
│                    │  Inter-vertical arb. ·     │                             │
│                    │  Weekly MAS Health Report  │                             │
│                    └──────────────┬─────────────┘                             │
└──────────────────────────────────┼────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────────────┐
│                  LAYER 1 — BUSINESS OPS AGENTS [+1 NEW in v3.0]               │
│  ┌─────────┐ ┌─────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────┐ ┌───┐   │
│  │  Sales  │ │Marketng │ │   Finance    │ │   Ops / HR   │ │Account │ │Mkt│   │
│  │  Agent  │ │  Agent  │ │   Agent      │ │   Agent      │ │ Growth │ │Int│   │
│  │         │ │ +Affil. │ │ +Affiliate   │ │ +Client      │ │ Agent  │ │   │   │
│  │         │ │         │ │  +Dyn Pricing│ │  Health Scor.│ │        │ │   │   │
│  └─────────┘ └─────────┘ └──────────────┘ └──────────────┘ └────────┘ └───┘   │
│                                  ┌──────────────────────────┐                 │
│                                  │ Gov. Tender Bidding Agent│                 │
│                                  │ [NEW]                    │                 │
│                                  └──────────────────────────┘                 │
└───────────────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────────────┐
│                              LAYER 2 — SHARED SERVICES                        │
│  ┌──────────────────────┐  ┌────────────────────┐  ┌────────────────────────┐ │
│  │  Memory & Knowledge  │  │  Quality &         │  │  Self-Improvement      │ │
│  │  +KB Validity Decay  │  │  Compliance        │  │  Engine                │ │
│  │  +Supersession flags │  │  +Tiered Parallel  │  │  +A/B prompt testing   │ │
│  │  +IP Registry        │  │   QA Pipeline      │  │  +IP candidacy scoring │ │
│  └──────────────────────┘  └────────────────────┘  └────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────────────┐
│                   LAYER 3 — INDUSTRY VERTICAL CLUSTERS                        │
│                                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │ HEALTHCARE  │  │  LOGISTICS  │  │    LEGAL    │  │  EDTECH + B2C       │   │
│  │             │  │             │  │             │  │                     │   │
│  │ Vertical Mgr│  │ Vertical Mgr│  │ Vertical Mgr│  │  Vertical Mgr       │   │
│  │ Clinical AI │  │ Supply Chain│  │ Contract    │  │  Curriculum(Dynamic)│   │
│  │ Compliance  │  │ Inventory   │  │ Regulatory  │  │  Assessment         │   │
│  │ EHR Integr. │  │ Route Optim │  │ Research    │  │  Adaptive Tutor     │   │
│  │ Analytics   │  │ Demand Fcst │  │ Risk        │  │  Exam Strategist    │   │
│  │ Pharma Supp │  │ ERP Integr. │  │ Policy Draft│  │  Performance        │   │
│  │ Patient Eng │  │ Trade Compl │  │ Litigation  │  │  LMS Integration    │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────────────┐
│                    LAYER 4 — DOMAIN KNOWLEDGE BASES                           │
│   (Includes Validity Timestamps and Supersession Flags for all domains)       │
└───────────────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────────────┐
│                       LAYER 5 — CLIENT INTERFACES                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │  Hospital   │  │    Ops      │  │    Legal    │  │  Learning Portal    │   │
│  │  Portal     │  │  Dashboard  │  │  Workspace  │  │  + B2C Aspirant App │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────────────┐
│                  LAYER 6 — HUMAN OVERSIGHT LAYER                              │
│   Approval gates · Audit log · Escalation triggers · Contract sign-off        │
│   Agent behaviour review · Ethics board · Weekly MAS Health Report            │
└───────────────────────────────────────────────────────────────────────────────┘

```

### 4.2 Agent Count by Layer — v3.0

| Layer | Name | v2.0 Count | v3.0 Count | Delta |
| --- | --- | --- | --- | --- |
| 0 | Orchestration | 1 | 1 | — |
| 1 | Business Ops | 6 | 7 | +1 (Gov. Tender Bidding) |
| 2 | Shared Services | 3 | 3 | — |
| 3 | Industry Verticals (4 × 7) | 28 | 28 | Upgraded capabilities |
| **Total** |  | **42** | **43** | **+1 net additions** |

---

## 5. Shared Platform Agents

### 5.1 Government Tender Bidding Agent — NEW (v3.0 — I17)

**Role:** Autonomously monitor, qualify, and generate technical and financial bid documents for government and institutional contracts.

**Responsibilities:**

* Monitor government portals (GEM, eProcure) and state health/education department sites for consulting and AI implementation tenders.
* Parse Request for Proposal (RFP) requirements and map them against the agency's IP Registry and past capabilities.
* Filter out tenders where the agency does not meet financial or technical eligibility criteria.
* Coordinate with the **Finance Agent** for bid pricing (incorporating dynamic pricing buffers for government payment cycles).
* Coordinate with the relevant **Vertical Manager** for technical solution architecture generation.
* Compile complete, compliant bid packages (Technical Bid + Financial Bid).

**Escalation:** All generated tender submissions require Human Oversight approval before upload to government portals.

**KPIs:** Tenders screened per week ≥ 20 · Bid package generation time ≤ 48 hours · Tender Win Rate ≥ 15%.

### 5.2 Sales Agent

**Role:** Autonomous pipeline management from lead discovery through contract close. Monitors inbound channels, qualifies leads, generates customized proposals using IP Registry assets, executes follow-up sequences, and routes proposals to the Finance Agent for dynamic pricing validation.

### 5.3 Marketing Agent — with Affiliate Management (v3.0 — I18)

**Role:** Autonomous brand-building, demand generation, competitive positioning, and affiliate network management.

**Responsibilities:**

* Publish weekly long-form LinkedIn posts per vertical.
* Convert approved deliverables into case study drafts via IP Registry.
* **v3.0 Addition:** Generate promotional assets (banners, copy) for the agency's high-ticket affiliate partners (selling EdTech SaaS, automated compliance tools).
* Monitor affiliate compliance with brand and ethical guidelines.

### 5.4 Finance Agent — with Dynamic Pricing & Affiliate Payouts (v3.0 — I18)

**Role:** Autonomous financial management, dynamic pricing intelligence, and affiliate commission management.

**Responsibilities:**

* Calculate dynamic pricing for all proposals (accounting for client tier, geography, urgency, complexity, and competitive context).
* Invoice generation, API cost monitoring, P&L reporting.
* **v3.0 Addition:** Manage affiliate tier structures and automate commission payouts. Track SaaS metrics generated by affiliates (LTV, CAC, Affiliate ROI).

### 5.5 Ops / HR Agent — with Client Health Scoring

**Role:** Manage agency infrastructure, vendor relationships, and client health monitoring. Computes weekly Client Health Scores (CHS) using login frequency, response times, satisfaction scores, and payment timeliness. Auto-triggers the Account Growth Agent if CHS drops below 65.

### 5.6 Account Growth Agent

**Role:** Maximise lifetime revenue per client through autonomous upsell, cross-sell, and expansion detection. Automatically triggered post-engagement to analyze client profiles against the IP Registry and draft personalized retainer or cross-vertical proposals.

### 5.7 Market Intelligence Agent

**Role:** Continuously monitor the competitive landscape, regulatory pipeline, and market opportunities. Scans competitor sites, VC funding announcements, and regulatory portals to compile a weekly digest for the CEO, Marketing, and Sales agents.

---

## 6. Shared Services Layer

### 6.1 Memory & Knowledge Agent — with KB Validity Decay & IP Registry

**Role:** Persistent memory store, knowledge retrieval, validity lifecycle management, and IP asset registry.

**KB Validity Decay:** Every document in the KB carries a validity metadata envelope (decay rate: fast, medium, slow). Confidence scores decay logarithmically based on the domain. Decayed documents (< 0.7 confidence) cap the agent's output confidence, preventing the hallucination of stale laws.

**IP Registry:** Structured catalogue of approved deliverables. Evaluated for reusability (Template, Accelerator, Product). Checked by Vertical Managers before every new engagement to bypass bespoke work and accelerate delivery.

### 6.2 Quality & Compliance Agent — Tiered Parallel QA

**Role:** Validate all client-facing deliverables using a tiered, parallelised pipeline.

* **Class A (Pattern-matched):** Fast-track, lightweight rule check (< 2 mins).
* **Class B (Standard):** Full LLM validation + domain rules (< 15 mins).
* **Class C (High-stakes):** Healthcare clinical content, legal opinions; requires human review gate.

### 6.3 Self-Improvement Engine

**Role:** Evaluate agent performance post-engagement and continuously improve prompts, tool selection, and knowledge. Computes IP asset reusability scores, automates A/B testing for prompt changes, and feeds EdTech cohort data into learning models.

---

## 7. Healthcare Vertical — Agent Internals (v3.0)

### 7.1 Vertical Overview

Target clients: Government/private hospitals, lab chains, pharma, health-tech startups.

**Regulatory domain (v3.0 expansion):**

* ABDM — ABHA, HIP, HIU standards [Decay: Fast — 180 days]
* NMC Act 2020 [Decay: Fast — 180 days]
* NABH (4th edition) [Decay: Medium — 365 days]
* **NQAS (National Quality Assurance Standards)** [Decay: Medium — 365 days]
* DPDP Act 2023 [Decay: Fast — 180 days]

**IP Registry assets (v3.0 additions):**

* **Hospital Evacuation Protocol Blueprint** [Product — reusability 0.95]
* NABH Pre-Assessment AI Toolkit [Accelerator]

### 7.2 Agent Architecture

* **Vertical Manager Agent (Healthcare):** Coordinates sub-agents via DAG task scheduling.
* **Clinical AI Agent (with Bioinformatics — v3.0):** Designs CDSS, differential diagnosis systems, and ICU early-warning models. **v3.0 Upgrade:** Now designs architectures for integrating public health data, genomic pipelines, and epidemiological tracking into hospital IT. (Guardrail: No individual patient diagnosis).
* **Regulatory Compliance Agent (with NQAS — v3.0):** Monitors regulations. **v3.0 Upgrade:** Now executes NQAS pre-assessment gap analyses specifically tailored for district and public hospitals, alongside NABH and ABDM workflows.
* **EHR Integration Agent:** FHIR/HL7 mapping, HMIS setup, patient data migration.
* **Health Analytics Agent:** Dashboards for bed capacity, mortality analysis, infection control.
* **Pharma Supply Agent:** EML stock optimization, FEFO tracking, cold chain monitoring.
* **Patient Engagement Agent:** AI triage chatbots, post-discharge automation, multilingual NLP.

---

## 8. Logistics & Supply Chain Vertical — Agent Internals

### 8.1 Vertical Overview

Target clients: 3PLs, manufacturers, e-commerce, cold chain operators.
Regulatory domain: DGFT, Customs Tariff Act, GST/e-way bills, Warehousing Regulation Act.

### 8.2 Agent Architecture

* **Vertical Manager Agent (Logistics):** DAG coordination.
* **Supply Chain Agent:** Supply chain visibility architecture, supplier risk scoring.
* **Inventory Agent:** ABC-XYZ analysis, safety stock optimization, multi-warehouse balancing.
* **Route Optimizer Agent:** VRP solving, dynamic rerouting, EV fleet transition studies.
* **Demand Forecaster Agent:** ML time-series forecasting (ARIMA, Prophet), promotional uplift modeling.
* **ERP Integration Agent:** AI layer integrations for SAP S/4HANA, Oracle SCM, Tally Prime.
* **Trade Compliance Agent:** HS code classification, DGFT license checks, export promotion identification.

---

## 9. Legal & Compliance Vertical — Agent Internals

### 9.1 Vertical Overview

Target clients: Law firms, in-house legal, fintechs.
Regulatory domain: BNS 2023, Companies Act, SEBI LODR, RBI Master Directions, DPDP Act 2023.

### 9.2 Agent Architecture

* **Vertical Manager Agent (Legal):** Coordinates agents. *MANDATORY DISCLAIMER appended to ALL outputs.*
* **Contract Analysis Agent:** AI contract review, redlining, change-of-control clause extraction.
* **Regulatory Watch Agent:** Scrapes SEBI, RBI, MCA portals. **PRIMARY publisher of supersession events** dropping KB confidence for outdated laws to zero.
* **Legal Research Agent:** Case law research, judgment summarization via SCC Online/Manupatra APIs.
* **Risk Assessment Agent:** Heatmaps, DPDP data protection risk scoring.
* **Policy Drafting Agent:** DPDP-compliant privacy policies, SaaS Terms of Service.
* **Litigation Support Agent:** Chronology construction, discovery request drafting.

---

## 10. EdTech & Competitive Exam Vertical — Agent Internals (v3.0)

### 10.1 Vertical Overview

Target clients: UPSC/NEET/JEE coaching institutes (B2B), Exam aspirants (B2C).
**B2C Flywheel:** Aspirants use AI study plans -> Anonymized performance data feeds Adaptive Tutor -> Aggregated cohort data sold to B2B clients as Cohort Intelligence.

### 10.2 Agent Architecture Updates

* **Vertical Manager Agent (EdTech):** Manages B2B projects and B2C continuous service.
* **Curriculum Design Agent (Dynamic Current Affairs — v3.0):** Builds and maps curricula. **v3.0 Upgrade:** Syllabi for UPSC Polity, Economics, and Ethics are updated dynamically via a real-time data ingestion pipeline mapping daily news, economic surveys, and supreme court judgments directly to syllabus nodes.
* **Assessment Agent:** MCQ generation, mock test calibration via Item Response Theory (IRT).
* **Adaptive Tutor Agent:** Personalises learning paths using SM-2 spaced repetition (B2C flywheel core).
* **Exam Strategist Agent:** Generates macro-level exam preparation and timing strategies.
* **Performance Analytics Agent:** Heatmaps, percentile rankings. Anonymizes data for B2B cohort intelligence.
* **LMS Integration Agent (Modernized Stack — v3.0):** **v3.0 Upgrade:** Deprecates legacy plugins (Moodle). Architects bespoke EdTech platforms using **Next.js, Tailwind CSS** (frontend), **Flutter** (mobile), and **Supabase** (backend/analytics).

---

## 11. MAS Design Specification

### 11.1 Agent Execution Modes

* **Reactive:** Event-driven via message bus.
* **Proactive:** Cron executions (Regulatory watch, CHS computation).
* **Collaborative:** DAG-based multi-agent parallel workflows via Upstash Workflow.
* **Reflective:** Self-evaluation post-task.
* **Flywheel:** B2C data pipeline loop.

### 11.2 Reasoning Architecture

All Tier 0–3 agents use **Plan-and-Execute** with a mandatory Phase 0 **IP Registry Check** (to fast-track known use cases). Tier 4 agents use **ReAct** (Reason + Act). All agents conduct a **Domain Pre-validation** checking KB validity scores before QA handoff.

---

## 12. Memory Architecture

* **Working Memory:** Ephemeral context window.
* **Episodic Memory:** Long-term structured logs of past tasks (powers Self-Improvement Engine).
* **Semantic Memory:** Vector DB containing all KB documents with validity metadata envelopes.
* **Procedural Memory:** Versioned system prompts and workflow templates.
* **IP Registry:** Structured catalogue of approved deliverables with reusability scores.

---

## 13. Communication Architecture

All inter-agent communication passes through a central message bus (Apache Kafka). Agents never call each other directly via HTTP/RPC.

**Key Topics:** `task.assigned`, `deliverable.ready`, `client.health.alert`, `regulatory.update.{vertical}`, `mas.health.report`.

---

## 14. Human Oversight & Guardrails

### 14.1 Proactive Weekly MAS Health Report

Auto-generated by CEO Orchestrator every Monday. Contains Revenue Snapshot, Agent Performance, Client Health (CHS alerts), KB Health (decay warnings), and Market Intelligence highlights.

### 14.2 Mandatory Approval Gates

* Contract signing > ₹10 lakh.
* Government/public sector tender submissions.
* Healthcare clinical recommendations / Legal opinion-class outputs.
* Dynamic pricing outputs > 2.5× base rate.

---

## 15. Inter-Vertical Synergies

Cross-vertical triggers managed by the Account Growth Agent (e.g., pitching Trade Compliance to a Logistics client; pitching DPDP compliance to a Healthcare client). Cross-vertical DAG synchronisation is chaired by the lead Vertical Manager.

---

## 16. Domain Knowledge Bases

* **Healthcare:** ABDM, HL7 FHIR, NABH, **NQAS (v3.0)**, ICMR guidelines, DPDP implications.
* **Logistics:** SAP/Oracle APIs, ITC-HS codes, GSTN e-way bills, IATA regulations.
* **Legal:** BNS 2023, Companies Act, SEBI, RBI, DPDP Act.
* **EdTech:** Exam syllabi, past papers, NCERT, **Real-time current affairs pipeline (v3.0)**.

---

## 17. Technology Stack — The Hybrid AI Architecture (v3.0)

The v3.0 architecture implements a multi-modal deployment strategy to support standard operations and highly secure, air-gapped enterprise environments.

### 17.1 Core Infrastructure

| Component | Technology | Notes |
| --- | --- | --- |
| **Cloud LLM Backbone** | Anthropic (Claude), OpenAI (ChatGPT), Google Gemini APIs | Dynamic routing based on task complexity, context length, and rate-limit fallbacks. |
| **On-Premise / Air-gapped LLMs** | Llama 3, Mixtral (or fine-tuned local models) | Deployed on client hardware for Healthcare/Legal clients requiring zero external data transmission (DPDP compliance). |
| Agent orchestration | Upstash Workflow | QStash-backed, serverless, durable DAG execution. |
| Vector database | Upstash Vector | Semantic KB with validity metadata (hybrid dense + sparse index). |
| Cache & Rate Limiting | Upstash Redis | Fast ephemeral state and quota management. |
| External Knowledge / MCP | Context7 MCP | Dynamic fetching of up-to-date framework/library documentation. |
| Relational DB / Backend | Supabase (PostgreSQL) | Episodic memory, IP Registry, real-time sync. |
| Message bus | Apache Kafka | Event-driven inter-agent comms. |
| Dynamic pricing engine | Python service | Finance Agent's multi-signal pricing model. |

### 17.2 Frontend / Client Interfaces

| Interface | Tech | Users |
| --- | --- | --- |
| Client Portals (HC, Legal, Log.) | Next.js + Tailwind CSS | B2B Consulting Clients |
| Learning Portal (B2B) | Next.js + Tailwind CSS | EdTech coaching clients |
| Aspirant App (B2C) | Flutter | Cross-platform mobile for individual aspirants |
| Internal Oversight Console | React | Operators and founders |

---

## 18. Phased Build Plan

* **Phase 0 (Weeks 1–4):** Foundation (Message bus, Memory DB, basic routing).
* **Phase 1 (Weeks 5–8):** First Revenue (Sales Agent, Finance Agent, HC vertical v1).
* **Phase 2 (Weeks 9–14):** Growth Engines (Account Growth Agent, CHS, Logistics vertical).
* **Phase 3 (Weeks 15–22):** Full Vertical Coverage (Legal, EdTech B2C Flywheel, KB validity).
* **Phase 4 (Months 6–9):** Intelligence (Market Intel, Dynamic Pricing v2, MAS Health Report).
* **Phase 5 (Month 10+ — v3.0 scale):** Hybrid AI Deployments (Air-gapped LLMs), Government Tender Bidding Agent activation, High-Ticket Affiliate Marketing network launch.

---

## 19. KPIs & Success Metrics

* **Business:** Active clients (75 by M24), Retainer conversion rate (≥ 35%), Expansion revenue (≥ 30% by Y2).
* **Agent Performance:** Average quality score (≥ 82/100), Escalation rate (≤ 10% Y2).
* **Knowledge/IP:** IP reuse rate (≥ 40% Y2), Avg. delivery time reduction from IP (≥ 35%).
* **Institutional & Passive (v3.0):** Government Tender Win Rate (≥ 15%), Affiliate Revenue (≥ 15% of MRR by Month 12), Hybrid Deployment Adoption (≥ 25% of Tier-1 clients).

---

## 20. Risks & Mitigations

| Risk | Severity | Likelihood | Mitigation |
| --- | --- | --- | --- |
| Hallucinated regulatory information | Critical | Medium | Tiered QA pipeline; KB validity decay caps. |
| **Open-Source LLM Hallucinations (v3.0)** | High | Medium | Stricter evaluation loops in Tiered QA specifically for outputs generated by local air-gapped models. |
| **Tender Compliance Failure (v3.0)** | Critical | Medium | Mandatory Human Oversight review of all bids generated by the Government Tender Agent. |
| Legal liability / Patient safety risk | Critical | Low | Mandatory disclaimers; no individual patient diagnosis; opinion-class human review gates. |
| **Current Affairs Pipeline Noise (v3.0)** | Medium | High | Multi-source verification for Curriculum Agent; automatic filtering of editorial/opinion pieces. |
| Runaway API cost | High | Medium | Per-task token budget; automatic throttling at 20% overage. |
| Data breach / DPDP non-compliance | High | Low | **Air-gapped LLM deployments (v3.0)**; Supabase RLS; PII stripping pipelines. |

---

## 21. Appendix A — Agent Registry v3.0

Complete list of all 43 agents.

| # | Agent Name | Tier | Vertical | Primary Function | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | CEO Orchestrator | 0 | All | Strategy, routing, weekly MAS Health Report | Active |
| 2 | Sales Agent | 1 | All | Pipeline, proposals, close | Active |
| 3 | Marketing Agent | 1 | All | Content, SEO, IP-to-case-study, **Affiliate assets** | Upgraded |
| 4 | Finance Agent | 1 | All | Dynamic pricing, invoices, **Affiliate payouts** | Upgraded |
| 5 | Ops / HR Agent | 1 | All | Vendors, SLAs, Client Health Scoring | Active |
| 6 | Account Growth Agent | 1 | All | Upsell, cross-sell, retainer conversion | Active |
| 7 | Market Intelligence Agent | 1 | All | Competitor monitoring, regulatory pipeline | Active |
| 8 | **Gov. Tender Bidding Agent** | 1 | All | **Automated institutional bid generation** | **NEW** |
| 9 | Memory & Knowledge Agent | 2 | All | Vector DB, KB validity decay, IP Registry | Active |
| 10 | Quality & Compliance Agent | 2 | All | Tiered parallel validation, guardrails | Active |
| 11 | Self-Improvement Engine | 2 | All | Eval, A/B testing, IP candidacy scoring | Active |
| 12 | Vertical Manager (Healthcare) | 3 | Healthcare | DAG coordination, KPI reporting | Active |
| 13 | Clinical AI Agent | 4 | Healthcare | CDSS design, **Bioinformatics pipeline architecture** | Upgraded |
| 14 | Regulatory Compliance Agent | 4 | Healthcare | ABDM, NABH, NMC, **NQAS audits** | Upgraded |
| 15 | EHR Integration Agent | 4 | Healthcare | HL7 FHIR, HMIS, lab APIs | Active |
| 16 | Health Analytics Agent | 4 | Healthcare | Outcomes, bed management dashboards | Active |
| 17 | Pharma Supply Agent | 4 | Healthcare | Drug inventory, procurement automation | Active |
| 18 | Patient Engagement Agent | 4 | Healthcare | Appointments, ABHA PHR chatbots | Active |
| 19 | Vertical Manager (Logistics) | 3 | Logistics | DAG coordination, KPI reporting | Active |
| 20 | Supply Chain Agent | 4 | Logistics | Sourcing, risk, carbon tracking | Active |
| 21 | Inventory Agent | 4 | Logistics | Stock, reorder, SKU balancing | Active |
| 22 | Route Optimizer Agent | 4 | Logistics | Last-mile, fleet, EV feasibility | Active |
| 23 | Demand Forecaster Agent | 4 | Logistics | ML forecasting, seasonality | Active |
| 24 | ERP Integration Agent | 4 | Logistics | SAP, Oracle, Tally APIs | Active |
| 25 | Trade Compliance Agent | 4 | Logistics | Customs, GST, DGFT rules | Active |
| 26 | Vertical Manager (Legal) | 3 | Legal | DAG coordination, KPI reporting | Active |
| 27 | Contract Analysis Agent | 4 | Legal | Review, redline, clause extraction | Active |
| 28 | Regulatory Watch Agent | 4 | Legal | SEBI/RBI monitoring, **KB supersession** | Active |
| 29 | Legal Research Agent | 4 | Legal | Case law, statutes | Active |
| 30 | Risk Assessment Agent | 4 | Legal | Exposure scoring, DPDP risk | Active |
| 31 | Policy Drafting Agent | 4 | Legal | SOPs, DPDP-compliant docs | Active |
| 32 | Litigation Support Agent | 4 | Legal | Briefs, discovery timelines | Active |
| 33 | Vertical Manager (EdTech) | 3 | EdTech | DAG coordination, B2B + B2C tracks | Active |
| 34 | Curriculum Design Agent | 4 | EdTech | Syllabus mapping, **Dynamic Current Affairs pipeline** | Upgraded |
| 35 | Assessment Agent | 4 | EdTech | Question gen, IRT calibration | Active |
| 36 | Adaptive Tutor Agent | 4 | EdTech | Spaced repetition (B2C flywheel engine) | Active |
| 37 | Exam Strategist Agent | 4 | EdTech | Study plans, macro strategy | Active |
| 38 | Performance Analytics Agent | 4 | EdTech | Score trends, cohort intelligence | Active |
| 39 | LMS Integration Agent | 4 | EdTech | **Next.js, Tailwind, Flutter, Supabase architecture** | Upgraded |
| *Note: Agents 40-43 are allocated as internal sub-system controllers (IP Registry Engine, KB Validity Engine, Pricing Model, Anonymisation Pipeline) functioning underneath Layer 2.* |  |  |  |  |  |

---

## 22. Appendix B — Glossary

* **MAS:** Multi-Agent System.
* **Hybrid AI Architecture:** Deployment strategy utilizing both cloud APIs (Anthropic, OpenAI, Gemini) and air-gapped on-premise open-source LLMs.
* **Air-gapped:** Systems physically isolated from unsecured networks, used for sensitive DPDP-compliant client deployments.
* **NQAS:** National Quality Assurance Standards — public health hospital accreditation.
* **KB Validity Decay:** The mathematical decay of a KB document's confidence contribution over time.
* **Supersession:** Process of marking a KB document as replaced by a newer version.
* **IP Registry:** Structured catalogue of reusable consulting assets (templates, accelerators, products).
* **Client Health Score (CHS):** A 0–100 weekly metric indicating a client's engagement health.
* **Dynamic Pricing Model:** Finance Agent's multi-signal pricing engine.
* **B2C Flywheel:** Individual aspirant data improves AI quality, generating B2B data assets.
* **DAG:** Directed Acyclic Graph — task dependency structure enabling parallel execution.

---

*End of Document*