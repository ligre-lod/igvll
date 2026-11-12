import csv

from ..linking.matcher import COMPOUND, NONE, SEVERAL, THROUGH_LSJ
from ..sources.lsj import viewer_link

UNMATCHED_COLUMNS = ["matches", "greek", "corrected", "latin", "etymon", "ligre_lemmas", "lsj_match", "lsj_urn",
                     "lsj_headword", "lsj_link"]
CORRECTION_COLUMNS = ["greek", "corrected", "corrections", "latin", "etymon", "ligre_matches"]
LSJ_MATCH_COLUMNS = ["greek", "corrected", "lsj_headword", "ligre_lemma", "latin", "etymon", "lsj_link"]
UNMATCHED_ORDER = {SEVERAL: 0, NONE: 1}


def write_tsv(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def corrected_form(match):
    return match.corrected if match.corrections else ""


def unmatched_rows(matches, lsj_index):
    rows = []
    for match in matches:
        if match.status not in UNMATCHED_ORDER:
            continue
        etymon = match.etymon
        links = [viewer_link(urn) for urn in etymon.lsj_urns] if etymon.lsj_match == "exact" else []
        rows.append([match.status, etymon.greek, corrected_form(match), etymon.latin, etymon.iri,
                     " ".join(lemma.describe() for lemma in match.lemmas), etymon.lsj_match,
                     " ".join(etymon.lsj_urns), " ".join(lsj_index.headword(urn) or "?" for urn in etymon.lsj_urns),
                     " ".join(links)])
    return sorted(rows, key=lambda row: (UNMATCHED_ORDER[row[0]], row[1], row[4]))


def correction_rows(matches):
    rows = [[match.etymon.greek, match.corrected, ", ".join(match.corrections), match.etymon.latin, match.etymon.iri,
             "" if match.status == COMPOUND else len(match.lemmas)]
            for match in matches if match.corrections]
    return sorted(rows, key=lambda row: (row[0], row[4]))


def lsj_match_rows(matches):
    rows = [[match.etymon.greek, corrected_form(match), " ".join(match.lsj_headwords), match.lsj_lemma.describe(),
             match.etymon.latin, match.etymon.iri, " ".join(viewer_link(urn) for urn in match.etymon.lsj_urns)]
            for match in matches if match.status == THROUGH_LSJ]
    return sorted(rows, key=lambda row: (row[0], row[5]))


def write_review_files(directory, filenames, matches, lsj_index):
    unmatched, corrections, lsj_matches = filenames
    write_tsv(directory / unmatched, UNMATCHED_COLUMNS, unmatched_rows(matches, lsj_index))
    write_tsv(directory / corrections, CORRECTION_COLUMNS, correction_rows(matches))
    write_tsv(directory / lsj_matches, LSJ_MATCH_COLUMNS, lsj_match_rows(matches))
