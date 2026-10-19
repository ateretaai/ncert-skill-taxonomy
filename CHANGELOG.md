# Changelog

## [0.1.0] - 2026-10-18

First draft. **AI-drafted, not teacher-reviewed.**

### Added
- 503 Marble Mathematics topics (ids unchanged, `origin: marble`) and their 985 maths-to-maths edges.
- NCERT alignment of every Marble topic to Classes 1-8 chapters (706 links: 309 exact, 397 inferred), with earliest-class `grade`.
- 31 new topics (`ncm_0001`-`ncm_0031`) for NCERT content Marble lacked: lakh/crore, Indian vs international number names, number bases, figurate numbers, Virahanka-Fibonacci, digit puzzles, parity, magic squares, cryptarithms, divisibility tests, co-primes, prime factorisation, integer addition/subtraction, exponent rules, algebraic identities, triangle inequality, triangle constructions, Baudhayana triples, tilings, fractals, views of solids, rotational symmetry, maps, Indian money, profit/loss/discount, inverse proportion, winning strategies in games, Indian contributions to mathematics, compass constructions, multi-term ratios, estimating large quantities. Plus 65 prerequisite edges.
- `ncert-curriculum.json` (10 books, 106 chapters, verified) and `ncf-competencies.json` (63 competencies, 16 goals; codes verified, text paraphrased).
- Indian localisation notes; localised text for 8 currency/units topics.
- `scripts/validate.py`, `scripts/coverage.py`, `scripts/build/`, `docs/coverage.md`, `docs/sources.md`.

### Removed (relative to Marble)
- Non-Mathematics subjects; 66 cross-subject edges (`docs/dropped-edges.json`); Marble's `curriculum-standards.json` and `clusters.json` are not redistributed.
