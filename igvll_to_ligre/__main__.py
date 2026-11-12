import argparse
from pathlib import Path

from . import settings
from .pipeline import PipelineOptions, run_pipeline


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="python -m igvll_to_ligre",
        description="Link the Greek words of IGVLL to the LiGre lemma bank and list those that do not match.",
    )
    parser.add_argument("--igvll", type=Path, default=settings.DEFAULT_IGVLL_TURTLE, help="IGVLL.ttl")
    parser.add_argument("--ligre", type=Path, default=settings.DEFAULT_LIGRE_TURTLE, help="the LiGre lemma bank dump")
    parser.add_argument("--data-dir", type=Path, default=settings.DEFAULT_DATA_DIRECTORY,
                        help="holds the downloaded LSJ index")
    parser.add_argument("--review-dir", type=Path, default=settings.DEFAULT_REVIEW_DIRECTORY,
                        help="where the review files are written")
    parser.add_argument("--output-dir", type=Path, default=settings.DEFAULT_OUTPUT_DIRECTORY,
                        help="where the linkset is written")
    return parser.parse_args()


def main():
    arguments = parse_arguments()
    run_pipeline(PipelineOptions(
        igvll_turtle=arguments.igvll,
        ligre_turtle=arguments.ligre,
        data_directory=arguments.data_dir,
        review_directory=arguments.review_dir,
        output_directory=arguments.output_dir,
    ))


if __name__ == "__main__":
    main()
