import argparse
import csv
import sys
from pathlib import Path

REPOSITORY_DIRECTORY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_DIRECTORY))

from igvll_to_ligre import settings
from igvll_to_ligre.linking.decisions import Decision, reviewed_words
from igvll_to_ligre.pipeline import decision_paths
from igvll_to_ligre.sources.ligre import LemmaBank

COLUMNS = ["action", "ligre_id", "lemma", "pos", "gender", "new_lemma", "new_pos", "new_gender", "replaced_by",
           "reason", "evidence", "submitted_by"]


def read_arguments():
    parser = argparse.ArgumentParser(description="Write the LiGre changes in the decision files in review/ as a LiGre "
                                                 "corrections file.")
    parser.add_argument("--review-dir", type=Path, default=settings.DEFAULT_REVIEW_DIRECTORY)
    parser.add_argument("--ligre", type=Path, default=settings.DEFAULT_LIGRE_TURTLE,
                        help="the LiGre dump the decisions refer to")
    parser.add_argument("--output", type=Path, default=settings.LIGRE_CORRECTIONS_PATH)
    parser.add_argument("--submitted-by", default=settings.LINKSET_CREATORS[0]["iri"])
    return parser.parse_args()


def evidence_of(words):
    attested = "; ".join(sorted({f"{word.greek} (Latin {word.latin}, {word.etymon})" for word in words}))
    links = " ".join(sorted({word.lsj_link for word in words if word.lsj_link}))
    return f"IGVLL ({settings.IGVLL_REPOSITORY_URL}): {attested}" + (f"; LSJ {links}" if links else "")


def change_of(word):
    if word.decision is Decision.WR:
        return ("add-wr", word.ligre_id, word.spelling)
    if word.decision is Decision.CORRECT_LIGRE:
        return ("correct", word.ligre_id, word.spelling, word.pos, word.gender)
    if word.decision in (Decision.LV, Decision.NEW):
        return ("add", word.spelling, word.pos, word.gender, word.ligre_id if word.decision is Decision.LV else "")
    return None


def group_changes(words):
    groups, by_target, errors = {}, {}, []
    for word in words:
        change = change_of(word)
        if change is None:
            continue
        target = change[:2] if change[0] != "add" else change[:4]
        if target in by_target and by_target[target] != change:
            errors.append(f"{word.where}: another row gives {target} another change")
        by_target[target] = change
        groups.setdefault(change, []).append(word)
    if errors:
        raise SystemExit("\n".join(errors))
    return groups


def current(lemma_bank, ligre_id):
    lemma = lemma_bank.lemma(ligre_id)
    return {"ligre_id": ligre_id, "lemma": lemma.label, "pos": lemma.tag, "gender": lemma.gender}


def correction_rows(groups, lemma_bank, submitted_by):
    corrects, adds, written_forms, variants, skipped = [], [], [], [], []
    for change, words in groups.items():
        common = {"evidence": evidence_of(words), "submitted_by": submitted_by}
        kind = change[0]
        if kind == "add-wr":
            _, ligre_id, spelling = change
            if lemma_bank.has_written(ligre_id, spelling):
                skipped.append(f"add-wr {ligre_id} {spelling}")
                continue
            written_forms.append({"action": "add-wr", **current(lemma_bank, ligre_id), "new_lemma": spelling,
                                  "reason": "spelling missing from LiGre", **common})
        elif kind == "correct":
            _, ligre_id, spelling, pos, gender = change
            now = current(lemma_bank, ligre_id)
            if (now["lemma"], now["pos"], now["gender"]) == (spelling, pos, gender):
                skipped.append(f"correct {ligre_id} {spelling}")
                continue
            corrects.append({"action": "correct", **now, "new_lemma": spelling, "new_pos": pos, "new_gender": gender,
                             "reason": "wrong spelling in LiGre", **common})
        else:
            _, spelling, pos, gender, variant_of = change
            existing = lemma_bank.lemma_with(spelling, pos, gender)
            if existing:
                skipped.append(f"add {spelling} {pos}")
            else:
                adds.append({"action": "add", "new_lemma": spelling, "new_pos": pos, "new_gender": gender,
                             "reason": "lemma missing from LiGre", **common})
            if not variant_of:
                continue
            if existing and lemma_bank.are_variants(existing.lemma_id, variant_of):
                skipped.append(f"add-variant {variant_of} {spelling}")
                continue
            variants.append({"action": "add-variant", **current(lemma_bank, variant_of), "new_lemma": spelling,
                             "new_pos": pos, "new_gender": gender,
                             "reason": "another inflected form of the same word, used as lemma", **common})
    return corrects + adds + written_forms + variants, skipped


def main():
    arguments = read_arguments()
    lemma_bank = LemmaBank.from_turtle(arguments.ligre)
    words = reviewed_words(decision_paths(arguments.review_dir), lemma_bank)
    rows, skipped = correction_rows(group_changes(words), lemma_bank, arguments.submitted_by)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    with arguments.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, COLUMNS, delimiter="\t", lineterminator="\n", restval="")
        writer.writeheader()
        writer.writerows(rows)
    counts = {action: sum(row["action"] == action for row in rows) for action in ("correct", "add", "add-wr", "add-variant")}
    print(f"Wrote {len(rows)} LiGre corrections to {arguments.output}: "
          + ", ".join(f"{count} {action}" for action, count in counts.items())
          + f"; {len(skipped)} changes are already in the LiGre dump and left out")


if __name__ == "__main__":
    main()
