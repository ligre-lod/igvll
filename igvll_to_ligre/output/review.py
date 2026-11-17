import csv

from .. import settings
from ..linking.decisions import read_rows, updated_rows, write_rows
from ..linking.matcher import COMPOUND, NONE, SEVERAL, THROUGH_LSJ
from ..sources.lsj import viewer_link

UNMATCHED_COLUMNS = ["greek", "corrected", "latin", "etymon", "lsj_match", "lsj_urn", "lsj_headword", "lsj_link"]
CORRECTED_COLUMNS = ["greek", "corrected", "corrections", "latin", "etymon", "ligre_matches"]


def write_tsv(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def corrected_form(match):
    return match.corrected if match.corrections else ""


def exact_lsj_links(etymon):
    return " ".join(viewer_link(urn) for urn in etymon.lsj_urns) if etymon.lsj_match == "exact" else ""


def unmatched_rows(matches, lsj_index):
    rows = []
    for match in matches:
        if match.status != NONE:
            continue
        etymon = match.etymon
        rows.append([etymon.greek, corrected_form(match), etymon.latin, etymon.iri, etymon.lsj_match,
                     " ".join(etymon.lsj_urns), " ".join(lsj_index.headword(urn) or "?" for urn in etymon.lsj_urns),
                     exact_lsj_links(etymon)])
    return sorted(rows, key=lambda row: (row[0], row[3]))


def corrected_rows(matches):
    rows = [[match.etymon.greek, match.corrected, ", ".join(match.corrections), match.etymon.latin, match.etymon.iri,
             "" if match.status == COMPOUND else len(match.lemmas)]
            for match in matches if match.corrections]
    return sorted(rows, key=lambda row: (row[0], row[4]))


def candidate_row(match, ligre_lemma, candidates, lsj_index):
    etymon = match.etymon
    return {"greek": etymon.greek, "ligre_lemma": ligre_lemma, "decision": "", "new_lemma": "", "new_pos": "",
            "new_gender": "", "note": "", "corrected": corrected_form(match), "latin": etymon.latin,
            "candidates": " ".join(lemma.describe() for lemma in candidates),
            "lsj_headword": " ".join(lsj_index.headword(urn) or "?" for urn in etymon.lsj_urns),
            "lsj_link": exact_lsj_links(etymon), "etymon": etymon.iri}


def lsj_candidates(matches, lsj_index):
    return [candidate_row(match, match.lsj_lemma.lemma_id, [match.lsj_lemma], lsj_index)
            for match in matches if match.status == THROUGH_LSJ]


def ambiguous_candidates(matches, lsj_index):
    return [candidate_row(match, "", match.lemmas, lsj_index) for match in matches if match.status == SEVERAL]


def update_decisions(path, candidates):
    write_rows(path, updated_rows(read_rows(path), candidates))


def write_review_files(directory, matches, lsj_index):
    update_decisions(directory / settings.LSJ_DECISIONS_FILENAME, lsj_candidates(matches, lsj_index))
    update_decisions(directory / settings.AMBIGUOUS_DECISIONS_FILENAME, ambiguous_candidates(matches, lsj_index))
    write_tsv(directory / settings.UNMATCHED_LIST_FILENAME, UNMATCHED_COLUMNS, unmatched_rows(matches, lsj_index))
    write_tsv(directory / settings.CORRECTED_LIST_FILENAME, CORRECTED_COLUMNS, corrected_rows(matches))
