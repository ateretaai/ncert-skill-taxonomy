# Attribution and notices

## Marble Skill Taxonomy (upstream: required attribution)

This dataset is a derivative database of the Marble Skill Taxonomy. As the upstream README requires, any use must credit:

> Marble Skill Taxonomy (v1) · © Generative Spark, Inc. (Marble) · https://withmarble.com · licensed under ODbL 1.0 (database) and CC BY-SA 4.0 (content).

- Upstream repository: https://github.com/withmarbleapp/os-taxonomy (commit `96a7933`, data generated 2026-07-08).
- Used: the 503 `Mathematics` topics from `data/topics.json` and the 985 dependencies between them from `data/dependencies.json`.
- **Changes made** (ODbL §4.6 / CC BY-SA 4.0 §3(a)(1)(B)):
  - Kept only the Mathematics subset; dropped 66 edges whose other end is a non-Mathematics topic (listed in `docs/dropped-edges.json`).
  - Added fields to every topic (`origin`, `reviewStatus`, `grade`, `gradeSource`, `ncertStatus`, `noNcertHomeReason`, `localisation`) and an `origin` field to every edge.
  - Added Indian-localised alternative text for 8 topics (₹ instead of £/$, metric instead of imperial, Indian digit grouping) in `localisation.localised`; Marble's original text is unchanged.
  - Added 31 new topics (`ncm_` ids) and 65 new edges, NCERT/NCF-SE alignment files and documentation.
- Marble's `standards` codes (`ccss-math:…`, `uk-nc-2013:…`) are kept as bare identifiers. Their text is not included. If you look them up or display them, these upstream notices apply:
  - UK National Curriculum: "Contains public sector information licensed under the Open Government Licence v3.0."
  - Common Core: "© Copyright 2010 National Governors Association Center for Best Practices and Council of Chief State School Officers." (CCSS Public License, purpose-limited.)

## Our additions

New topics, new edge reasons, alignment notes, chapter `contentSummary` texts and competency `summary` paraphrases were written for this dataset (AI-drafted, editor-directed) and are released under the same licences: ODbL 1.0 for the database and CC BY-SA 4.0 for the text. Credit as "ncert-skill-taxonomy contributors".

## NCERT and NCF-SE 2023 (not licensed by us)

- NCERT textbooks (*Joyful Mathematics*, *Maths Mela*, *Ganita Prakash*) and the *National Curriculum Framework for School Education 2023* are © National Council of Educational Research and Training. Their imprint pages say "ALL RIGHTS RESERVED".
- This dataset reproduces only **factual references**: book titles, NCERT book codes, ISBNs, edition dates, chapter numbers and chapter titles, and NCF-SE curricular-goal / competency **codes**. Competency and goal descriptions here are **our own paraphrases**, not NCERT's text. No exercises, examples, explanations or figures from the books are included.
- Our ODbL / CC BY-SA licences do **not** extend to NCERT material. For the authoritative text, use the official PDFs listed in `docs/sources.md`.
- "Aligned to NCERT / NCF-SE 2023" describes our own mapping. It does **not** mean NCERT, CBSE or the Ministry of Education reviewed or endorse this dataset.

This is not legal advice. Have a lawyer review before commercial launch, especially before showing NCERT chapter titles at scale in a paid product.
