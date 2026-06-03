import re
from datetime import date
from models import ConversionResult, Task

# ─────────────────────────────────────────────────────────
# Member lookup table: key (lowercase) → (team, email)
# ─────────────────────────────────────────────────────────
MEMBER_MAP = {
    # --- HR TEAM ---
    "madhumati angadi": ("HR", "madhumati3006@gmail.com"),
    "madhumati":        ("HR", "madhumati3006@gmail.com"),
    "madhu":            ("HR", "madhumati3006@gmail.com"),
    "sanchi":           ("HR", "petkarsanchi@gmail.com"),
    "shruthi":          ("HR", "shruthi.2003v@gmail.com"),
    "godavari dk":      ("HR", "godavari.dk@aksharaenterprises.info"),
    "godavari":         ("HR", "godavari.dk@aksharaenterprises.info"),
    "chandana":         ("HR", "bheemasrichandana@gmail.com"),
    "tridha":           ("HR", "tridha@aksharaenterprises.info"),
    "jagriti":          ("HR", "jagriti@aksharaenterprises.info"),
    "arrel":            ("HR", "arrel@aksharaenterprises.info"),
    "rowena":           ("HR", "rowena@aksharaenterprises.info"),
    "irene":            ("HR", "irene@aksharaenterprises.info"),
    "ashish":           ("HR", "ashish@aksharaenterprises.info"),
    "amritha":          ("HR", "amritha@aksharaenterprises.info"),
    "gowthami":         ("HR", "gowthami@aksharaenterprises.info"),
    "gopika":           ("HR", "gopika@aksharaenterprises.info"),
    "rahul hemanth":    ("HR", "18rahul.hemanth@gmail.com"),
    "rahul":            ("BUSINESS OPERATIONS", "18rahul.hemanth@gmail.com"),

    # --- BUSINESS OPERATIONS TEAM ---
    "chandan":          ("BUSINESS OPERATIONS", "chandan@aksharaenterprises.info"),
    "chandan k":        ("BUSINESS OPERATIONS", "chandan@aksharaenterprises.info"),
    "purav":            ("BUSINESS OPERATIONS", "purav@aksharaenterprises.info"),
    "purav c":          ("BUSINESS OPERATIONS", "purav@aksharaenterprises.info"),
    "kshitij":          ("BUSINESS OPERATIONS", "kshitij@aksharaenterprises.info"),
    "kshithij":         ("BUSINESS OPERATIONS", "kshitij@aksharaenterprises.info"),
    "bopanna":          ("BUSINESS OPERATIONS", "bopanna@aksharaenterprises.info"),
    "pavan":            ("BUSINESS OPERATIONS", "pavan@aksharaenterprises.info"),
    "pavan rag":        ("BUSINESS OPERATIONS", "pavan@aksharaenterprises.info"),
    "pawan":            ("BUSINESS OPERATIONS", "pavan@aksharaenterprises.info"),
    "pawan rag":        ("BUSINESS OPERATIONS", "pavan@aksharaenterprises.info"),
    "abhilash":         ("BUSINESS OPERATIONS", "abhilash@aksharaenterprises.info"),
    "ranjith":          ("BUSINESS OPERATIONS", "ranjith@aksharaenterprises.info"),
    "ujwal":            ("BUSINESS OPERATIONS", "ujwal@aksharaenterprises.info"),
    "abhinitha":        ("BUSINESS OPERATIONS", "abhinitha@aksharaenterprises.info"),
    "padma":            ("BUSINESS OPERATIONS", "padma@aksharaenterprises.info"),
    "benjamin":         ("BUSINESS OPERATIONS", "benjamin@aksharaenterprises.info"),
    "jeff":             ("BUSINESS OPERATIONS", "jeff@aksharaenterprises.info"),
    "pramukh":          ("BUSINESS OPERATIONS", "pramukh@aksharaenterprises.info"),
    "pranauv":          ("BUSINESS OPERATIONS", "pranauv@aksharaenterprises.info"),
    "pranauv namashivayam": ("BUSINESS OPERATIONS", "pranauv@aksharaenterprises.info"),
    "praneel":          ("BUSINESS OPERATIONS", "praneel@aksharaenterprises.info"),
    "rithvik":          ("BUSINESS OPERATIONS", "rithvik@aksharaenterprises.info"),
    "vasudha":          ("BUSINESS OPERATIONS", "vasudha@aksharaenterprises.info"),
    "vinay shetty":     ("BUSINESS OPERATIONS", "vinay@aksharaenterprises.info"),
    "vinay":            ("BUSINESS OPERATIONS", "vinay@aksharaenterprises.info"),
    "yashas":           ("BUSINESS OPERATIONS", "yashas@aksharaenterprises.info"),
    "roshan thomas":    ("BUSINESS OPERATIONS", "roshan.thomas@aksharaenterprises.info"),
    "ananth":           ("BUSINESS OPERATIONS", "ananth@aksharaenterprises.info"),
    "shoaib":           ("BUSINESS OPERATIONS", "shoaib@aksharaenterprises.info"),
    "avish":            ("BUSINESS OPERATIONS", "avish@aksharaenterprises.info"),
    "chirag":           ("BUSINESS OPERATIONS", "chirag@aksharaenterprises.info"),
    "tharun eshwar":    ("BUSINESS OPERATIONS", "tharun.eshwar@aksharaenterprises.info"),

    # --- PRODUCT TEAM ---
    "hemanth":          ("PRODUCT", "hemanth@aksharaenterprises.info"),
    "hemanth kumar gl": ("PRODUCT", "hemanth@aksharaenterprises.info"),
    "kashinath":        ("PRODUCT", "kashinath@aksharaenterprises.info"),
    "vasanth":          ("PRODUCT", "vasanth@aksharaenterprises.info"),
    "shubhanga":        ("PRODUCT", "shubhanga@aksharaenterprises.info"),

    # --- SPOS TEAM ---
    "keshav":           ("SPOS", "keshav@aksharaenterprises.info"),
    "keshav navneet bhattad": ("SPOS", "keshav@aksharaenterprises.info"),
    "haritha":          ("SPOS", "haritha@aksharaenterprises.info"),
    "jyothi":           ("SPOS", "jyothi@aksharaenterprises.info"),
    "roshan paul":      ("SPOS", "roshan.paul@aksharaenterprises.info"),

    # --- STUDENT RELATED BUS ---
    "tharun":           ("STUDENT RELATED BUS", "tharun@aksharaenterprises.info"),
    "tharun chalam":    ("STUDENT RELATED BUS", "tharun@aksharaenterprises.info"),
    "tharun r challam": ("STUDENT RELATED BUS", "tharun@aksharaenterprises.info"),
    "j vaishnav rahul": ("STUDENT RELATED BUS", "vaishnav@aksharaenterprises.info"),
    "rahul vaishnav":   ("STUDENT RELATED BUS", "vaishnav@aksharaenterprises.info"),
    "yogesh":           ("STUDENT RELATED BUS", "yogesh@aksharaenterprises.info"),
    "k yogesh":         ("STUDENT RELATED BUS", "yogesh@aksharaenterprises.info"),
    "sathvik":          ("STUDENT RELATED BUS", "sathvik@aksharaenterprises.info"),
    "sathwik":          ("STUDENT RELATED BUS", "sathvik@aksharaenterprises.info"),
    "suhas":            ("STUDENT RELATED BUS", "suhas@aksharaenterprises.info"),

    # --- NEW JOINERS ---
    "yuvan":            ("NEW JOINERS", "yuvan@aksharaenterprises.info"),
}


TEAM_NORM = {
    "hr": "HR", "human resource": "HR", "human resources": "HR",
    "biz ops": "BUSINESS OPERATIONS", "business ops": "BUSINESS OPERATIONS",
    "business operations": "BUSINESS OPERATIONS", "bizops": "BUSINESS OPERATIONS",
    "new joiner": "NEW JOINERS", "new joiners": "NEW JOINERS",
    "product": "PRODUCT", "spos": "SPOS", "spos / talenty": "SPOS",
    "solid": "SOLID", "student related": "STUDENT RELATED BUS",
    "student related bus": "STUDENT RELATED BUS",
}

NOISE_PATTERNS = [
    re.compile(r"^---\s*PAGE\s*\d+\s*---", re.IGNORECASE),
    re.compile(r"TASK\s+ALLOCATION\s+REPORT", re.IGNORECASE),
    re.compile(r"GENERATED\s+BY", re.IGNORECASE),
    re.compile(r"^#\s+Name\s+Task", re.IGNORECASE),
    re.compile(r"Priority\s+Indicator", re.IGNORECASE),
    re.compile(r"^\s*l\s+(HIGH|MEDIUM|LOW)\s*l", re.IGNORECASE),
    re.compile(r"^\s*PAGE\s+\d+\s*$", re.IGNORECASE),
]

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────
def _normalise_team(raw: str) -> str:
    c = raw.lower().replace("/", " ").replace("-", " ").strip()
    for k, v in TEAM_NORM.items():
        if k in c:
            return v
    return raw.strip().upper()


def _lookup_member(raw_name: str):
    """Return (display_name, team, email). Always returns something."""
    key = raw_name.strip().lower()
    # exact match
    if key in MEMBER_MAP:
        t, e = MEMBER_MAP[key]
        return raw_name.strip().title(), t, e
    # first word match
    first = key.split()[0] if key.split() else key
    if first in MEMBER_MAP:
        t, e = MEMBER_MAP[first]
        return raw_name.strip().title(), t, e
    # two-word match
    words = key.split()
    if len(words) >= 2:
        two = " ".join(words[:2])
        if two in MEMBER_MAP:
            t, e = MEMBER_MAP[two]
            return raw_name.strip().title(), t, e
    return raw_name.strip().title(), "BUSINESS OPERATIONS", ""


def _normalise_priority(text: str) -> str:
    m = re.search(r"\b(high|medium|low)\b", text, re.IGNORECASE)
    if m:
        return m.group(1).capitalize()
    lower = text.lower()
    if any(k in lower for k in ("mandatory","complete","wrap up","submit","eod","urgent","asap")):
        return "High"
    if "leave" in lower:
        return "Low"
    return "Medium"


def _infer_status(description: str, priority: str) -> tuple[str, int]:
    lower = description.lower()
    if "leave" in lower:
        return "Leave", 0
    if "completed" in lower or "done" in lower:
        return "Completed", 100
    if priority == "High":
        return "In Progress", 50
    if any(k in lower for k in ("target", "call", "schedule", "wrap up", "continue", "visit")):
        return "In Progress", 40
    return "In Progress", 30


def _story_points(description: str, status: str) -> int:
    if status == "Leave":
        return 0
    n = description.count(",") + description.count("+") + description.count("—") + 1
    if n > 4 or len(description) > 200:
        return 8
    if n > 2 or len(description) > 100:
        return 5
    return 3


def _is_noise(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    for pat in NOISE_PATTERNS:
        if pat.search(s):
            return True
    return False


def _build_task(seq_id: int, raw_name: str, description: str, due_date: str,
                team_override: str = "") -> Task:
    # 1. Parse embedded status if present, e.g. [Status: In Progress]
    status_override = None
    status_m = re.search(r"\[Status:\s*(.+?)\]", description)
    if status_m:
        status_override = status_m.group(1).strip()
        description = description.replace(status_m.group(0), "").strip()

    # 2. Parse embedded due date if present, e.g. (Due: 29-May-26)
    due_date_override = None
    due_m = re.search(r"\(Due:\s*(.+?)\)", description)
    if due_m:
        due_date_override = due_m.group(1).strip()
        description = description.replace(due_m.group(0), "").strip()

    is_leave = "leave" in raw_name.lower() or "leave" in description.lower()
    name, team, email = _lookup_member(raw_name)
    if team_override and team == "BUSINESS OPERATIONS":
        team = team_override

    if is_leave:
        return Task(id=seq_id, name=name, team=team, taskTitle="Leave",
                    priority="Low", storyPoints=0, dueDate=due_date_override or due_date,
                    description="On leave", email=email,
                    status="Leave", completionPct=0)

    priority = _normalise_priority(description)
    
    if status_override:
        status = status_override
        # Determine completionPct based on status
        l_status = status.lower()
        if l_status in ("completed", "done"):
            pct = 100
        elif l_status == "in progress":
            pct = 50
        elif l_status in ("not started", "pending", "todo"):
            pct = 0
        else:
            _, pct = _infer_status(description, priority)
    else:
        status, pct = _infer_status(description, priority)

    sp = _story_points(description, status)

    # Build concise task title: first clause before comma / + / newline
    title = re.split(r"[,+\n]", description)[0].strip()
    if len(title) > 65:
        title = title[:62].rstrip() + "…"
    if not title:
        title = "Task"

    return Task(id=seq_id, name=name, team=team, taskTitle=title,
                priority=priority, storyPoints=sp, dueDate=due_date_override or due_date,
                description=description, email=email,
                status=status, completionPct=pct)



# ═══════════════════════════════════════════════════════════
# FORMAT DETECTORS
# ═══════════════════════════════════════════════════════════
def _is_tabular(raw: str) -> bool:
    """Structured report: rows like  N  Name  TaskTitle  High|Medium|Low  desc"""
    pat = re.compile(r"^\s*\d+\s+\S.+?\s+(High|Medium|Low)\b", re.IGNORECASE | re.MULTILINE)
    return len(pat.findall(raw)) >= 2


def _is_numbered_dotlist(raw: str) -> bool:
    """Daily allocation with leading numbers: '1. Name - ...' """
    pat = re.compile(r"^\s{0,8}\d+\.\s+\S", re.MULTILINE)
    return len(pat.findall(raw)) >= 2


# ═══════════════════════════════════════════════════════════
# PARSER 1 — Structured tabular report
# ═══════════════════════════════════════════════════════════
def _parse_tabular(lines: list[str], due_date: str) -> list[Task]:
    TASK_ROW = re.compile(r"^\s*(\d+)\s+(.+?)\s+(High|Medium|Low)\s+(.*)$", re.IGNORECASE)
    SECTION  = re.compile(r"Team:\s*(.+?)(?:\s*$)", re.IGNORECASE)

    tasks: list[Task] = []
    current_team = "BUSINESS OPERATIONS"
    seq_id = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if _is_noise(line):
            i += 1
            continue

        sm = SECTION.search(stripped)
        if sm:
            current_team = _normalise_team(sm.group(1).split("·")[0].strip())
            i += 1
            continue

        tm = TASK_ROW.match(line)
        if tm:
            name_title = tm.group(2).strip()
            priority   = tm.group(3).capitalize()
            desc       = tm.group(4).strip()

            # Collect continuation lines
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                nxt_s = nxt.strip()
                if not nxt_s:
                    j += 1
                    continue
                if TASK_ROW.match(nxt) or SECTION.search(nxt_s) or _is_noise(nxt):
                    break
                if nxt and not nxt.startswith(" ") and not nxt.startswith("\t"):
                    break
                desc += " " + nxt_s
                j += 1
            desc = re.sub(r"\s+", " ", desc).strip()

            # Split name_title → name + title (longest exact member-map match)
            words = name_title.split()
            best_name, best_title = name_title, ""
            for end in range(len(words), 0, -1):
                cand = " ".join(words[:end]).lower()
                if cand in MEMBER_MAP:
                    best_name  = " ".join(words[:end])
                    best_title = " ".join(words[end:])
                    break

            seq_id += 1
            task = _build_task(seq_id, best_name, desc, due_date, current_team)
            if best_title:
                task.task_title = best_title
            tasks.append(task)
            i = j
            continue

        i += 1

    return tasks


# ═══════════════════════════════════════════════════════════
# PARSER 2 — Numbered dot-list  "1. Name - description"
# ═══════════════════════════════════════════════════════════
def _parse_numbered(lines: list[str], due_date: str) -> list[Task]:
    TASK_PAT = re.compile(r"^\s{0,8}\d+\.\s+(.+)$")

    raw_blocks: list[tuple[str, str]] = []
    i = 0
    while i < len(lines):
        m = TASK_PAT.match(lines[i])
        if m and not _is_noise(lines[i]):
            content = m.group(1).strip()
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if TASK_PAT.match(nxt) or (nxt.strip() and not (nxt.startswith(" ") or nxt.startswith("\t"))):
                    break
                if nxt.strip():
                    content += " " + nxt.strip()
                j += 1

            # Split on first " - "
            sp = re.search(r"^(.+?)\s*-\s*(.+)$", content, re.DOTALL)
            if sp:
                raw_name = sp.group(1).strip().rstrip("-").strip()
                desc = sp.group(2).strip()
            else:
                raw_name, desc = "Unknown", content

            # Skip if name is too long (continuation block, no real name)
            if len(raw_name.split()) > 6 or len(raw_name) > 45:
                i = j
                continue

            raw_blocks.append((raw_name, desc))
            i = j
        else:
            i += 1

    return [_build_task(idx + 1, n, d, due_date) for idx, (n, d) in enumerate(raw_blocks)]


# ═══════════════════════════════════════════════════════════
# PARSER 3 — Plain  "Name - description"  (no numbers)
# ═══════════════════════════════════════════════════════════
def _parse_plain(lines: list[str], due_date: str) -> list[Task]:
    """
    Handles PDFs where tasks are plain lines like (3-space indent):
       Abhilash - shop community onboarding…
       continuation line
       Vinay shetty - full time hiring...
    Detection heuristic: stripped line starts with 1-5 capitalized words
    then ' -' or '–' then content.  Works for mixed-case names too.
    """
    # Match:  "   Name [Name2] - description"
    # Name part: 1-5 words where FIRST word starts with uppercase letter
    # Allow mixed case in subsequent words (e.g. "Vinay shetty")
    TASK_PAT = re.compile(
        r"^\s{0,8}"           # leading whitespace (0-8 spaces)
        r"([A-Z][A-Za-z]{1,20}"              # First word: starts uppercase
        r"(?:\s+[A-Za-z]{1,20}){0,4})"      # up to 4 more words (any case)
        r"\s*[-–]\s*"                         # dash separator
        r"(.+)$"                              # description (non-empty)
    )

    # Lines that signal a new section / header, NOT continuations
    SECTION_PAT = re.compile(
        r"^\s*(APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|"
        r"JANUARY|FEBRUARY|MARCH|SPRINT|TASKS?|TEAM|PAGE)\b",
        re.IGNORECASE,
    )

    raw_blocks: list[tuple[str, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip noise and empty
        if _is_noise(line) or not stripped:
            i += 1
            continue

        # Skip pure section headers
        if SECTION_PAT.match(stripped) and len(stripped.split()) <= 4:
            i += 1
            continue

        m = TASK_PAT.match(line)
        if m:
            raw_name = m.group(1).strip()
            desc     = m.group(2).strip()

            # Skip stubs — description too short (e.g. "Vasudha -" gives desc="")
            if not desc or len(desc) < 3:
                i += 1
                continue

            # Collect continuation lines: same or greater indent, no new task pattern
            leading = len(line) - len(line.lstrip())
            j = i + 1
            while j < len(lines):
                nxt   = lines[j]
                nxt_s = nxt.strip()
                # skip blanks silently
                if not nxt_s:
                    j += 1
                    continue
                nxt_leading = len(nxt) - len(nxt.lstrip())
                # If next line matches task pattern AND same indent → new task
                if TASK_PAT.match(nxt) and nxt_leading <= leading + 2:
                    break
                # section header → stop
                if SECTION_PAT.match(nxt_s) and len(nxt_s.split()) <= 4:
                    break
                if _is_noise(nxt):
                    break
                # Lines that are just a single bare name (no dash) → stop
                if re.match(r"^\s*[A-Z][A-Za-z\s]{1,30}\s*$", nxt) and len(nxt_s.split()) <= 3:
                    break
                desc += " " + nxt_s
                j += 1

            desc = re.sub(r"\s+", " ", desc).strip()
            if desc and len(desc) >= 3:
                raw_blocks.append((raw_name, desc))
            i = j
        else:
            i += 1

    return [_build_task(idx + 1, n, d, due_date)
            for idx, (n, d) in enumerate(raw_blocks)]


# ═══════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════
async def parse_tasks_with_llm(
    raw_text: str,
    page_count: int,
    method: str,
) -> ConversionResult:
    """
    Deterministic, fully offline parser.
    Auto-detects one of three formats:
      1. Structured table report (N  Name  Title  High|Medium|Low  Desc)
      2. Numbered dot-list      (1. Name - description…)
      3. Plain name-dash format (Name - description…)
    """
    lines = raw_text.splitlines()

    # ── Header / date parsing ─────────────────────────────
    sprint_title = "Sprint Tasks"
    organisation = "Akshara Enterprises"
    due_date     = date.today().strftime("%d-%b-%y")

    for line in lines:
        s = line.strip()
        if not s:
            continue

        # "Sprint 1-5 · 29 May 2026 · Akshara Enterprises"
        m = re.search(
            r"Sprint\s*([\d\-–]+)[^·]*·[^·]*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})[^·]*·\s*(.+)",
            s,
        )
        if m:
            sprint_title  = f"Sprint {m.group(1).strip()}"
            organisation  = m.group(5).strip()
            try:
                mo = [x.lower() for x in MONTHS].index(m.group(3)[:3].lower()) + 1
                due_date = f"{m.group(2)}-{MONTHS[mo-1]}-{m.group(4)[-2:]}"
            except ValueError:
                pass
            break

        # "TASK ALLOCATION - 29/5/26"  or  "APRIL TASKS"
        m2 = re.search(r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})", s)
        if m2:
            try:
                d_v, mo_v, yr_v = m2.group(1), int(m2.group(2)), m2.group(3)
                due_date = f"{d_v}-{MONTHS[mo_v-1]}-{yr_v[-2:]}"
            except (ValueError, IndexError):
                pass

        # Extract month name from header like "APRIL TASKS"
        mo_name_m = re.search(
            r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\b",
            s, re.IGNORECASE,
        )
        if mo_name_m and ("task" in s.lower() or "allocation" in s.lower()):
            month_name = mo_name_m.group(1).capitalize()
            try:
                mo_idx = [x.lower() for x in MONTHS].index(month_name[:3].lower()) + 1
                sprint_title = f"{month_name} Tasks"
                due_date = f"30-{MONTHS[mo_idx-1]}-{date.today().strftime('%y')}"
            except ValueError:
                pass

    # ── Choose parser ─────────────────────────────────────
    if _is_tabular(raw_text):
        print("[PARSER] Format: TABULAR")
        tasks = _parse_tabular(lines, due_date)
    elif _is_numbered_dotlist(raw_text):
        print("[PARSER] Format: NUMBERED DOT-LIST")
        tasks = _parse_numbered(lines, due_date)
    else:
        print("[PARSER] Format: PLAIN NAME-DASH")
        tasks = _parse_plain(lines, due_date)

    print(f"[PARSER] Extracted {len(tasks)} tasks from {page_count} pages.")

    return ConversionResult(
        sprintTitle=sprint_title,
        organisation=organisation,
        extractedDate=date.today().isoformat(),
        tasks=tasks,
        rawText=raw_text,
        pageCount=page_count,
        method=method,
        confidence=1.0,
    )
