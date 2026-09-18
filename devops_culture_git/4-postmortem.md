# PixelCart Friday Night Incident Post-Mortem

## 1. Factual timeline

- **Friday, 5:40 pm — Deployment started:** A checkout fix was deployed manually to production. The process required connecting to the production server over SSH, copying files manually, and editing configuration directly on the server.
- **Friday, 5:52 pm — Incident occurred:** A typo was introduced in the database URL configuration. Because there was no production-like test environment, the issue was not detected before deployment.
- **Friday, 6:05 pm — No active monitoring:** The deployment was left running without automated monitoring or alerting.
- **Friday, 8:30 pm — First external signal:** A customer reported that checkout was failing on social media.
- **Saturday, 9:15 am — Incident detected by the team:** The complaints were discovered. The person investigating did not have server access and there was no deployment history or documented record of the change.
- **Saturday, 11:40 am — Service restored:** The configuration error was identified and corrected manually.

The checkout service was unavailable for approximately **15 hours**.

## 2. Systemic causes

The incident was caused by several weaknesses in the deployment and operational process:

- **Manual production deployment:** Files and configuration were changed directly on the production server, increasing the risk of human error.
- **No production-like test environment:** The change could not be validated under conditions close to production before deployment.
- **No automated validation:** There were no automated tests or checks capable of detecting the invalid database configuration before or immediately after deployment.
- **No monitoring or alerting:** The team was not automatically informed when checkout stopped working.
- **No deployment traceability:** There was no reliable record of what had been deployed or changed.
- **No simple rollback mechanism:** Restoring the previous working configuration required manual investigation and intervention.
- **Insufficient incident access and on-call process:** The person who discovered the incident could not directly access the system needed to investigate and restore service.

The incident was therefore not the result of one individual mistake, but of a system that allowed a configuration error to reach production and remain undetected for many hours.

## 3. Priority actions

### Priority 1 — Introduce an automated deployment pipeline

Deployments should go through a CI/CD pipeline instead of being performed manually over SSH.

The pipeline should:
- install dependencies;
- run automated tests;
- validate configuration;
- deploy changes consistently;
- keep a record of each deployment.

This would reduce manual errors and make deployments reproducible and traceable.

### Priority 2 — Add monitoring and automated alerting

PixelCart should monitor critical functions such as checkout availability and database connectivity.

Alerts should automatically notify the on-call team when checkout fails.

This is a priority because the incident remained undetected internally for more than 15 hours. Faster detection would significantly reduce the duration of future incidents.

### Priority 3 — Implement versioned deployments and automated rollback

Each deployment should be versioned and the previous working version should be easy to restore.

If monitoring detects a failed deployment, the team should be able to quickly roll back to the last known working version.

This would reduce recovery time and avoid having to investigate and repair production manually under pressure.

## 4. Impact on DORA metrics

### Change Failure Rate

The manual deployment process, lack of automated tests, and direct production configuration changes increase the probability that a deployment causes an incident.

These weaknesses therefore degrade the **Change Failure Rate**.

### Time to Restore Service / MTTR

The absence of monitoring, limited operational access, lack of deployment history, and absence of an automated rollback mechanism made recovery much slower.

These problems directly degrade **Time to Restore Service / MTTR**.

### Lead Time for Changes

A manual deployment process involving SSH access, file copying, and direct configuration changes makes delivering changes slower and less predictable.

An automated CI/CD pipeline would reduce the **Lead Time for Changes** by making deployments repeatable and faster.

### Deployment Frequency

Because deployments are manual, risky, and difficult to recover from, the team is likely to deploy less frequently.

Automating the deployment process and reducing deployment risk would make smaller and more frequent releases easier, improving **Deployment Frequency**.
