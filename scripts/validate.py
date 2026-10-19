#!/usr/bin/env python3
"""Validate ncert-skill-taxonomy data: structure, enums, referential integrity, DAG, grades, manifest checksums.
Stdlib only. Usage: python3 scripts/validate.py   (exit code 0 = pass)
Set STRICT_REVIEW=1 to fail while any record is still 'ai-draft' (use as a gate before paid/production use)."""
import json, os, re, sys, hashlib, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, *p)
errors, warnings = [], []
def err(m): errors.append(m)
def warn(m): warnings.append(m)
def load(p):
    try:
        with open(p, encoding="utf-8") as f: return json.load(f)
    except Exception as e:
        err(f"cannot load {p}: {e}"); return None

topics_f = load(D("data", "topics.json")); deps_f = load(D("data", "dependencies.json"))
al_f = load(D("data", "ncert-alignments.json")); cur_f = load(D("data", "ncert-curriculum.json"))
ncf_f = load(D("data", "ncf-competencies.json")); man = load(D("manifest.json"))
if errors: print("\n".join(errors)); sys.exit(1)

TYPES = {"CONCEPTUAL", "PROCEDURAL", "REPRESENTATIONAL", "LANGUAGE", "META"}
DOMAINS = {"Counting & Cardinality","Number Representation & Place Value","Addition & Subtraction","Multiplication & Division","Fractions",
           "Ratio & Proportion","Algebra","Geometry","Measurement","Data & Statistics","Probability","Mathematical Thinking"}
ORIGINS = {"marble", "ncert-new"}; REVIEW = {"ai-draft", "teacher-reviewed"}
STATUS = {"mapped", "no-ncert-home", "cross-cutting"}
NOHOME = {"not-in-ncert-classes-1-8", "not-applicable-in-india", "representation-not-used-in-ncert", "not-found"}
ID_RE = re.compile(r"^(mt_[A-Za-z0-9_-]{10}|ncm_\d{4})$")
COMP_RE = re.compile(r"^ncfse-2023:(FS|PS|MS)\.C-(\d+)\.(\d+)$")
REQ = ["id","type","subject","domain","name","description","ageRangeStart","ageRangeEnd","evidence","assessmentPrompt","standards","origin","reviewStatus","grade","gradeSource","ncertStatus"]

# --- curriculum ---
chapters = {}; book_keys = set()
for b in cur_f["books"]:
    if b["key"] in book_keys: err(f"duplicate book {b['key']}")
    book_keys.add(b["key"])
    if not (1 <= b["class"] <= 8): err(f"book {b['key']} class out of range")
    nums = [c["chapter"] for c in b["chapters"]]
    if nums != list(range(1, len(nums) + 1)): err(f"book {b['key']} chapter numbers not 1..n")
    for c in b["chapters"]:
        if c["id"] != f"ncert:{b['key']}:{c['chapter']}": err(f"bad chapter id {c['id']}")
        if c["id"] in chapters: err(f"duplicate chapter {c['id']}")
        chapters[c["id"]] = c
        if not c["chapterName"].strip(): err(f"empty chapter name {c['id']}")

# --- NCF ---
comp_ids = set(); cg_ids = {g["id"] for g in ncf_f["curricularGoals"]}
for c in ncf_f["competencies"]:
    m = COMP_RE.match(c["id"])
    if not m: err(f"bad competency id {c['id']}"); continue
    if c["id"] in comp_ids: err(f"duplicate competency {c['id']}")
    comp_ids.add(c["id"])
    if c["cg"] != f"CG-{m.group(2)}": err(f"{c['id']}: cg field {c['cg']} does not match code")
    if f"ncfse-2023:{m.group(1)}.CG-{m.group(2)}" not in cg_ids: err(f"{c['id']}: parent goal missing")
for c in chapters.values():
    for k in c.get("ncfCompetencies", []):
        if k not in comp_ids: err(f"chapter {c['id']} references unknown competency {k}")

# --- topics ---
topics = topics_f["topics"]; ids = {}
if topics_f.get("topicCount") != len(topics): err("topicCount mismatch")
for t in topics:
    for k in REQ:
        if k not in t: err(f"{t.get('id')}: missing field {k}")
    tid = t.get("id", "")
    if not ID_RE.match(tid): err(f"bad id {tid}")
    if tid in ids: err(f"duplicate topic id {tid}")
    ids[tid] = t
    if t.get("type") not in TYPES: err(f"{tid}: bad type {t.get('type')}")
    if t.get("domain") not in DOMAINS: err(f"{tid}: bad domain {t.get('domain')}")
    if t.get("subject") != "Mathematics": err(f"{tid}: subject must be Mathematics")
    if t.get("origin") not in ORIGINS: err(f"{tid}: bad origin")
    if t.get("reviewStatus") not in REVIEW: err(f"{tid}: bad reviewStatus")
    if t.get("ncertStatus") not in STATUS: err(f"{tid}: bad ncertStatus")
    if t.get("origin") == "marble" and not tid.startswith("mt_"): err(f"{tid}: marble topic must keep mt_ id")
    if t.get("origin") == "ncert-new":
        if not tid.startswith("ncm_"): err(f"{tid}: new topic must use ncm_ prefix")
        if t.get("reviewStatus") != "ai-draft": warn(f"{tid}: new topic not ai-draft")
    if t.get("ncertStatus") == "no-ncert-home":
        if t.get("noNcertHomeReason") not in NOHOME: err(f"{tid}: missing/invalid noNcertHomeReason")
        if t.get("grade") is not None: err(f"{tid}: no-ncert-home topic must have grade null")
    if not isinstance(t.get("evidence"), list) or not t["evidence"]: err(f"{tid}: evidence must be non-empty list")
    if t.get("ageRangeStart", 0) > t.get("ageRangeEnd", 0): err(f"{tid}: ageRangeStart > ageRangeEnd")
    if "{{name}}" not in t.get("assessmentPrompt", ""): warn(f"{tid}: assessmentPrompt lacks {{{{name}}}}")
    loc = t.get("localisation")
    if loc and "localised" in loc:
        for k in loc["localised"]:
            if k not in ("name","description","evidence","assessmentPrompt"): err(f"{tid}: unknown localised field {k}")

# --- alignments ---
al = {}
for a in al_f["alignments"]:
    tid = a["topicId"]
    if tid not in ids: err(f"alignment for unknown topic {tid}"); continue
    if tid in al: err(f"duplicate alignment {tid}")
    al[tid] = a; t = ids[tid]
    if a["ncertStatus"] != t["ncertStatus"] or a["grade"] != t["grade"]: err(f"{tid}: alignment/topic status or grade mismatch")
    seen = set()
    for c in a["chapters"]:
        ch = chapters.get(c["chapterId"])
        if not ch: err(f"{tid}: unknown chapter {c['chapterId']}"); continue
        if c["chapterId"] in seen: err(f"{tid}: duplicate chapter {c['chapterId']}")
        seen.add(c["chapterId"])
        if c["confidence"] not in ("exact", "inferred"): err(f"{tid}: bad confidence")
        if (c["book"], c["chapter"], c["chapterName"]) != (ch["book"], ch["chapter"], ch["chapterName"]): err(f"{tid}: chapter fields disagree with curriculum for {c['chapterId']}")
        if c["class"] != ch["class"]: err(f"{tid}: class mismatch {c['chapterId']}")
    for c in a["competencies"]:
        if c["id"] not in comp_ids: err(f"{tid}: unknown competency {c['id']}")
    if t["ncertStatus"] == "mapped" and not a["chapters"]: err(f"{tid}: mapped but no chapters")
    if t["ncertStatus"] == "no-ncert-home" and a["chapters"]: err(f"{tid}: no-ncert-home but has chapters")
    if t["gradeSource"] == "ncert-alignment":
        g = min((c["class"] for c in a["chapters"]), default=None)
        if g != t["grade"]: err(f"{tid}: grade {t['grade']} != earliest aligned class {g}")
    if t["ncertStatus"] == "mapped" and not a["competencies"]: warn(f"{tid}: mapped topic has no NCF competency")
for tid in ids:
    if tid not in al: err(f"{tid}: no alignment record")

# --- dependencies ---
deps = deps_f["dependencies"]; pairs = set(); graph = collections.defaultdict(list); indeg = collections.Counter()
if deps_f.get("edgeCount") != len(deps): err("edgeCount mismatch")
for d in deps:
    a, b = d.get("topicId"), d.get("prerequisiteId")
    if a not in ids: err(f"edge topicId {a} unknown")
    if b not in ids: err(f"edge prerequisiteId {b} unknown")
    if a == b: err(f"self-loop {a}")
    if (a, b) in pairs: err(f"duplicate edge {a} <- {b}")
    pairs.add((a, b))
    if d.get("strength") not in ("hard", "soft"): err(f"edge {a}<-{b}: bad strength")
    if not str(d.get("reason", "")).strip(): err(f"edge {a}<-{b}: empty reason")
    if d.get("origin") not in ORIGINS: err(f"edge {a}<-{b}: bad origin")
    graph[b].append(a); indeg[a] += 1
# cycle check (Kahn)
q = [n for n in ids if indeg[n] == 0]; seen = 0; indeg2 = dict(indeg)
while q:
    n = q.pop(); seen += 1
    for m in graph[n]:
        indeg2[m] -= 1
        if indeg2[m] == 0: q.append(m)
if seen != len(ids): err(f"dependency graph has a cycle ({len(ids) - seen} topics involved)")
for t in topics:
    if t["origin"] == "ncert-new" and not any(d["topicId"] == t["id"] for d in deps): err(f"{t['id']}: new topic has no prerequisite edge")
isolated = [t["id"] for t in topics if not any(t["id"] in p for p in pairs)]
if isolated: warn(f"{len(isolated)} topics have no edges at all")

# --- manifest ---
for f, meta in man["files"].items():
    p = D("data", f)
    if not os.path.exists(p): err(f"manifest lists missing file {f}"); continue
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if h != meta["sha256"]: err(f"checksum mismatch for {f}")
    if os.path.getsize(p) != meta["bytes"]: err(f"size mismatch for {f}")
c = man["counts"]
if c["topics"] != len(topics) or c["dependencies"] != len(deps): err("manifest counts disagree with data")

drafts = sum(1 for t in topics if t["reviewStatus"] == "ai-draft")
if os.environ.get("STRICT_REVIEW") == "1" and drafts: err(f"STRICT_REVIEW: {drafts} topics still ai-draft")

print(f"topics: {len(topics)} ({collections.Counter(t['origin'] for t in topics)})")
print(f"edges: {len(deps)}  chapters: {len(chapters)}  competencies: {len(comp_ids)}  alignments: {len(al)}")
print(f"ncertStatus: {dict(collections.Counter(t['ncertStatus'] for t in topics))}  ai-draft: {drafts}")
for w in warnings[:15]: print("WARN", w)
if len(warnings) > 15: print(f"WARN ... {len(warnings) - 15} more")
if errors:
    for e in errors[:50]: print("ERROR", e)
    print(f"VALIDATION FAILED: {len(errors)} error(s), {len(warnings)} warning(s)"); sys.exit(1)
print(f"VALIDATION PASSED ({len(warnings)} warning(s))")
