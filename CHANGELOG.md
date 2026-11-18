# Changelog

All notable changes to the IGVLL–LiGre linkset are listed here. Releases follow
[semantic versioning](https://semver.org/).

## [Unreleased]

### Changed
- A `PROPN` decided as `new` may be without a gender, for indeclinable names,
  which LiGre now accepts; a `NOUN` still needs one.

## [0.2.0] - 2026-11-17

### Added
- 75 links after review: Greek words matched to one LiGre lemma through the
  headword of their LSJ entry, whose form differs from the lemma only in
  diacritics or capitals (52), is an infinitive (4), a plural (14) or a
  participle (2), or has an OCR error (3). The linkset now links 1,456 Greek
  words: 1,381 by their form and 75 after review.
- A review workflow like that of papygreek-to-ligre: the words matched through
  their LSJ headword (`review/decisions_lsj.tsv`) and those that match several
  LiGre lemmas (`review/decisions_ambiguous.tsv`) are decision files, read back
  by every run, with the decisions `link`, `wr`, `lv`, `correct-ligre`, `new`
  and `reject`. Decided words are linked in the linkset; `lv` and `new` once
  LiGre has the lemma.
- `scripts/export_ligre_corrections.py`, which writes the LiGre changes of the
  decisions as `ligre_corrections/igvll-review.tsv`, in the format of the lemma
  bank's corrections.
- `review/check_sample.tsv`: the manual check of a random sample of 100 links.

### Changed
- The files in `review/` are named by their role: `decisions_` files are filled
  in by hand, `list_` files are only written. `unmatched.tsv` is now
  `list_unmatched.tsv` (only the words that match none; those that match
  several are in `decisions_ambiguous.tsv`), `corrections.tsv` is
  `list_corrected_forms.tsv`, and `lsj_matches.tsv` is `decisions_lsj.tsv`.
- The description of the linkset also mentions the words linked after review.

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
