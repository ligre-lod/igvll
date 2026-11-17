import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from . import settings
from .linking.decisions import reviewed_words
from .linking.matcher import BY_FORM, COMPOUND, MATCHED, NONE, SEVERAL, THROUGH_LSJ, match
from .output.linkset import automatic_links, reviewed_links, sorted_links, write_linkset
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


def decision_paths(review_directory):
    return [review_directory / settings.LSJ_DECISIONS_FILENAME, review_directory / settings.AMBIGUOUS_DECISIONS_FILENAME]


def report(matches, words, automatic, reviewed, pending, options):
    statuses = Counter(match.status for match in matches)
    checked = [match for match in matches if match.status != COMPOUND]
    corrected = [match for match in checked if match.corrections]
    lsj_links = Counter(match.etymon.lsj_match for match in checked if match.status in (NONE, SEVERAL))
    review = options.review_directory
    print(f"{len(checked)} Greek words checked: {statuses[BY_FORM]} match one LiGre lemma by their form; "
          f"{statuses[THROUGH_LSJ]} match one through their LSJ headword ({review / settings.LSJ_DECISIONS_FILENAME}); "
          f"{statuses[SEVERAL]} match several ({review / settings.AMBIGUOUS_DECISIONS_FILENAME}); "
          f"{statuses[NONE]} match none ({review / settings.UNMATCHED_LIST_FILENAME})", file=sys.stderr)
    print(f"{sum(1 for match in matches if match.corrections)} IGVLL Greek words corrected ({len(corrected)} checked "
          f"words, of which {sum(1 for match in corrected if match.status in MATCHED)} now match one LiGre lemma), "
          f"listed in {review / settings.CORRECTED_LIST_FILENAME}", file=sys.stderr)
    decisions = Counter(word.decision.value for word in words)
    print(f"{len(words)} decisions" + (": " + ", ".join(f"{count} {name}" for name, count in sorted(decisions.items()))
                                       if words else "")
          + f"; {len(pending)} wait for a lemma LiGre will add", file=sys.stderr)
    print(f"{len(automatic) + len(reviewed)} etymons linked to their LiGre lemma ({len(automatic)} by their form, "
          f"{len(reviewed)} after review) in {options.output_directory / settings.LINKSET_FILENAME}, described in "
          f"{options.output_directory / settings.DESCRIPTION_FILENAME}", file=sys.stderr)
    print("LSJ links of the words that match none or several: "
          + ", ".join(f"{count} {kind}" for kind, count in sorted(lsj_links.items())), file=sys.stderr)


def run_pipeline(options):
    etymons = read_etymons(options.igvll_turtle)
    lemma_bank = LemmaBank.from_turtle(options.ligre_turtle)
    lsj_index = LsjIndex.from_file(options.data_directory / settings.LSJ_INDEX_FILENAME)
    matches = [match(etymon, lemma_bank, lsj_index) for etymon in etymons]
    write_review_files(options.review_directory, matches, lsj_index)
    words = reviewed_words(decision_paths(options.review_directory), lemma_bank)
    automatic = automatic_links(matches)
    reviewed, pending = reviewed_links(words, lemma_bank, automatic)
    write_linkset(options.output_directory, sorted_links({**automatic, **reviewed}))
    report(matches, words, automatic, reviewed, pending, options)
