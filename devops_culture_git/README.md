# DevOps Culture & Git Collaboration

## About

This project focuses on the mindset behind DevOps: understanding *why*
teams work the way they do before diving into Docker, containers, and
pipelines. It covers the CALMS framework, DORA metrics, PR-based
workflows, conventional commits, merge conflict resolution, and
blameless post-mortems.

## Learning Objectives

- What DevOps is, and the collaboration problem it solves
- CALMS framework and the DevOps loop
- The 4 DORA metrics: throughput vs. stability
- Pull Request-based workflow and why code review matters
- Conventional commits and why we standardize commit messages
- Why merge conflicts happen and how to resolve them cleanly
- Blameless post-mortems: why we don't look for a culprit

## Files

| File | Description |
|---|---|
| `0-environment.md` | Local environment setup verification (Docker, Git, SSH, Node.js). |
| `config.yml` | Resolved merge conflict between `feature/scale-up` and `feature/dark-mode`. |
| `RESOLUTION.md` | Explanation of the conflict, its cause, the resolution choice and why small changes reduce conflicts. |
