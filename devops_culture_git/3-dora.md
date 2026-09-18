## Q1. Match each DORA metric to its definition

- **Deployment Frequency:** measures how often we deploy over time.
- **Lead Time for Changes:** measures the delay between the moment a commit or PR is pushed and its deployment to production.
- **Change Failure Rate:** measures the percentage of deployments that caused an incident.
- **Time to Restore / MTTR:** measures the time needed to restore the service back to normal after an incident.

## Q2. A team deploys once a quarter. Which metric is poor?

**Deployment Frequency.**

This metric measures how often an organization successfully deploys code changes. Deploying only once a quarter means the team has a low deployment frequency, so this metric is performing poorly.

## Q3. You shorten the time between merging a PR and shipping it to production. Which metric improves?

**Lead Time for Changes.**

This metric covers the whole interval between a commit being pushed and it running in production. The merge-to-production step is part of that interval, so shortening it directly reduces the total lead time.

A long lead time usually points to bottlenecks somewhere in the pipeline, such as automated tests, code review, or deployment.

## Q4. 1 deployment out of 4 causes an incident. Which metric is this, and is a high value good or bad?

This is the **Change Failure Rate**.

1 deployment out of 4 causes an incident, so the change failure rate is **25%**. A high value is bad because it means that a large proportion of deployments cause failures or require remediation.

## Q5. What does the acronym CALMS stand for?

CALMS stands for:

- **Culture**
- **Automation**
- **Lean**
- **Measurement**
- **Sharing**

## Q6. True or false: "Elite" teams deploy less often but in bigger batches. Justify your answer.

**False.**

High-performing teams deploy **more frequently**, usually with smaller changes. Smaller batches make deployments easier to test, review, and recover from if something goes wrong.

## Q7. Which practice improves MTTR the most?

**(b) Monitoring and alerting plus automated rollback.**

Fast detection and automated recovery help reduce the time needed to restore service after an incident.

## Q8. Among the 4 DORA metrics, which measure throughput and which measure stability?

### Throughput

- **Deployment Frequency**
- **Lead Time for Changes**

### Stability

- **Change Failure Rate**
- **Time to Restore / MTTR**

## Q9. Why do we run blameless post-mortems?

We run blameless post-mortems to understand why an incident happened and improve the system without focusing on blaming individuals.

The goal is to identify technical and organizational causes, learn from the incident, and prevent similar failures in the future.