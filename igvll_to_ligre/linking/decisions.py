import csv
import sys
from dataclasses import dataclass
from enum import Enum

from ..rdf import text_key
from ..sources.ligre import GENDERED_TAGS, UNIVERSAL_TAGS

DECISION_COLUMNS = ["greek", "ligre_lemma", "decision", "new_lemma", "new_pos", "new_gender", "note"]
INFORMATION_COLUMNS = ["corrected", "latin", "candidates", "lsj_headword", "lsj_link", "etymon"]
COLUMNS = [*DECISION_COLUMNS, *INFORMATION_COLUMNS]
KEPT_COLUMNS = ["ligre_lemma", "decision", "new_lemma", "new_pos", "new_gender", "note"]
GENDERS = {"m", "f", "n"}


class Decision(Enum):
    LINK = "link"
    WR = "wr"
    LV = "lv"
    CORRECT_LIGRE = "correct-ligre"
    NEW = "new"
    REJECT = "reject"


NEEDS_LIGRE_LEMMA = {Decision.LINK, Decision.WR, Decision.LV, Decision.CORRECT_LIGRE}
LINKS_NOW = {Decision.LINK, Decision.WR, Decision.CORRECT_LIGRE}


class DecisionError(ValueError):
    pass


@dataclass(frozen=True)
class ReviewedWord:
    where: str
    decision: Decision
    etymon: str
    greek: str
    latin: str
    lsj_link: str
    ligre_id: str = ""
    spelling: str = ""
    pos: str = ""
    gender: str = ""


def read_rows(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as decision_file:
        reader = csv.DictReader(decision_file, delimiter="\t")
        rows = [{column: (row.get(column) or "").strip() for column in COLUMNS} for row in reader]
        if rows and (reader.fieldnames or [])[:len(DECISION_COLUMNS)] != DECISION_COLUMNS:
            raise DecisionError(f"{path}: expected the columns {COLUMNS}, found {reader.fieldnames}")
    return rows


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as decision_file:
        writer = csv.DictWriter(decision_file, COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def updated_rows(existing_rows, candidate_rows):
    existing = {row["etymon"]: row for row in existing_rows}
    keys = set()
    rows = []
    for candidate in candidate_rows:
        keys.add(candidate["etymon"])
        row = {**candidate}
        if candidate["etymon"] in existing:
            row.update({column: existing[candidate["etymon"]][column] for column in KEPT_COLUMNS})
        rows.append(row)
    rows += [row for key, row in existing.items() if key not in keys and row["decision"]]
    return sorted(rows, key=lambda row: (bool(row["decision"]), row["greek"], row["etymon"]))


def check_analysis(where, pos, gender):
    if pos not in UNIVERSAL_TAGS:
        raise DecisionError(f"{where}: new_pos is one of {sorted(UNIVERSAL_TAGS)}, not {pos!r}")
    if (pos in GENDERED_TAGS) != bool(gender) or (gender and gender not in GENDERS):
        raise DecisionError(f"{where}: NOUN and PROPN need new_gender m, f or n; other parts of speech none")


def reviewed_word(where, row, lemma_bank):
    values = [decision.value for decision in Decision]
    if row["decision"] not in values:
        raise DecisionError(f"{where}: decision is one of {values} or empty, not {row['decision']!r}")
    decision = Decision(row["decision"])
    ligre_id = row["ligre_lemma"]
    lemma = lemma_bank.lemma(ligre_id) if ligre_id else None
    if decision in NEEDS_LIGRE_LEMMA and lemma is None:
        raise DecisionError(f"{where}: {decision.value} needs the id of a LiGre lemma in ligre_lemma")
    if decision is Decision.NEW and ligre_id:
        raise DecisionError(f"{where}: new adds a lemma that is not in LiGre, so leave ligre_lemma empty")
    common = {"where": where, "decision": decision, "etymon": row["etymon"], "greek": row["greek"],
              "latin": row["latin"], "lsj_link": row["lsj_link"]}
    if decision is Decision.REJECT:
        return ReviewedWord(**common)
    if decision is Decision.LINK:
        return ReviewedWord(**common, ligre_id=ligre_id)
    spelling = text_key(row["new_lemma"] or row["corrected"] or row["greek"])
    if decision is Decision.WR:
        return ReviewedWord(**common, ligre_id=ligre_id, spelling=spelling)
    if decision is Decision.NEW:
        check_analysis(where, row["new_pos"], row["new_gender"])
        return ReviewedWord(**common, spelling=spelling, pos=row["new_pos"], gender=row["new_gender"])
    pos = row["new_pos"] or lemma.tag
    gender = row["new_gender"] if row["new_pos"] else lemma.gender
    check_analysis(where, pos, gender)
    return ReviewedWord(**common, ligre_id=ligre_id, spelling=spelling, pos=pos, gender=gender)


def reviewed_words(paths, lemma_bank):
    words = []
    for path in paths:
        for line, row in enumerate(read_rows(path), start=2):
            if not row["decision"]:
                continue
            where = f"{path.name}:{line}"
            try:
                words.append(reviewed_word(where, row, lemma_bank))
            except DecisionError as error:
                print(f"Warning: {error}; the row is skipped until it is complete", file=sys.stderr)
    return words


def linked_lemma(word, lemma_bank):
    if word.decision in LINKS_NOW:
        return lemma_bank.lemma(word.ligre_id)
    if word.decision in (Decision.LV, Decision.NEW):
        return lemma_bank.lemma_with(word.spelling, word.pos, word.gender)
    return None
