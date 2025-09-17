# Incident Response Runbook

Last updated: 2025-09-17

Purpose: Provide a clear, repeatable process for triaging and resolving production incidents.

Severity Levels:
- SEV1: Total outage or critical data loss
- SEV2: Significant functionality impaired, high user impact
- SEV3: Degraded performance or minor feature outage

Immediate Actions:
1) Declare incident and assign roles
- Incident Commander (IC)
- Communications Lead
- Operations Lead
- Scribe

2) Stabilize
- [ ] Flip feature flags off for unstable subsystems
- [ ] Scale up resources if constrained
- [ ] Apply circuit breakers / rate limits as needed

3) Diagnose
- [ ] Check dashboards (metrics, traces, logs)
- [ ] Identify last deploy/change (git, CI) and roll back if needed
- [ ] Capture context (errors, request IDs, user reports)

4) Mitigate
- [ ] Rollback deployment or hotfix
- [ ] Throttle or isolate problematic components
- [ ] Restore from backups if data corruption detected

5) Communicate
- [ ] Update status channel every 15 minutes (SEV1/2)
- [ ] User-facing updates if applicable

6) Close & Learn
- [ ] Verify system health and clear alarms
- [ ] Post-incident review within 48 hours
- [ ] Create action items and owners

Artifacts & Tools:
- Logs: logs/*.log (API: logs/api_security.log, App: logs/eternia.log)
- Metrics: /metrics (Prometheus exporter)
- Backups: see modules/backup_manager and scripts/restore_backup.py
- Security headers: services/api/server.py

On-call Escalation:
- Primary: #eternia-oncall
- Secondary: #eternia-ops
- Eng Mgmt: #engineering
