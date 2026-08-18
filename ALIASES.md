# Identifiers and alias rules

The entity registry is the join key of the whole system. Everything else in this
contract references entities by identifier; if two records about the same actor
resolve to two identifiers, every total downstream is wrong in a way no
validation catches.

This file is normative. `core.entities` implements it, and a country registry that
disagrees with it is a bug in the registry.

## Identifier form

```
<country>-ent-<type>-<slug>
```

`sn-ent-party-b`, `ng-ent-candidate-a`, `za-ent-vendor-outdoor-c`.

Rules that do not bend:

1. **An identifier is permanent.** A party that renames itself keeps its
   identifier and gains an alias. Renaming an identifier orphans every
   observation collected under it.
2. **An identifier is opaque.** It is not parsed for meaning by any consumer, and
   the slug is not required to resemble the name. Slugs are fictional in this
   repository and in every fixture.
3. **One actor, one identifier, per country.** A party operating in two countries
   is two entities linked by `affiliated_with`. Election law, disclosure regimes
   and rate cards are national; a cross-border single entity would flatten all
   three.
4. **A coalition is an entity, not a shortcut.** Spending attributed to a
   coalition stays on the coalition and is never silently split across its
   members. The split is an analytical step with its own method note.

## Normalisation, applied before any comparison

In this order, always:

1. Unicode NFKC.
2. Casefold.
3. Strip diacritics **except** where the language marks a distinction that
   changes the word. Hausa hooked letters (ɓ, ɗ, ƙ) and Wolof ñ are preserved;
   French accents are stripped.
4. Collapse internal whitespace, strip punctuation used as separators (`.`, `-`,
   `/`), keep apostrophes inside words.
5. Drop honorifics and titles at the start of a string, from the country
   configuration list (`Alh.`, `Dr`, `Hon.`, `Chief`, `Sen.`, ...).
6. Expand nothing. Abbreviations are matched through the alias list, not by a
   guessing rule. The one exception: a string that normalises to single letters
   separated by spaces is also indexed without the spaces, so that `P.B.` and
   `PB` are the same key. Both forms occur in the same ad library, often in the
   same week.

Normalisation is for **matching only**. The stored label keeps its original form,
diacritics included. A registry that has lost the accents of a name has damaged
its own data.

## Resolution order

A candidate string from a collector resolves as follows, first hit wins:

| Order | Rule | Attribution basis it supports |
|---|---|---|
| 1 | Exact match on a platform handle or a disclaimer string in `matching` | `platform_declared` |
| 2 | Exact match on the normalised label | `explicit_branding` |
| 3 | Exact match on a normalised alias | `explicit_branding` |
| 4 | Regular expression in `matching.patterns` | `explicit_branding` |
| 5 | Fuzzy match at or above `minimumScore` | `contextual_inference` |
| 6 | No match | unresolved |

Anything in `matching.doNotMatch` fails immediately at every level, including
exact match. That list exists because the same wrong join otherwise reappears
every week.

**Unresolved is a state, not an error.** Unresolved strings are kept with their
count and reported as an unattributed pool. They are never dropped, never
attributed to the nearest plausible actor, and the size of the pool is published
next to the estimate — a large pool is a caveat the reader is entitled to.

**Fuzzy matches never enter a per-actor total without review.** Rule 5 produces a
queue, not a join, and everything it produces carries `contextual_inference`,
which alone cannot support a confidence grade above C.

## Aliases in practice

An alias earns its place from a source, not from imagination. Add one when it has
actually been seen in collected material, and record where. The recurring
categories:

- the acronym, with and without dots
- the local-language name where campaigning happens in it
- the transliteration used by the media of the country
- the two or three misspellings that recur in ad-library advertiser fields
- the former name, after a rename, with `since` on the relation

## Fictional in this repository

Every label, alias, pattern and handle committed here is fictional and CI rejects
examples where `label.isFictional` is not true. Real registries are country-scoped
deployment data, published on their own schedule under their own review. That
separation is what lets this repository be public.
