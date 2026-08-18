# Migrations

One entry per version change, newest first. Every entry states what changed, why,
what a consumer must do, and what happens to documents already published under
the previous version.

An entry is written when the change is merged, not afterwards from memory.

## 0.1.0 (2026-08-18)

Initial contract. Nothing to migrate from.

Eight documents: `entity`, `observation`, `field-observation`, `unit-cost`,
`estimate`, `provenance`, `confidence`, `common`. Identifier and alias rules in
`ALIASES.md`.

Frozen and published ahead of the Mapomo Lab, September 2026, so that all build
teams work against one shape. Expect corrections after the first full deployment;
those will appear here.

<!--
Template for the next entry:

## 0.2 (YYYY-MM-DD)

**Kind:** minor, additive. Documents valid under 0.1 remain valid.

**What changed**
- ...

**Why**
- ... link the ADR

**What consumers must do**
- ...

**Effect on published documents**
- ... state plainly whether any published estimate is affected
-->
