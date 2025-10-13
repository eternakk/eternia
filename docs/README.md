# Eternia Documentation Index

This directory captures the working knowledge for Eternia’s simulation stack, automation runway, and operational guardrails. Use the categorized links below to find the right reference before you change code, expand automation, or schedule a release. Unless noted otherwise, every item maps back to work tracked in `docs/tasks.md` or `docs/implementation_stories.md`.

> Tip: See `cleanup_docs.sh` for keeping generated data out of version control, and `create_docs_files.ipynb` for scripting bulk doc scaffolds.

## Orientation & Getting Started

- [Developer Onboarding](developer_onboarding.md) – Day-one setup, expectations, and checkpoints.
- [Environment Setup](environment_setup.md) – Tooling, virtualenv, Node, and optional Docker instructions.
- [Running the Server](running_the_server.md) – Launching the FastAPI service and simulation runners.
- [Docker Setup](docker_setup.md) – Container build, compose targets, and environment parity.
- [README](../README.md) – High-level project overview and repo map.

## Strategy, Planning & Governance

- [Tasks](tasks.md) – Canonical backlog; every change should trace to an item here.
- [Implementation Stories](implementation_stories.md) – Story-level narratives that explain why work matters.
- [Issue Story Map](issue_story_map.json) – Machine-readable mapping from issues to stories/epics.
- [Pending Implementation Design](pending_implementation_design.md) – Open design decisions and blocking research.
- [Implementation Notes](implementation_notes.md) – Historical decisions, trade-offs, and follow-ups.
- [Agentic Orchestration Plan](agentic_orchestration_plan.md) – Planner/Test/Implementer/Security workflow contract.
- [Notes Epic A1 Integration](notes_epic_a1_integration.md) – Epic-specific alignment and rollout timelines.

## Architecture & System Design

- [Architecture (v1)](architecture.md), [Architecture v2](architecture_v2.md), [Architecture v3](architecture_v3.md) – Iterative system blueprints; prefer the latest version unless you are diffing history.
- [Module Map](module_map.md) – Component relationships and code hot spots.
- [State Management and Data Flow](state_management_and_data_flow.md) – Data lifecycles across modules and services.
- [Runtime Cycle](runtime_cycle.md) – Tick-by-tick loop for the governor and world builder.
- [Event System](event_system.md) – Event sourcing patterns and subscription flows.
- [Optimization Summary](optimization_summary.md) – Performance tuning backlog and completed wins.
- [Pydantic Compatibility Fix](pydantic_compatibility_fix.md) – Migration guide for Pydantic updates.

## Simulation Mechanics & World Building

- [World Builder Overview](../world_builder.py) – Code entry point; pair it with the docs below.
- [Companion Ecology](companion_ecology.md) – Behavioral loops and inter-companion dynamics.
- [Evolution Logic](evolution_logic.md) – Trait adaptation and mutation systems.
- [Symbolic Laws](symbolic_laws.md) – Narrative physics and ritual constraints.
- [Genesis Valley PCG](genesis_valley_pcg.md) – Procedural content generation notes for the launch biome.
- [Memory Integration](memory_integration.md) – Persistence model for agent experiences.
- [Art Pipeline Changelog](art_pipeline_changelog.md) – Visual asset evolution and backlog.

## Platform Services & Data

- [API Documentation](api_documentation.md) – REST/WebSocket/quantum endpoints and authentication flows.
- [Database](database.md) – Schema reference and migration hooks.
- [Migration Manager](migration_manager.md) – Yoyo-based workflow and safeguards.
- [Logging](logging.md) – Structured logging strategy and sinks.
- [Monitoring and Alerting](monitoring_and_alerting.md) – Metrics stack, alert routes, and dashboards.
- [CI/CD Pipeline](ci_cd_pipeline.md) – Automation flows for builds, tests, and deployments.
- [MCP Integration](mcp.md) – Machine Control Protocol touchpoints and configuration.

## Security, Safety & Governance

- [Governor](governor.md) & [Governor Events](governor_events.md) – Alignment controls and signal taxonomy.
- [Secure Coding Guidelines](secure_coding_guidelines.md) – Baseline engineering guardrails.
- [Security Improvements](security_improvements.md) – Hardening backlog and completed mitigations.
- [Security Scanning](security_scanning.md) – Current scanning pipeline and future enhancements.
- [Backup and Recovery](backup_and_recovery.md) – Canonical backup SOP (supersedes `backup_recovery.md`; keep both until all references migrate).
- [Backup Recovery (legacy)](backup_recovery.md) – Older checklist retained for historical context.

## Operations, Reliability & Runbooks

- [Release Management](release_management.md) – Branching, approvals, and rollout ceremonies.
- [Monitoring & Observability](monitoring_and_alerting.md) – Metrics, dashboards, and alert routing.
- [Logging](logging.md) – Log levels, sinks, and retention.
- Runbooks:
  - [Deployment](runbooks/deployment.md) – Step-by-step deploy playbook.
  - [Incident Response](runbooks/incident_response.md) – Triage, escalation, and recovery.
- [Backup & Recovery](backup_and_recovery.md) – See Security section for canonical guidance.
- [Art Pipeline Changelog](art_pipeline_changelog.md) – Included here for operational visibility into asset updates.

## Frontend & UX

- [UI Architecture](ui_architecture.md) – High-level structure of the Vite/React client.
- [UI Components](ui_components.md) – Canonical component inventory and usage.
- [UI Development Guidelines](ui_development_guidelines.md) – Standards for styling, testing, and linting.
- [UI Pending Tasks](ui_pending_tasks.md) – Frontend backlog and open questions.

## Quantum, Research & Experimental Systems

- [Quantum Overview](quantum_overview.md) – Conceptual model for quantum-inspired helpers.
- [Quantum Tasks](quantum_tasks.md) – Roadmap for quantum feature delivery.
- [Quantum Runtime Hooks](../modules/quantum_service.py) – Pair with the overview for implementation details.

## Logs, Notes & Glossaries

- [Dev Log](dev_log.md) – Rolling engineering journal and retro outcomes.
- [Glossary](glossary.md) – Terminology shared across engineering, narrative, and ops.
- [Structure Directory](../structure/) – Auto-generated code tree snapshots for quick spelunking.

## Utilities & Supporting Assets

- [Cleanup Docs Script](../cleanup_docs.sh) – Removes generated artifacts from `docs/`.
- [Create Docs Notebook](create_docs_files.ipynb) – Notebook helper for bulk doc creation.
- [Installed Packages](../installed_packages.txt) – Baseline tooling and CLI dependencies.

---

If you cannot find what you need, add a TODO to `docs/tasks.md` and open an issue tagged `agent:ready` so the automation pipeline can plan the update. Align any new documentation with the categories above to keep navigation consistent.
