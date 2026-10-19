#!/usr/bin/env python3
"""Generate docs/coverage.md from the data files. Stdlib only."""
import json, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = lambda p: json.load(open(os.path.join(ROOT, "data", p), encoding="utf-8"))
T = L("topics.json")["topics"]; A = {a["topicId"]: a for a in L("ncert-alignments.json")["alignments"]}
C = L("ncert-curriculum.json"); E = L("dependencies.json")["dependencies"]
byid = {t["id"]: t for t in T}
def nm(tid): t = byid[tid]; return f"{t['name']} (`{tid}`)"
out = []
w = out.append
w("# Coverage report: ncert-skill-taxonomy v0.1\n")
w("> **Status: AI-drafted, not teacher-reviewed.** Every alignment below is an editor/AI judgement. 'exact' means the chapter title, a verified section heading or strong keyword evidence in the official chapter PDF names the concept; 'inferred' means judgement from the chapter's theme. Treat 'inferred' as a hypothesis for a teacher to confirm.\n")
st = collections.Counter(t["ncertStatus"] for t in T); org = collections.Counter(t["origin"] for t in T)
conf = collections.Counter(c["confidence"] for a in A.values() for c in a["chapters"])
w("## Summary\n")
w(f"- Topics: **{len(T)}** = {org['marble']} from Marble (Mathematics) + {org['ncert-new']} new NCERT gap topics (`ncm_`).")
w(f"- NCERT status: {st['mapped']} mapped to at least one chapter, {st['cross-cutting']} cross-cutting process skills (aligned via NCF competencies), {st['no-ncert-home']} with no NCERT Classes 1-8 home.")
mm = sum(1 for t in T if t['origin']=='marble' and A[t['id']]['chapters'])
w(f"- Marble topics with at least one chapter alignment: **{mm} / 503**.")
w(f"- Chapter alignments: {sum(conf.values())} ({conf['exact']} exact, {conf['inferred']} inferred).")
w(f"- Prerequisite edges: {len(E)} ({sum(1 for e in E if e['origin']=='marble')} Marble, {sum(1 for e in E if e['origin']=='ncert-new')} new).\n")

w("## Per class\n")
w("| Class | Book(s) | Chapters | Chapters with >=1 topic | Distinct topics aligned | Exact / inferred links |")
w("|---|---|---:|---:|---:|---|")
use = collections.defaultdict(list)
for a in A.values():
    for c in a["chapters"]: use[c["chapterId"]].append((a["topicId"], c["confidence"]))
for cls in range(1, 9):
    bks = [b for b in C["books"] if b["class"] == cls]
    chs = [c for b in bks for c in b["chapters"]]
    topics = {t for c in chs for t, _ in use[c["id"]]}
    ex = sum(1 for c in chs for _, k in use[c["id"]] if k == "exact"); inf = sum(1 for c in chs for _, k in use[c["id"]] if k == "inferred")
    w(f"| {cls} | {', '.join(b['title'] + (' Part ' + str(b['part']) if b['part'] else '') for b in bks)} | {len(chs)} | {sum(1 for c in chs if use[c['id']])} | {len(topics)} | {ex} / {inf} |")
w("")
w("## Per chapter\n")
w("Thin = fewer than 3 aligned topics (a likely content gap or a chapter that is mostly puzzles/themes).\n")
for b in C["books"]:
    w(f"### Class {b['class']}: {b['title']}{' Part ' + str(b['part']) if b['part'] else ''} (`{b['key']}`)\n")
    w("| Ch | Chapter | Topics (exact/inferred) | New `ncm_` topics | Flag |")
    w("|---:|---|---|---|---|")
    for c in b["chapters"]:
        u = use[c["id"]]; ex = sum(1 for _, k in u if k == "exact")
        new = [t for t, _ in u if t.startswith("ncm_")]
        w(f"| {c['chapter']} | {c['chapterName']} | {len(u)} ({ex}/{len(u)-ex}) | {', '.join(new) or '-'} | {'thin' if len(u) < 3 else ''} |")
    w("")
w("## Marble topics with no NCERT Classes 1-8 home\n")
reasons = collections.defaultdict(list)
for t in T:
    if t["ncertStatus"] == "no-ncert-home": reasons[t["noNcertHomeReason"]].append(t)
label = {"not-in-ncert-classes-1-8": "Not in NCERT Classes 1-8 (often appears in Class 9/10 or not at all)", "not-applicable-in-india": "Not applicable in India",
         "representation-not-used-in-ncert": "Representation not used by NCERT (US line plots)", "not-found": "Not found (search inconclusive)"}
for r, ts in reasons.items():
    w(f"### {label[r]}: {len(ts)}\n")
    for t in ts: w(f"- {t['domain']}: {nm(t['id'])}. {A[t['id']]['note'] or ''}")
    w("")
w("## NCERT content gaps filled with new topics (`ncm_`, AI-draft)\n")
w("| id | Name | Class | Chapters | Prerequisites |")
w("|---|---|---:|---|---|")
for t in T:
    if t["origin"] != "ncert-new": continue
    pre = [e for e in E if e["topicId"] == t["id"]]
    w(f"| `{t['id']}` | {t['name']} | {t['grade']} | {', '.join(c['chapterId'].split(':',1)[1] + ('' if c['confidence']=='exact' else ' (inferred)') for c in A[t['id']]['chapters'])} | {'; '.join(byid[e['prerequisiteId']]['name'] + ' [' + e['strength'] + ']' for e in pre)} |")
w("")
w("## Low-confidence and partial items\n")
inf_only = [t for t in T if A[t["id"]]["chapters"] and all(c["confidence"] == "inferred" for c in A[t["id"]]["chapters"])]
w(f"### Topics whose chapter links are all 'inferred': {len(inf_only)}\n")
w("These need a teacher to confirm the chapter. Listed by earliest class.\n")
for t in sorted(inf_only, key=lambda t: (t["grade"], t["name"])):
    w(f"- Class {t['grade']}: {nm(t['id'])} -> {', '.join(c['chapterId'].split(':',1)[1] for c in A[t['id']]['chapters'])}")
w("")
part = [t for t in T if (A[t["id"]]["note"] or "").lower().startswith(("partial", "low confidence")) or "low confidence" in (A[t["id"]]["note"] or "").lower()]
w(f"### Partial or explicitly low-confidence mappings: {len(part)}\n")
for t in part: w(f"- {nm(t['id'])}: {A[t['id']]['note']}")
w("")
nocomp = [t for t in T if t["ncertStatus"] == "mapped" and not A[t["id"]]["competencies"]]
w(f"### Mapped topics with no NCF competency link: {len(nocomp)}\n")
for t in nocomp: w(f"- {nm(t['id'])}")
w("\nNote: NCF-SE's Preparatory list has no data-handling competency, so Class 3-5 data topics cannot link to one.\n")
w("### Grade shift versus Marble's age band\n")
w("Marble ages come from UK/US curricula. Comparing Marble's `ageRangeStart` with the NCERT class (class + 5 ~ age) for mapped Marble topics:\n")
sh = collections.Counter()
for t in T:
    if t["origin"] == "marble" and t["gradeSource"] == "ncert-alignment":
        d = (t["grade"] + 5) - t["ageRangeStart"]; sh["NCERT later (2+ yrs)" if d >= 2 else "NCERT later (1 yr)" if d == 1 else "same" if d == 0 else "NCERT earlier"] += 1
for k in ["NCERT earlier", "same", "NCERT later (1 yr)", "NCERT later (2+ yrs)"]: w(f"- {k}: {sh[k]}")
w("\nBiggest shifts: decimals, percentages, ratio and some geometry arrive later in NCERT than in the UK/US; probability, coordinates and volume are absent from Classes 1-8.\n")
open(os.path.join(ROOT, "docs", "coverage.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("wrote docs/coverage.md", len(out), "lines")
