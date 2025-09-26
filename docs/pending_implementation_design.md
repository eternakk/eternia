# Pending Implementation Design for Eternia

This document consolidates the remaining capability gaps surfaced in:
- **Eternia: Aligned Personal Worlds as a Solution – Memo to Dr. Roman Yampolskiy** (2025) – establishes the personal-universe alignment goals, companion ecology expectations, and safety governance requirements.
- **Multi-Agent Orchestration System for Eternia** (2025) – outlines the autonomous agent workflow that should continuously triage, implement, and validate backlog items.
- **Eternia Project – Feasibility, Progress, and Funding Plan** (2025) – reinforces market readiness, investor expectations, and experiential polish required for a production-quality Eternia verse.
- **docs/tasks.md** – definitive backlog with completion signals.

The intent is to translate those sources into actionable design direction for features that remain unchecked.

## Guiding Principles
- Preserve the **personal-universe alignment guarantees**: every new feature must respect the Alignment Governor’s ability to pause, rollback, audit, and narratively justify safety interventions.
- Maintain **narrative immersion**: UI/UX additions should reinforce the “living world” illusion described in the memo (companions, rituals, symbolic governance) while keeping accessibility high.
- Enable **autonomous delivery loops**: design artifacts should be machine-readable and referenceable by MCP agents (Planner, Implementers, Reviewer, Security Sentry, Doc Writer) described in the orchestration memo.

## Outstanding Workstreams & Designs

### 1. Frontend Experience Cohesion (tasks 504, 505, 508, 509, 510)
- **Internationalization (504)**: introduce `i18next` with filesystem-backed locale JSON under `ui/src/locales/`. Wrap existing `t()` usages via a `useTranslation` hook, memoize through the existing context providers, and preload English as default. Add pipeline step to ensure untranslated keys fail CI.
- **Advanced State Management (505)**: layer Redux Toolkit on top of the existing Context API. Create feature slices for `zones`, `companions`, `governor`, and `session` to centralize websocket + REST data. Re-export selectors/hooks to avoid API churn for components already consuming contexts.
- **Accessibility & Keyboard Support (508)**: expand `ui/src/components/accessibility/` with focus trap utilities, ARIA annotations on key interactive regions (ZoneCanvas, dashboards), and a keyboard map stored in Redux for command palette integrations. Include automated tests via Cypress’ `tab` navigation helpers.
- **Dark Mode & Theming (509)**: extend the design tokens (SCSS/TS) to include semantic color roles. Persist theme preference in `localStorage`, synchronize with governor state for narrative events (e.g., ritual-induced ambient changes), and expose theme toggles in the control panel.
- **Offline Support (510)**: ship a Vite service worker (using Workbox) caching critical assets, zone manifests, and last-known simulation state snapshots. Ensure alignment checks invalidate caches when governor triggers rollbacks to prevent stale views.

### 2. Security Hardening (tasks 604–610)
- **Two-Factor Authentication (604)**: integrate TOTP using `pyotp` on the backend and a modal flow on UI. Store encrypted secrets in the existing `artifacts/` vault (rotate via governor events). Extend `/auth` routes with enrollment, verification, and backup-code issuance that respects governor shutdown states.
- **API Request Signing (605)**: adopt HMAC headers (`X-Eternia-Signature`, `X-Eternia-Timestamp`) computed with per-client keys. Reuse dependency injection container to register signer/verifier services. Document fallback for trusted internal components (governor loop, MCP agents).
- **Audit Logging (606)**: leverage `modules.logging_config` to emit structured JSON logs for security-sensitive actions (auth changes, zone mutations, governor overrides). Stream to Prometheus/Grafana via Loki or existing exporters and persist rotationally under `logs/security/`.
- **Secure Upload Handling (609)**: add FastAPI background task that scans uploads with ClamAV (containerized microservice). Enforce MIME-type whitelists, size caps, and quarantine flows; governor gets notified if artifacts violate policy.
- **Privacy-Aware Data Handling (610)**: implement anonymization utilities in `modules/data_privacy.py` to scrub PII when exporting analytics or logs. Ensure PDP compliance when personal companions mirror real individuals.

### 3. Data & Analytics Foundation (tasks 702–710)
- **Data Export (702)**: expose `/api/data/export` endpoints producing user-readable bundles (JSON + optional encrypted tar). Coordinate with governor to snapshot consistent states, reusing checkpoint pipeline.
- **Analytics Pipeline (703) & ML (710)**: Establish Kafka (or lightweight Redis Streams) ingestion from event bus. Feed a Dagster or Prefect workflow to compute engagement metrics, emotional resonance trends, and predictive models for companion interventions.
- **Anomaly Detection (704)**: extend `modules.monitoring` with unsupervised detectors (e.g., Twitter’s Seasonal Hybrid ESD) acting on cycle metrics. Tie alerts into governor pause hooks.
- **A/B Testing (705)**: create experiment registry in config settings, with Redux Toolkit integration on the UI. Govern exposure through alignment policies to avoid disruptive narratives.
- **Validation Layer (706)**: implement pydantic `BaseModel` schemas for all UI payloads and auto-generate TypeScript types via `pydantic2ts`. Add client interceptors that enforce schema adherence before dispatching mutations.
- **Data Warehousing (707) & Lineage (709)**: provision DuckDB/Parquet lake in `artifacts/datawarehouse/` for on-device dev, with Terraform modules for cloud warehouses. Track lineage using OpenLineage events emitted from ETL jobs.
- **Real-Time Dashboards (708)**: build Grafana dashboards (zones, emotion metrics, governor interventions) and embed snapshots within the UI monitoring section.

### 4. Immersive World Interface & Embodied Simulation
- **3D/Spatial World UI**: deliver an interactive “World Builder” interface surfaced in the React app (or companion desktop client) that mirrors live simulation state. Use WebGL/Three.js to render zones, companions, rituals, and symbolic modifiers in situ. Synchronize with backend via WebSocket streams; highlight governor interventions (pauses, rollbacks) with cinematic overlays. Allow users to sculpt terrain, adjust physics toggles, and spawn narrative events using drag-and-drop components aligned with the memo’s symbolic law cues.
- **Embodied Companion Movement**: extend simulation APIs beyond zone switching. Introduce pathfinding and locomotion primitives (grid- or navmesh-based) so companions can traverse coordinates, interact with objects, and perform rituals spatially. Persist movement intents in state tracker, propagate updates to UI, and ensure governor can veto physically unsafe trajectories.
- **Holographic Storytelling Layer**: inspired by the feasibility plan’s emphasis on experiential polish, add narrative timelines, memory galleries, and funding-demo friendly scenarios that demonstrate value to stakeholders. Provide recorded “journeys” exportable as pitch material.

### 5. Conversational Convergence & Co-Learning
- **Unified Communication Hub**: build a bi-directional chat system connecting the user, autonomous agents (Planner, Implementers, Companions), and optional human collaborators. House it in the UI as a “Mission Control Console.” Route messages through a new `modules.conversation_bus` with persistence, rate limiting, and alignment checks. Support plaintext, structured commands, and file drops.
- **AI-Driven Replies & Training Loop**: plug large language model responders into the hub (local or API-backed). Conversations should feed the companion training pipeline and Planner retrospectives—store transcripts in `artifacts/conversations/` for supervised fine-tuning and RLHF. Tag each utterance with context (zone, emotional state, governor status) so agents can learn situational awareness.
- **Consent & Privacy Controls**: surface toggles for what conversations may be used for training, in line with feasibility plan’s trust requirements. Governor audits conversation flows and can redact sensitive events before logs reach MCP agents or analytics.
- **Real-Time Presence Indicators**: show avatar pings and movement trails in the world UI, allowing users to follow agents or “teleport” their point-of-view to companions mid-mission, making collaboration feel embodied rather than abstract.

### 6. Autonomic Development Enablement
- **MCP Integration**: implement `scripts/mcp/` orchestration described in the multi-agent memo. Provide YAML task manifests referencing docs/tasks.md IDs, plus sandbox policies for agents to interact safely with governor APIs.
- **Agent Tooling Hooks**: expose read/write APIs for agents (Planner, Implementers, Security Sentry, Doc Writer). Document boundaries in `docs/mcp.md` and ensure governor can revoke agent sessions if anomalies occur.

## Implementation Roadmap
1. **Security Hardening** – prerequisites for MCP automation and data exports; reduces attack surface before broader exposure.
2. **Validation & Internationalization** – enabling consistent UX and compliance for global users.
3. **Advanced State & Offline UX** – ensures narrative continuity even in degraded connectivity scenarios.
4. **World Interface & Conversation Layer** – ship immersive tooling and communication hub to satisfy feasibility/funding demos and unlock co-creative experiences.
5. **Analytics & ML Stack** – unlock adaptive storytelling, anomaly detection, and telemetry loops described in the memo.
6. **MCP Automation** – once foundations are stable, empower autonomous agents to close remaining backlog items.

Each milestone should end with:
- README and `docs/` updates accessible to human and MCP agents.
- New automated tests (pytest, Cypress, Workbox integration tests, security scans) to maintain guardrails.
- Governor policy reviews to ensure new capabilities cannot bypass symbolic law enforcement.

## Acceptance Metric Examples
- Two-factor enrollment success path covered by integration tests and simulated governor shutdown scenario.
- 95%+ component coverage for keyboard navigation flows with Cypress.
- <1% cache incoherence incidents after offline mode; verified via chaos experiments.
- Analytics pipeline able to replay 24h of event backlog without data loss; lineage metadata recorded for every DAG run.
- Conversation hub maintains <150ms mean latency for AI responses while governor filters remain effective.
- World UI renders at 60fps on target hardware, with movement updates synchronized within 250ms end-to-end.

This design provides the scaffolding required before tackling the remaining unchecked tasks in `docs/tasks.md`, keeping Eternia aligned with its personal-universe mandate while readying the project for autonomous agent-driven execution.
