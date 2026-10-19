# ncert-skill-taxonomy

An open, machine-readable map of **what Indian school students learn in mathematics, Classes 1-8**: fine-grained skills ("micro-topics"), the prerequisite links between them, and where each one appears in the current **NCERT textbooks** and the **NCF-SE 2023** competencies.

It is a derivative of the [Marble Skill Taxonomy](https://github.com/withmarbleapp/os-taxonomy) (Mathematics subset), refined and re-aligned for the Indian curriculum.

> [!IMPORTANT]
> **This dataset is AI-drafted and has not yet been reviewed by teachers.** It is not an official NCERT or CBSE publication, and it is not endorsed by NCERT, CBSE, or the Ministry of Education.
>
> **Version** `0.1.0`. Every NCERT alignment, competency link, new topic, and new prerequisite edge is a draft (`reviewStatus: "ai-draft"`). Do not use it for grading, placement, or anything high-stakes until a qualified maths teacher has reviewed it. Weak spots are listed in [docs/coverage.md](docs/coverage.md). Book titles and chapter names are cited only to say where a skill is taught.
>
> **Educators:** please report errors by [opening a GitHub issue](https://github.com/ateretaai/ncert-skill-taxonomy/issues).

Maintained by [Takhtee](https://takhtee.com). The taxonomy is used as free curriculum material in the Takhtee platform.

## What's inside

| | Count |
|---|---:|
| Topics | **534** (503 from Marble + 31 new `ncm_` topics for NCERT content Marble lacks) |
| Marble topics aligned to at least one NCERT chapter | 421 / 503 |
| Cross-cutting process skills (aligned via NCF competencies) | 48 |
| Marble topics with no NCERT Classes 1-8 home (flagged, kept) | 44 |
| Prerequisite edges | **1,050** (985 Marble maths-to-maths, unchanged + 65 new); acyclic |
| NCERT books / chapters | 10 books / 106 chapters (Classes 1-8, 2026-27 editions) |
| Topic-chapter alignments | 706 (309 `exact`, 397 `inferred`) |
| NCF-SE 2023 maths competencies | 63 (Foundational 14, Preparatory 19, Middle 30) + 16 curricular goals |

Books covered (all verified from NCERT's official prelims PDFs):

| Class | Book | Chapters |
|---|---|---:|
| 1 | *Joyful Mathematics* | 13 |
| 2 | *Joyful Mathematics* | 11 |
| 3 | *Maths Mela* | 14 |
| 4 | *Maths Mela* | 14 |
| 5 | *Maths Mela* | 15 |
| 6 | *Ganita Prakash* | 10 |
| 7 | *Ganita Prakash* Part I + Part II | 8 + 7 |
| 8 | *Ganita Prakash* Part I + Part II | 7 + 7 |

## Files

| File | What it holds |
|---|---|
| `data/topics.json` | Topics (graph nodes). Marble-compatible fields plus `origin`, `reviewStatus`, `grade`, `ncertStatus`, `localisation`. |
| `data/dependencies.json` | Prerequisite edges: `topicId` depends on `prerequisiteId`, `hard`/`soft`, with a reason and `origin`. |
| `data/ncert-alignments.json` | One record per topic: NCERT chapters (with `exact`/`inferred` confidence), NCF-SE competency codes, notes. |
| `data/ncert-curriculum.json` | NCERT books (code, ISBN, edition, source URL) and chapters for Classes 1-8. |
| `data/ncf-competencies.json` | NCF-SE 2023 maths curricular goals and competency codes with **paraphrased** summaries and page references. |
| `manifest.json` | Counts and SHA-256 checksums. |
| `docs/coverage.md` | Per class / per chapter coverage, gaps, low-confidence items. |
| `docs/sources.md` | Every NCERT PDF consulted, with URL and checksum. |
| `docs/dropped-edges.json` | The 66 Marble edges to non-maths topics that were dropped. |
| `scripts/validate.py` | Stdlib-only validator (structure, enums, referential integrity, cycles, grades, checksums). |
| `scripts/coverage.py` | Regenerates `docs/coverage.md`. |
| `scripts/build/` | The build script and the editor mapping tables it reads (`map*.txt`, `crosscut.txt`, `*_data.py`). |

## Quick start

```bash
python3 scripts/validate.py        # -> VALIDATION PASSED
STRICT_REVIEW=1 python3 scripts/validate.py   # fails until every record is teacher-reviewed
```

```python
import json
topics = {t["id"]: t for t in json.load(open("data/topics.json"))["topics"]}
deps   = json.load(open("data/dependencies.json"))["dependencies"]
align  = {a["topicId"]: a for a in json.load(open("data/ncert-alignments.json"))["alignments"]}

# Everything taught in Ganita Prakash Class 7 Part I, Chapter 3 ("A Peek Beyond the Point")
ch = "ncert:GP7-1:3"
in_ch = [t for t, a in align.items() if any(c["chapterId"] == ch for c in a["chapters"])]
# Direct prerequisites of the first one
pre = [topics[d["prerequisiteId"]]["name"] for d in deps if d["topicId"] == in_ch[0]]
```

Rebuild from Marble (needs a Marble checkout next to this folder, or set `MARBLE_DATA`):

```bash
MARBLE_DATA=../os-taxonomy/data python3 scripts/build/build.py && python3 scripts/validate.py && python3 scripts/coverage.py
```

## Schema

### Topic (`data/topics.json` → `topics[]`)

Marble fields are kept as-is: `id`, `type`, `subject`, `domain`, `name`, `description`, `ageRangeStart`, `ageRangeEnd`, `centrality`, `evidence`, `assessmentPrompt` (with a `{{name}}` placeholder), `standards`.

- `standards` holds Marble's original US/UK codes (`ccss-math:…`, `uk-nc-2013:…`) as identifiers only. Their text lives in Marble's `curriculum-standards.json`, which is **not** redistributed here (see ATTRIBUTION.md).
- `centrality` is Marble's value for Marble topics and `null` for new topics.

Added fields:

| Field | Values |
|---|---|
| `origin` | `marble` (id unchanged) or `ncert-new` (`ncm_NNNN`) |
| `reviewStatus` | `ai-draft` (all in v0.1) or `teacher-reviewed` |
| `grade` | Earliest NCERT class (1-8) with an aligned chapter; `null` if no NCERT home |
| `gradeSource` | `ncert-alignment`, or `age-estimate` (cross-cutting skills with no chapter: Marble age minus 5, minimum 1), or `null` |
| `ncertStatus` | `mapped`, `cross-cutting`, `no-ncert-home` |
| `noNcertHomeReason` | `not-in-ncert-classes-1-8`, `not-applicable-in-india`, `representation-not-used-in-ncert`, `not-found` |
| `localisation` | `notes[]` and optional `localised{name, description, evidence, assessmentPrompt}` Indian versions (₹, metric units, lakh/crore). The original Marble text is left untouched. |

### Alignment (`data/ncert-alignments.json` → `alignments[]`)

```json
{
  "topicId": "mt_…",
  "ncertStatus": "mapped",
  "grade": 7,
  "gradeSource": "ncert-alignment",
  "chapters": [
    {"chapterId": "ncert:GP7-1:3", "book": "GP7-1", "class": 7, "part": 1, "chapter": 3,
     "chapterName": "A Peek Beyond the Point", "confidence": "exact", "note": null}
  ],
  "competencies": [{"id": "ncfse-2023:MS.C-1.6", "confidence": "inferred", "basis": "chapter-domain-heuristic"}],
  "note": "…",
  "reviewStatus": "ai-draft"
}
```

- Chapter ids are `ncert:<BOOK>:<n>`. Book keys: `JM1`, `JM2`, `MM3`, `MM4`, `MM5`, `GP6`, `GP7-1`, `GP7-2`, `GP8-1`, `GP8-2`. Part II books restart chapter numbering at 1, so always use the book key.
- `exact`: the chapter title, a section heading or strong keyword evidence in the official chapter PDF names the concept. `inferred`: editor judgement from the chapter's theme.
- Competency `basis`: `chapter-domain-heuristic` = codes the editors assigned to the chapter, filtered by the topic's domain; `editor` = hand-assigned (cross-cutting skills).

### Competency (`data/ncf-competencies.json` → `competencies[]`)

`id` like `ncfse-2023:MS.C-1.1` (stage `FS`/`PS`/`MS` + official code), `cg`, `summary` (**our paraphrase**, not NCERT wording), `source.section`, `source.printedPages`.

### Dependency

Same as Marble (`topicId`, `prerequisiteId`, `strength`, `reason`) plus `origin` and, for new edges, `reviewStatus`.

## How it was made (short)

1. Book lists, chapter titles, ISBNs and editions were read from NCERT's official prelims PDFs; NCF-SE codes from the official NCF-SE 2023 PDF.
2. All 106 chapter PDFs were downloaded and keyword-searched (and section headings extracted for Classes 6-8) to see what each chapter covers.
3. An AI assistant then went through all 503 Marble maths topics and assigned chapters by hand-written judgement, guided by that evidence (no automated text matching decided the mapping). It drafted 31 new topics for NCERT content Marble lacks, with prerequisite edges into Marble topics.
4. Scripts assembled, validated and reported. Details and caveats: [PROVENANCE.md](PROVENANCE.md).

## Licence

The source of the mathematics skills is the [Marble Skill Taxonomy](https://github.com/withmarbleapp/os-taxonomy) (v1, Mathematics subset; © Generative Spark, Inc.). This dataset keeps Marble's share-alike terms. The summary below matches [LICENSE](LICENSE), [LICENSE-CONTENT](LICENSE-CONTENT), and [ATTRIBUTION.md](ATTRIBUTION.md):

- **Database** (structure, ids, relationships, alignments): [Open Database License (ODbL) 1.0](LICENSE).
- **Text content** (topic names, descriptions, evidence, prompts, edge reasons, notes, and summaries — Marble's and ours): [Creative Commons Attribution-ShareAlike 4.0](LICENSE-CONTENT) (CC BY-SA 4.0).
- **Not covered by these licences:** NCERT and NCF-SE material. This repository includes only titles, codes, and factual metadata, plus our own paraphrases. See [ATTRIBUTION.md](ATTRIBUTION.md).

You can build a commercial app on this data without open-sourcing the app. If you publish an improved version of the **dataset**, it must stay under ODbL / CC BY-SA, with attribution.

### Attribution (required)

> ncert-skill-taxonomy v0.1 · derived from the Marble Skill Taxonomy (v1) · © Generative Spark, Inc. (Marble) · https://withmarble.com · licensed under ODbL 1.0 (database) and CC BY-SA 4.0 (content). NCERT/NCF-SE references are factual citations; not endorsed by NCERT.

The upstream commit, the list of changes from Marble, and the boundary with NCERT text are in [ATTRIBUTION.md](ATTRIBUTION.md). To cite the dataset, use [CITATION.cff](CITATION.cff).

## Contributing

Teachers and curriculum specialists can correct this draft.

- **Report an error** by [opening a GitHub issue](https://github.com/ateretaai/ncert-skill-taxonomy/issues). Name the topic id, chapter, or competency, and say what should change.
- **Propose a correction** in a pull request. In the description, say what you changed and why (a textbook page or an NCF-SE reference helps).
- Before submitting, run `python3 scripts/validate.py`. It must print `VALIDATION PASSED`.
