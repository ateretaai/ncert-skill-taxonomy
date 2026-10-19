# Provenance

How every part of v0.1 was produced, and how sure we are about it. All retrieval happened on **2026-10-18 (IST)**.

## Status in one line

**AI-drafted, needs teacher review.** Facts about books and NCF-SE codes were checked against official PDFs. The *mapping* (which topic belongs to which chapter and competency), the new topics and the new edges are AI judgements that no teacher has reviewed.

## 1. Verified facts (checked against official NCERT PDFs)

| Fact | Source | Status |
|---|---|---|
| Class 1 *Joyful Mathematics*: 13 chapters; NCERT code 0124; ISBN 978-93-5292-505-6; first edition May 2023; "Reprint 2026-27" | `aejm1ps.pdf` prelims | verified |
| Class 2 *Joyful Mathematics*: 11 chapters; 0224; ISBN 978-93-5292-426-4; first edition May 2023; Reprint 2026-27 | `bejm1ps.pdf` | verified |
| Class 3 *Maths Mela*: 14 chapters; 0333; ISBN 978-93-5292-816-3; first edition April 2024; Reprint 2026-27 | `cemm1ps.pdf` | verified |
| Class 4 *Maths Mela* (Grade 4): 14 chapters; 0433; ISBN 978-93-5729-703-5; first edition March 2025; Reprint 2026-27 | `demm1ps.pdf` | verified |
| Class 5 *Maths Mela* (Grade 5): 15 chapters; 0533; ISBN 978-93-5729-818-6; first edition June 2025; Reprint 2026-27 | `eemm1ps.pdf` | verified |
| Class 6 *Ganita Prakash*: 10 chapters; 0674; ISBN 978-93-5292-717-3; first edition Aug 2024; Reprint 2026-27 | `fegp1ps.pdf` | verified |
| Class 7 *Ganita Prakash* Part I: 8 chapters; 0774; ISBN 978-93-5729-983-1; first edition April 2025; Reprint 2026-27 | `gegp1ps.pdf` | verified |
| Class 7 *Ganita Prakash* Part II: 7 chapters (numbered 1-7 again); 0789; ISBN 978-93-5729-156-9; first edition Oct 2025 | `gegp2ps.pdf` | verified (no reprint line on the prelims) |
| Class 8 *Ganita Prakash* Part I: 7 chapters; 0874; ISBN 978-93-5729-642-7; first edition July 2025; Reprint 2026-27 | `hegp1ps.pdf` | verified |
| Class 8 *Ganita Prakash* Part II: 7 chapters (numbered 1-7 again); 0889; ISBN 978-93-5729-106-4; first edition Dec 2025 | `hegp2ps.pdf` | verified (no reprint line on the prelims) |
| No other new Class 1-8 maths books found: all ten carry 2026-27 printings or are first editions from 2025 | prelims above | verified for these files; no separate catalogue check |
| NCF-SE 2023, First Edition Oct 2024, ISBN 978-93-5292-741-8, © NCERT, all rights reserved | NCF-SE PDF imprint | verified |
| Foundational maths = CG-8 with C-8.1 to C-8.14 (Part C Ch 1, §1.4, Table 1.1iii, p. 200) | NCF-SE PDF | verified |
| Preparatory maths = CG-1 to CG-5, 19 competencies (§3.4.1.1, pp. 253-254); no data-handling competency in that list | NCF-SE PDF | verified |
| Middle maths = CG-1 to CG-10, 30 competencies (§3.4.1.2, pp. 255-257) | NCF-SE PDF | verified |

Chapter PDFs (106) were also downloaded. For Classes 6-8, numbered section headings were extracted automatically. For all classes, keyword counts were used as evidence of chapter content. File list and checksums: `docs/sources.md`.

## 2. Not verified / judgement calls

- **Chapter `contentSummary`** texts are our short descriptions from headings and keyword hits. Classes 1-2 PDFs are image-heavy with little extractable text, so those summaries lean more on chapter titles and are less certain.
- **Chapter-to-competency codes** (`ncfCompetencies` on chapters) are our inference. NCERT prefaces may state their own alignment; we did not extract it.
- **Topic alignments** (706) were assigned by an AI assistant going topic by topic through all 503 Marble topics, using the evidence above. `exact` (309) means a chapter title, heading or strong keyword evidence names the concept; `inferred` (397) is judgement. Neither has been teacher-checked.
- **Topic competencies** are derived mechanically (chapter codes filtered by the topic's domain), except for the 48 cross-cutting skills, which were assigned by hand. All are marked `inferred`.
- **Absence claims** ("not in Classes 1-8") rest on keyword searches of the chapter PDFs (e.g. no hits for probability, coordinate, circumference, π). A search can miss content that uses different words or appears only in figures.
- **Class 9 pointers** in notes (e.g. *Ganita Manjari* Ch 7 for probability) use chapter titles verified in an earlier audit (`iemh1ps.pdf`, `iemh2ps.pdf`); the chapter contents were not checked.
- **New topics (31)** and **new edges (65)** are AI drafts. Edge strengths (hard/soft) are especially uncertain.
- **Grades** = earliest aligned NCERT class. For cross-cutting skills with no chapter, grade = Marble age minus 5 (Class 1 ≈ age 6), minimum 1, marked `age-estimate`.
- Marble's own content (topic text, age bands, edges) is used unchanged. It reflects UK/US curricula and was not reviewed for India beyond the localisation notes.

## 3. Copyright handling

- Nothing from the body of any NCERT book is reproduced: only titles, codes, ISBNs, dates and chapter names.
- NCF-SE competency statements are not quoted. The PDF is "all rights reserved" and this dataset is openly licensed, so each competency has our own short paraphrase and a page reference.
- NCERT PDFs are not committed to the repository.

## 4. Tools

Python 3 standard library and `pdftotext` (poppler) for extraction. No machine-learning text matching was used to decide the mapping. The mapping tables are plain text in `scripts/build/` so every decision can be reviewed in a diff.
