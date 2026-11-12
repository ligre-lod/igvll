# Changelog

All notable changes to the IGVLL–LiGre linkset are listed here. Releases follow
[semantic versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-11-12

### Added
- The IGVLL–LiGre linkset (`ttl/IGVLL_LiGre.ttl`): 1,381 Greek words of the
  Index Graecorum Vocabulorum in Linguam Latinam linked to their LiGre lemma
  with `ontolex:canonicalForm`, for every Greek word that matches exactly one
  LiGre lemma by its form, after correcting IGVLL's OCR errors (Latin `v` and
  `o`) and grave accents. With its description (`void:Linkset`) as part of the
  LiGre Knowledge Base, also on its own in `ttl/IGVLL_LiGre_description.ttl`.
  The data is licensed under CC BY-NC-SA 4.0, as IGVLL; the code under MIT.
- Review files in `review/`: the Greek words that match no LiGre lemma or
  several (`unmatched.tsv`), those matched through the headword of their LSJ
  entry (`lsj_matches.tsv`), and the corrected words (`corrections.tsv`).
