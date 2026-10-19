#!/usr/bin/env python3
"""Builds ncert-skill-taxonomy v0.1 data files from Marble's taxonomy + editor mappings. Stdlib only."""
import json, hashlib, os, re, collections, datetime
from curriculum_data import BOOKS, SHORT, CHAPTER_COMPETENCIES, DOMAIN_FILTER, BASE
from ncf_data import SRC, CG, C
from newtopics_data import NEW

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MARBLE = os.environ.get("MARBLE_DATA", os.path.join(os.path.dirname(ROOT), "os-taxonomy", "data"))
OUT = os.path.join(ROOT, "data")
VERSION = "0.1.0"
os.makedirs(OUT, exist_ok=True)
H = os.path.dirname(os.path.abspath(__file__))

idx = json.load(open(os.path.join(H, "index.json")))          # M### -> Marble id
mt = json.load(open(os.path.join(MARBLE, "topics.json")))
md = json.load(open(os.path.join(MARBLE, "dependencies.json")))
math = [t for t in mt["topics"] if t["subject"] == "Mathematics"]
byid = {t["id"]: t for t in math}
assert len(math) == 503

# ---------- curriculum ----------
STAGE_OF_CLASS = {1:"FS",2:"FS",3:"PS",4:"PS",5:"PS",6:"MS",7:"MS",8:"MS"}
chapters = {}
books_out = []
for b in BOOKS:
    chs = []
    for i, (title, summary) in enumerate(b["chapters"], 1):
        cid = f"ncert:{b['key']}:{i}"
        comp = [f"ncfse-2023:{b['stage']}.C-{c}" for c in CHAPTER_COMPETENCIES[b["key"]][i-1]]
        ch = dict(id=cid, book=b["key"], class_=b["cls"], part=b["part"], chapter=i, chapterName=title,
                  chapterPdf=f"{BASE}{b['chapterFilePrefix']}{i:02d}.pdf", contentSummary=summary,
                  ncfCompetencies=comp)
        chapters[cid] = ch
        chs.append(ch)
    books_out.append(dict(key=b["key"], **{"class": b["cls"]}, part=b["part"], title=b["title"], subtitle=b["subtitle"],
        ncertBookCode=b["code"], isbn=b["isbn"], firstEdition=b["firstEdition"], printingSeen=b["printing"],
        ncfStage={"FS":"Foundational","PS":"Preparatory","MS":"Middle"}[b["stage"]],
        prelimsUrl=BASE + b["file"], verified=True,
        verification="Title, imprint (code, ISBN, first edition) and contents page read from the official prelims PDF on 2026-10-18.",
        chapters=[{("class" if k=="class_" else k): v for k, v in c.items()} for c in chs]))

def fix(c): return {("class" if k=="class_" else k): v for k, v in c.items()}
curriculum = dict(
    dataset="ncert-skill-taxonomy", version=VERSION, subject="Mathematics", board="NCERT (used by CBSE and many state boards)",
    academicYear="2026-27", retrieved="2026-10-18",
    note=("Book metadata and chapter titles are factual references taken from NCERT's official prelims PDFs (contents pages). "
          "NCERT textbooks are (c) NCERT, all rights reserved; no textbook text is reproduced beyond titles. "
          "'contentSummary' is the dataset editors' own short description inferred from section headings and keyword search of the chapter PDFs; it is NOT an official syllabus statement. "
          "'ncfCompetencies' per chapter is an editor inference, not an NCERT mapping. "
          "Chapter numbering restarts at 1 in Part II books (GP7-2, GP8-2), so always key chapters by book."),
    sources=[dict(title="NCERT textbook PDFs (prelims and chapter files)", url="https://ncert.nic.in/textbook.php", retrieved="2026-10-18")],
    books=books_out)

# ---------- NCF competencies ----------
items = []
for st in ["FS","PS","MS"]:
    for code, summ in C[st].items():
        cg = code.split(".")[0]
        items.append(dict(id=f"ncfse-2023:{st}.C-{code}", stage=SRC[st]["stage"], stageCode=st, grades=SRC[st]["grades"],
                          cg=f"CG-{cg}", code=f"C-{code}", summary=summ, summaryIsParaphrase=True,
                          source=dict(section=SRC[st]["section"], printedPages=SRC[st]["printedPages"])))
goals = [dict(id=f"ncfse-2023:{st}.CG-{k}", stageCode=st, stage=SRC[st]["stage"], code=f"CG-{k}", summary=v, summaryIsParaphrase=True)
         for st in ["FS","PS","MS"] for k, v in CG[st].items()]
ncf = dict(dataset="ncert-skill-taxonomy", version=VERSION,
    source=dict(title="National Curriculum Framework for School Education 2023 (NCF-SE 2023)", publisher="NCERT, Ministry of Education, Government of India",
                edition="First Edition, October 2024 (Kartika 1946)", isbn="978-93-5292-741-8",
                url="https://www.ncert.nic.in/pdf/NCFSE-2023-August_2023.pdf", retrieved="2026-10-18",
                copyright="(c) National Council of Educational Research and Training, 2024. ALL RIGHTS RESERVED (per imprint page)."),
    textPolicy=("Codes are reproduced as factual identifiers. Because the NCF-SE PDF is 'all rights reserved' and this dataset is redistributed under open licences, "
                "the official competency wording is NOT reproduced. Each 'summary' is the editors' own short paraphrase written for navigation; consult the official PDF "
                "(sections/pages given) for the authoritative text. Codes restart per stage, so they are namespaced FS/PS/MS."),
    stages={k: v for k, v in SRC.items()},
    notes=["Foundational Stage competencies are organised by developmental domain; mathematics sits under CG-8 (Cognitive Development). Other Foundational CGs are not maths and are omitted.",
           "The Preparatory Stage mathematics list (CG-1 to CG-5) contains no explicit data-handling competency, although Maths Mela 4 and 5 have data chapters.",
           "NCF-SE describes competencies as end-of-stage and suggestive; they are not per-class learning outcomes.",
           "Secondary Stage (Classes 9-10) competencies exist (CG-1 to CG-11) but are out of scope for v0.1."],
    curricularGoals=goals, competencies=items)
compids = {i["id"] for i in items}

# ---------- parse editor mappings ----------
def parse_chapters(s):
    out = []
    for tok in [x for x in s.split(",") if x.strip()]:
        tok = tok.strip(); conf = "exact" if tok.endswith("*") else "inferred"; tok = tok.rstrip("*")
        cls, ch = tok.split(":")
        out.append((f"ncert:{SHORT[cls]}:{int(ch)}", conf))
    return out
maps = {}
for fn in ["map1.txt","map2.txt","map3.txt"]:
    for line in open(os.path.join(H, fn), encoding="utf-8"):
        line = line.rstrip("\n")
        if not line: continue
        k, chs, note = line.split("|", 2)
        maps[k] = dict(chapters=parse_chapters(chs), note=note.strip() or None, cross=False, comps=None)
for line in open(os.path.join(H, "crosscut.txt"), encoding="utf-8"):
    line = line.rstrip("\n")
    if not line: continue
    k, chs, comps = line.split("|", 2)
    maps[k] = dict(chapters=parse_chapters(chs), note="Cross-cutting process skill: practised across many chapters rather than taught in one; aligned mainly via NCF-SE competencies.", cross=True,
                   comps=[f"ncfse-2023:{c.strip()}" for c in comps.split(",") if c.strip()])
assert set(maps) == set(idx), set(idx) ^ set(maps)
# Resolve internal 'See M###' references: inherit the referenced note for classification, and rewrite to public ids.
for k, m in maps.items():
    n = m["note"]
    if n:
        ref = re.search(r"[Ss]ee (M\d{3})", n)
        m["classifyNote"] = (maps[ref.group(1)]["note"] if ref else n)
        m["note"] = re.sub(r"M\d{3}", lambda g: f"'{byid[idx[g.group(0)]]['name']}' ({idx[g.group(0)]})", n)
    else:
        m["classifyNote"] = None
rev = {v: k for k, v in idx.items()}

def stage_of(cid): return STAGE_OF_CLASS[chapters[cid]["class_"]]
def derive_comps(domain, chs):
    out = []
    for cid, _ in chs:
        st = stage_of(cid); allowed = DOMAIN_FILTER[st][domain]
        for code in chapters[cid]["ncfCompetencies"]:
            num = code.split(".C-")[1]
            if num in allowed and code not in out: out.append(code)
    return out

def no_home_reason(note):
    n = (note or "").lower()
    if "not applicable" in n: return "not-applicable-in-india"
    if "line plot" in n: return "representation-not-used-in-ncert"
    if any(w in n for w in ["class 9","class 10","ganita manjari","beyond","not in classes 1-8","not in ncert classes 1-8","not found","not in classes"]): return "not-in-ncert-classes-1-8"
    return "not-found"

# ---------- localisation overrides (CC BY-SA 4.0 adaptations of Marble text; originals kept unchanged) ----------
LOCAL = {
 "M375": dict(name="Rupees and paise notation", description="Recognise and use the symbol ₹ for rupees and the word paise, write amounts such as ₹1.50, and combine coins and notes to make a given value",
              evidence=["Write ₹1.50 as one rupee fifty paise","Combine coins to make a given total, e.g. ₹5 + ₹2 + ₹1 = ₹8","Read prices written with the ₹ symbol"],
              assessmentPrompt="If {{name}} picks up a ₹10 note, a ₹5 coin and a ₹2 coin, can they write the total using the ₹ symbol and tell you if that's enough to buy something costing ₹18?"),
 "M384": dict(description="Add and subtract amounts of money in rupees (₹) to give change in practical contexts",
              evidence=["Calculate the total cost of two or three items priced in rupees","Work out the change from ₹50 or ₹100","Record money calculations using ₹ notation correctly (e.g. ₹34.50)"],
              assessmentPrompt="If {{name}} buys a notebook for ₹35 and a pencil for ₹12 with a ₹50 note, can they work out exactly how much change they should receive?"),
 "M385": dict(name="Money word problems with coins and notes", description="Solve word problems involving Indian coins and notes, using the ₹ symbol appropriately",
              evidence=["Determine the total value of a collection of ₹1, ₹2, ₹5 and ₹10 coins","Solve a word problem about making change with Indian currency","Use the ₹ symbol correctly in answers"],
              assessmentPrompt="If {{name}} has two ₹10 coins, one ₹5 coin and three ₹1 coins, can they work out the total and tell you whether that's enough to buy something costing ₹30?"),
 "M398": dict(description="Estimate, compare, and calculate different measures including money in rupees",
              evidence=["Estimate the length of the classroom in metres","Compare 1.5 kg and 1200 g and identify which is heavier","Calculate the total cost of 3 items at ₹45, ₹30 and ₹75"],
              assessmentPrompt="If {{name}} is comparing three items costing ₹85, ₹110 and ₹50, can they put them in order from cheapest to most expensive and work out the total cost?"),
 "M382": dict(description="Estimate lengths using centimetres and metres",
              evidence=["Estimate the length of a classroom object before measuring it","Use a known reference (e.g. width of a finger ≈ 1 cm) to make reasonable estimates","Check estimates by measuring and evaluate how close they were"]),
 "M388": dict(description="Measure the length of an object by selecting and using appropriate tools such as rulers, metre scales, and measuring tapes",
              evidence=["Choose the most appropriate tool for measuring a given object","Align the zero mark of a ruler with the end of the object and read the measurement","Measure lengths in centimetres and metres using the correct tool"]),
 "M393": dict(description="Measure areas by counting unit squares (square cm, square m)"),
 "M047": dict(evidence=["Write 4,03,072 (Indian grouping) / 403,072 (international) in words and in expanded form","Compare 5,48,301 and 5,43,801 using < and explain the reasoning","Order four six-digit numbers from smallest to largest"]),
}

# ---------- topics ----------
topics_out, align_out = [], []
for t in math:
    k = rev[t["id"]]; m = maps[k]
    chs = m["chapters"]
    comps = m["comps"] if m["cross"] else derive_comps(t["domain"], chs)
    if m["cross"] and chs:  # add chapter-derived comps too
        for c in derive_comps(t["domain"], chs):
            if c not in comps: comps.append(c)
    if chs:
        grade = min(chapters[c]["class_"] for c, _ in chs); gsrc = "ncert-alignment"
    elif m["cross"]:
        grade = max(1, t["ageRangeStart"] - 5); gsrc = "age-estimate"
    else:
        grade = None; gsrc = None
    status = "cross-cutting" if m["cross"] else ("mapped" if chs else "no-ncert-home")
    loc_notes = []
    if m["note"] and (m["note"].startswith("India:") or m["note"].startswith("LOCALISED:")): loc_notes.append(m["note"])
    if k in ("M047","M049","M050","M053","M058") and not loc_notes: loc_notes.append("India: use lakh/crore naming alongside million.")
    nt = dict(t)
    nt.update(origin="marble", reviewStatus="ai-draft", grade=grade, gradeSource=gsrc, ncertStatus=status)
    if status == "no-ncert-home": nt["noNcertHomeReason"] = no_home_reason(m["classifyNote"])
    if loc_notes or k in LOCAL:
        nt["localisation"] = dict(notes=loc_notes or ["India: localised text provided."], localised=LOCAL.get(k))
        if nt["localisation"]["localised"] is None: del nt["localisation"]["localised"]
    topics_out.append(nt)
    align_out.append(dict(topicId=t["id"], ncertStatus=status, grade=grade, gradeSource=gsrc,
        chapters=[dict(chapterId=c, book=chapters[c]["book"], **{"class": chapters[c]["class_"]}, part=chapters[c]["part"],
                       chapter=chapters[c]["chapter"], chapterName=chapters[c]["chapterName"], confidence=conf, note=None) for c, conf in chs],
        competencies=[dict(id=c, confidence="inferred", basis=("editor" if m["cross"] and c in (m["comps"] or []) else "chapter-domain-heuristic")) for c in comps],
        note=m["note"], reviewStatus="ai-draft"))

def resolve(ref): return idx[ref] if ref.startswith("M") else ref
new_edges = []
for n in NEW:
    chs = [(f"ncert:{SHORT[s.split(':')[0]]}:{int(s.split(':')[1])}", conf) for s, conf in n["chapters"]]
    grade = min(chapters[c]["class_"] for c, _ in chs)
    comps = derive_comps(n["domain"], chs)
    topics_out.append(dict(id=n["id"], type=n["type"], subject="Mathematics", domain=n["domain"], name=n["name"], description=n["description"],
        ageRangeStart=grade+5, ageRangeEnd=grade+6, centrality=None, evidence=n["evidence"], assessmentPrompt=n["prompt"], standards=[],
        origin="ncert-new", reviewStatus="ai-draft", grade=grade, gradeSource="ncert-alignment", ncertStatus="mapped"))
    align_out.append(dict(topicId=n["id"], ncertStatus="mapped", grade=grade, gradeSource="ncert-alignment",
        chapters=[dict(chapterId=c, book=chapters[c]["book"], **{"class": chapters[c]["class_"]}, part=chapters[c]["part"],
                       chapter=chapters[c]["chapter"], chapterName=chapters[c]["chapterName"], confidence=conf, note=None) for c, conf in chs],
        competencies=[dict(id=c, confidence="inferred", basis="chapter-domain-heuristic") for c in comps],
        note="New topic drafted to fill an NCERT gap; ageRange derived from NCERT class (Class N ~ age N+5 to N+6).", reviewStatus="ai-draft"))
    for ref, strength, reason in n["prereqs"]:
        new_edges.append(dict(topicId=n["id"], prerequisiteId=resolve(ref), strength=strength, reason=reason, origin="ncert-new", reviewStatus="ai-draft"))

ids = {t["id"] for t in topics_out}
marble_edges, dropped = [], []
for d in md["dependencies"]:
    a, b = d["topicId"] in byid, d["prerequisiteId"] in byid
    if a and b: marble_edges.append(dict(d, origin="marble"))
    elif a or b: dropped.append(d)
edges = marble_edges + new_edges

# ---------- write ----------
def dump(name, obj):
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False, indent=2); f.write("\n")
dump("topics.json", dict(version=VERSION, topicCount=len(topics_out), basedOn="Marble Skill Taxonomy v1 (Mathematics subset)", topics=topics_out))
dump("dependencies.json", dict(version=VERSION, note="topicId depends on prerequisiteId. Marble maths-to-maths edges unchanged (origin 'marble'); edges to non-maths Marble topics are dropped (see docs/dropped-edges.json). New edges have origin 'ncert-new'.", edgeCount=len(edges), dependencies=edges))
dump("ncert-curriculum.json", curriculum)
dump("ncf-competencies.json", ncf)
dump("ncert-alignments.json", dict(version=VERSION, note=("One record per topic. Chapter 'confidence': 'exact' = chapter title or a verified section heading/strong keyword evidence in the chapter PDF names the concept; "
     "'inferred' = editor judgement from chapter themes. All competency links are inferred (basis given). Every record is an AI draft awaiting teacher review."), alignments=align_out))
os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
with open(os.path.join(ROOT, "docs", "dropped-edges.json"), "w") as f:
    json.dump(dict(note="Marble edges linking a Mathematics topic to a non-Mathematics topic; dropped because the other end is not in this dataset.", count=len(dropped), edges=dropped), f, indent=2, ensure_ascii=False)

files = ["topics.json","dependencies.json","ncert-alignments.json","ncert-curriculum.json","ncf-competencies.json"]
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
by_origin = collections.Counter(t["origin"] for t in topics_out)
by_status = collections.Counter(t["ncertStatus"] for t in topics_out)
chapters_with = collections.defaultdict(set)
for a in align_out:
    for c in a["chapters"]: chapters_with[c["class"]].add(c["chapterId"])
manifest = dict(dataset="ncert-skill-taxonomy", version=VERSION, status="AI-drafted; needs teacher review",
    generatedAt=datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
    derivedFrom=dict(name="Marble Skill Taxonomy", version="v1", repo="https://github.com/withmarbleapp/os-taxonomy", commit="96a7933", subset="Mathematics"),
    counts=dict(topics=len(topics_out), topicsByOrigin=dict(by_origin), topicsByNcertStatus=dict(by_status),
                dependencies=len(edges), dependenciesByOrigin=dict(collections.Counter(e["origin"] for e in edges)), droppedCrossSubjectEdges=len(dropped),
                books=len(books_out), chapters=len(chapters), chaptersWithAtLeastOneTopicByClass={str(k): len(v) for k, v in sorted(chapters_with.items())},
                chaptersByClass={str(c): sum(1 for x in chapters.values() if x["class_"] == c) for c in range(1, 9)},
                ncfCompetencies=len(items), ncfCurricularGoals=len(goals),
                chapterAlignments=sum(len(a["chapters"]) for a in align_out),
                chapterAlignmentsByConfidence=dict(collections.Counter(c["confidence"] for a in align_out for c in a["chapters"]))),
    files={f: dict(bytes=os.path.getsize(os.path.join(OUT, f)), sha256=sha(os.path.join(OUT, f))) for f in files})
with open(os.path.join(ROOT, "manifest.json"), "w") as f: json.dump(manifest, f, indent=2); f.write("\n")
print(json.dumps(manifest["counts"], indent=1))
