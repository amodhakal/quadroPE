# Failure Manual / Incident Report (Template)

> This document is a template.
> Replace all placeholder values (for example: `<DATE/TIME>`, `<X>`, `<sha>`, `<metric>`) before using it for a real incident.

## How to use this template

1. Copy this file for each incident (for example, `incident-2026-04-04-db-timeout.md`).
1. Fill every placeholder with concrete values from logs, dashboards, and deploy history.
1. Keep the timeline in chronological order and include exact UTC times when possible.
1. Add follow-up action owners and due dates.

## Incident summary

On <DATE/TIME>, quadroPE returned errors for users due to <root cause – e.g., exhausted DB connections, bad deploy, misconfiguration>. The outage lasted approximately <X minutes>.

## Impact

- Affected environment: (staging / production)
- User-visible symptoms: timeouts / 5xxs on <endpoints>.
- Scope: <percentage or rough count of requests affected>.

## Timeline

- <t0> – Problem detected (alert / dashboard / manual report).
- <t1> – On-call acknowledged.
- <t2> – First mitigation step (rollback / restart / config change).
- <t3> – Service fully recovered.

## Root cause

The underlying cause was <technical reason – e.g., new release introduced a regression in DB access, causing connection leaks and timeouts under load>.

## Mitigation and resolution

- Rolled back to commit `<sha>`.
- Restarted application processes.
- Verified `/health` returned `{"status": "ok"}` and error rate returned to baseline.

## Lessons learned

- What worked well: e.g., health check and logs quickly pointed to DB.
- What failed: e.g., missing limit on open connections, no alert on queue depth.

## Follow-up actions

- [ ] Add test / check to prevent similar regression.
- [ ] Add dashboard panel for <metric>.
- [ ] Add an alert at threshold <X>.
