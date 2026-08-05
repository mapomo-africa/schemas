# schemas

**The Mapomo output contract.** Entity registry, observation, estimate, unit
cost, provenance, confidence.

This is the most important repository in the project. Everything depends on it;
it depends on nothing. It is what makes four separate tools one system, and what
lets a figure produced in Dakar be read, checked and compared in Nairobi.

Version **0.1**. Published before the Lab, deliberately, so that four build teams
work against one contract instead of producing four incompatible formats. See
[ADR 0005](https://github.com/mapomo-africa/mapomo/blob/main/decisions/0005-schemas-are-the-contract.md).

## The documents

| Schema | What it represents |
|---|---|
| [`entity`](schema/entity.schema.json) | An actor: candidate, party, coalition, third party, broadcaster, vendor |
| [`observation`](schema/observation.schema.json) | One counted trace of campaign activity, with no money attached |
| [`unit-cost`](schema/unit-cost.schema.json) | What one unit of a trace costs, in one country, at one time |
| [`estimate`](schema/estimate.schema.json) | A monetary estimate with its interval, coverage and comparison to declared finance |
| [`provenance`](schema/provenance.schema.json) | Where a record came from and what was done to it |
| [`confidence`](schema/confidence.schema.json) | How much weight a record can bear, and why |
| [`common`](schema/common.schema.json) | Shared building blocks: money, intervals, time windows, places, quantities |

## The shape of the pipeline

```
observation  ──┐
               ├──> estimate ──> comparison with declared finance
unit-cost   ───┘
```

Observations carry no money. Pricing happens at estimation time using unit costs,
so that a price correction never requires recollecting the field, and so that the
same observations can be repriced when better cost data arrives.

## Four design decisions worth knowing before you read the files

**Money is a string, not a number.** `{"amount": "48000.00", "currency": "ZAR"}`.
Binary floating point loses cents at scale, and these figures get aggregated,
converted and republished. A bare number with an implied currency is never
accepted anywhere in the contract.

**Nothing is published without an interval.** `estimate.value` is a
`moneyInterval`, never a point. A single number carries a claim of precision the
method does not support, and it is the form in which an estimate gets quoted
badly.

**Uncertainty and evidence strength are separate fields.** `confidence` describes
how good the evidence is; the interval describes how wide the number is. A
precisely counted figure from one unverified source is a different object from a
roughly counted one confirmed three ways, and one combined score would hide
exactly what a reader needs.

**Names live in the registry, never in the records.** Observations and estimates
reference entities by identifier. The sensitive layer is in one place, versioned,
publishable on its own schedule. In this repository every entity label is
fictional, and CI rejects examples where it is not.

## Validating

```bash
pip install jsonschema
python3 tools/validate.py
```

The validator checks every example against its schema and additionally enforces
what a JSON Schema cannot express: fictional labels only, no credential-shaped
strings, provenance present with a source. It is the same script CI runs, so a
green local run means a green pull request.

## Versioning

The version lives in every document as `schemaVersion` and in the `$id` of every
schema.

| Change | Version effect |
|---|---|
| New optional property, new enum member, clarified description | **Minor.** `0.1` to `0.2`. Existing documents stay valid. |
| New required property, removed or narrowed property, removed enum member, changed semantics of an existing field | **Major.** `0.x` to `1.0`. Existing documents become invalid. |

A major version requires an ADR in
[`mapomo-africa/decisions`](https://github.com/mapomo-africa/mapomo/tree/main/decisions), a
migration note in [`MIGRATIONS.md`](MIGRATIONS.md), and, from October 2026,
technical committee approval.

While at `0.x`, breaking changes are possible and will be announced. From `1.0`,
after the first full deployment has taught us what the contract got wrong, the
guarantee hardens.

## Using these schemas

The schemas are plain JSON Schema 2020-12 and work with any standard validator.
`$ref` is by bare filename, so keep `schema/` intact when vendoring.

Generated clients for Python and TypeScript ship alongside `core` on the
`mapomo-*` namespaces. They are a convenience; the JSON Schema files are the
contract.

## License

Apache-2.0. Chosen so that transparency platforms, electoral commissions and
newsroom data teams can embed the contract without a trip to their legal
department, with an explicit patent grant. See
[LICENSING.md](https://github.com/mapomo-africa/mapomo/blob/main/LICENSING.md).

## Contributing

Read [CONTRIBUTING](https://github.com/mapomo-africa/.github/blob/main/CONTRIBUTING.md).
Changes here are breaking changes for every downstream repository, so they need an
ADR first, and a pull request second.
