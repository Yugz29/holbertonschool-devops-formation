# Merge Conflict Resolution

## Context

Two feature branches were created from the same `main` commit and both
modified `config.yml`:

| Branch | Change | Lines touched |
|---|---|---|
| `feature/scale-up` | scale to 4 replicas, bump version to 1.1.0 | `version`, `replicas` |
| `feature/dark-mode` | enable dark mode, bump version to 2.0.0 | `version`, `feature_dark_mode` |

Merging `feature/dark-mode` into `feature/scale-up` produced:

```
Auto-merging config.yml
CONFLICT (content): Merge conflict in config.yml
Automatic merge failed; fix conflicts and then commit the result.
```

## Which line was in conflict

Only **one** line was in conflict: `version`.

```yaml
<<<<<<< HEAD
version: 1.1.0
=======
version: 2.0.0
>>>>>>> feature/dark-mode
```

- `HEAD` (the branch we are on, `feature/scale-up`) wanted `1.1.0`.
- `feature/dark-mode` (the branch being merged) wanted `2.0.0`.

## Why that line, and not the others

Git compares each branch against their common ancestor (the merge base).
For every line, it asks: *who changed it since the base?*

| Line | Base | scale-up | dark-mode | Result |
|---|---|---|---|---|
| `version` | `1.0.0` | `1.1.0` | `2.0.0` | **conflict**: both branches changed it, differently |
| `replicas` | `2` | `4` | `2` (untouched) | auto-merged to `4` |
| `feature_dark_mode` | `false` | `false` (untouched) | `true` | auto-merged to `true` |
| all other lines | unchanged | unchanged | unchanged | kept as is |

`replicas` and `feature_dark_mode` were merged automatically because only
**one** side changed each of them. Git can safely take the side that
changed and there is nothing to decide.

`version` was changed by **both** sides to **different** values. Git has
no way to know which one is right, so it stops and hands the decision to
a human. A conflict is not an error, it is Git refusing to guess.

Key takeaway: a conflict happens only when two branches modify the
**same lines** in different ways. Editing the same file is not enough to
cause one.

## My choice

I kept the `2.0.0` version and removed the three conflict markers.

Reasoning:

- Dark mode is a user-facing feature, which justifies a major bump
  (`2.0.0`) more than a replica count change (`1.1.0`).
- The merged result contains **both** changes, so the final version must
  be at least as high as the highest one requested. `2.0.0` covers both.
- The two auto-merged lines were kept untouched, as they already reflected
  both features.

Final `config.yml`:

```yaml
app: monservice
environment: production
version: 2.0.0
description: service principal
replicas: 4
max_connections: 100
feature_dark_mode: true
log_level: info
```

Steps used:

```bash
git merge feature/dark-mode        # conflict on config.yml
# edit config.yml: keep "version: 2.0.0", delete <<<<<<< ======= >>>>>>>
git add config.yml                 # mark the conflict as resolved
git commit                         # complete the merge
```

## Why smaller, focused changes reduce merge conflicts

- **Less surface area.** A small change touches few lines. The probability
  that someone else touched the *same* lines in the meantime drops with
  every line you do not modify.
- **Shorter lifetime.** A focused branch is merged in hours or days, not
  weeks. The less time a branch lives, the less `main` drifts away from
  it, and the less there is to reconcile.
- **One concern per change.** Here, the conflict came from a line
  (`version`) that neither feature really owned. A version bump is a
  separate concern and should be its own commit, ideally done once at
  release time. Mixing it into two feature branches guaranteed a clash.
- **Easier to resolve when it happens.** A conflict in a 5-line change is
  understood in seconds. A conflict in a 500-line refactor requires
  re-reading the whole intent of both sides.
- **Easier to review.** Small PRs get reviewed and merged faster, which
  again shortens branch lifetime and feeds back into fewer conflicts.

In short: merge often, keep branches small, and keep unrelated changes
(like version bumps) out of feature branches.
