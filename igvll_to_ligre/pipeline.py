import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from . import settings
from .linking.matcher import BY_FORM, COMPOUND, MATCHED, NONE, SEVERAL, THROUGH_LSJ, match
from .output.linkset import linkset_links, write_linkset
from .output.review import write_review_files
from .sources.igvll import read_etymons
from .sources.ligre import LemmaBank
from .sources.lsj import LsjIndex


@dataclass(frozen=True)
class PipelineOptions:
    igvll_turtle: Path
    ligre_turtle: Path
    data_directory: Path
    review_directory: Path
    output_directory: Path


def report(matches, links, options):
    statuses = Counter(match.status for match in matches)
    checked = [match for match in matches if match.status != COMPOUND]
    corrected = [match for match in checked if match.corrections]
    lsj_links = Counter(match.etymon.lsj_match for match in checked if match.status in (NONE, SEVERAL))
    review = options.review_directory
    print(f"{len(checked)} Greek words checked: {statuses[BY_FORM] + statuses[THROUGH_LSJ]} match one LiGre lemma "
          f"({statuses[BY_FORM]} by their form, {statuses[THROUGH_LSJ]} through their LSJ headword, listed in "
          f"{review / settings.LSJ_MATCHES_FILENAME}), {statuses[NONE]} none, {statuses[SEVERAL]} several; "
          f"{statuses[NONE] + statuses[SEVERAL]} listed in {review / settings.UNMATCHED_FILENAME}", file=sys.stderr)
    print(f"{sum(1 for match in matches if match.corrections)} IGVLL Greek words corrected ({len(corrected)} checked "
          f"words, of which {sum(1 for match in corrected if match.status in MATCHED)} now match one LiGre lemma), "
          f"listed in {review / settings.CORRECTIONS_FILENAME}", file=sys.stderr)
    print(f"{len(links)} etymons linked to their LiGre lemma in {options.output_directory / settings.LINKSET_FILENAME}, "
          f"described in {options.output_directory / settings.DESCRIPTION_FILENAME}", file=sys.stderr)
    print("LSJ links of the listed words: " + ", ".join(f"{count} {kind}" for kind, count in sorted(lsj_links.items())),
          file=sys.stderr)


def run_pipeline(options):
    etymons = read_etymons(options.igvll_turtle)
    lemma_bank = LemmaBank.from_turtle(options.ligre_turtle)
    lsj_index = LsjIndex.from_file(options.data_directory / settings.LSJ_INDEX_FILENAME)
    matches = [match(etymon, lemma_bank, lsj_index) for etymon in etymons]
    write_review_files(options.review_directory,
                       (settings.UNMATCHED_FILENAME, settings.CORRECTIONS_FILENAME, settings.LSJ_MATCHES_FILENAME),
                       matches, lsj_index)
    links = linkset_links(matches)
    write_linkset(options.output_directory, links)
    report(matches, links, options)
