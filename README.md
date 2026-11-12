# IGVLL to LiGre

The [Index Graecorum Vocabulorum in Linguam Latinam](https://github.com/CIRCSE/index-graecorum-vocabulorum)
(IGVLL) lists Latin loanwords from Greek. Its Latin words are linked to LiLa lemmas, but its Greek words
(`lemonEty:Etymon`) are only strings. This repository links them to lemmas of the LiGre Lemma Bank, and lists the
ones it cannot link.

## Running

```bash
uv run igvll
```

It reads IGVLL and the LiGre lemma bank from local copies, downloads the LSJ index on the first run, and writes:

| File | Content |
|---|---|
| `ttl/IGVLL_LiGre.ttl` | the linkset: every Greek word that matches one LiGre lemma by its form, linked to that lemma, with the description of the linkset |
| `ttl/IGVLL_LiGre_description.ttl` | the description of the linkset on its own |
| `review/unmatched.tsv` | the Greek words that match no LiGre lemma, or several |
| `review/lsj_matches.tsv` | the Greek words matched to a LiGre lemma through the headword of their LSJ entry |
| `review/corrections.tsv` | the Greek words corrected before matching |

It prints how many words it checked, how many match one LiGre lemma (by their form or through LSJ), none or
several, how many it corrected, how many it linked and how the listed words link to LSJ.

| Option | Default |
|---|---|
| `--igvll` | `IGVLL.ttl` in a clone of the IGVLL repository next to `ligre-lod/` (`../../index-graecorum-vocabulorum/IGVLL.ttl`) |
| `--ligre` | the lemma bank dump in `../ligre-webinterface/ligre_lemmabank/ttl/ligre_lemmabank.ttl` |
| `--data-dir` | `data/`, which holds the LSJ index of [cite_lsj_cex](https://github.com/Eumaeus/cite_lsj_cex) at a fixed commit |
| `--review-dir` | `review/` |
| `--output-dir` | `ttl/` |

## How the Greek words are matched

Every etymon with an `rdfs:label` is a Greek word. A compound written `ἅμαξα + ἄγω` is not matched as a whole: its
parts are etymons of their own and are matched one by one.

1. **Corrections.** Two kinds of error in IGVLL's Greek are corrected first:
   - Latin letters that look like Greek ones, from the OCR: `v` for `ν` and `o` for `ο` (`vάρκισσος` → `νάρκισσος`);
   - a grave accent on a word that stands on its own, which becomes an acute, as in a dictionary form
     (`αὐτὸς` → `αὐτός`, `ἓρπυλλον` → `ἕρπυλλον`); in a phrase (`τὰ πάντα`) the grave accent is correct and stays.
2. **By form.** The (corrected) word matches when it is the `ontolex:writtenRep` of exactly one LiGre lemma, both in
   Unicode NFC. IGVLL has no part of speech for its Greek words, so the match is on the spelling only. Deprecated
   LiGre lemmas (`owl:deprecated true`) are left out.
3. **Through LSJ.** A word that does not match one LiGre lemma by its form still matches when IGVLL links it to an
   LSJ entry with `skos:exactMatch` and the headword of that entry, without LSJ's hyphens and vowel-length marks,
   matches exactly one LiGre lemma (`γέρρα` → LSJ `γέρρον`, `γλυκίζειν` → LSJ `γλυκίζω`). A `broad` or `related` LSJ
   link is not used: its headword is another word than IGVLL's (`βαλλιστήρ` → `βάλλω`).

## Linkset

`ttl/IGVLL_LiGre.ttl` links every Greek word matched by its form (step 2) to its LiGre lemma, with the property IGVLL
itself uses for the citation form of an etymon:

```turtle
<http://lila-erc.eu/data/lexicalResources/IGVLL/id/etymon/1> ontolex:canonicalForm <https://w3id.org/ligre/data/id/lemma/27> .
```

The words matched through LSJ and the unmatched words are not linked yet.

The file starts with the description of the linkset
(<https://w3id.org/ligre/data/linksets/IGVLL/id/linkset>), which
`ttl/IGVLL_LiGre_description.ttl` also holds on its own: a `void:Linkset` from IGVLL
(`void:subjectsTarget`) to the LiGre Lemma Bank (`void:objectsTarget`) with `ontolex:canonicalForm`
(`void:linkPredicate`), its number of links and of distinct etymons and lemmas, and its Dublin Core and DCAT
metadata: title, creator, publisher, licence, version, and the download URL of `ttl/IGVLL_LiGre.ttl` in the release.
It is part of the LiGre Knowledge Base. The metadata is set in `igvll_to_ligre/settings.py` (`LINKSET_*`).

## Release

A release is tagged `vX.Y.Z` with the version in `LINKSET_VERSION` (`igvll_to_ligre/settings.py`), so that the
download URL in the description points to the linkset of that release, and its changes are listed in
`CHANGELOG.md`. The LiGre endpoint serves a release once its two files are copied into `ttl/linksets/` of the
[lemma bank](https://github.com/ligre-lod/ligre_lemmabank) (see *Linksets in the endpoint* in its README).

Releases are archived on Zenodo through the GitHub integration, with the metadata in `.zenodo.json`; the citation
metadata is in `CITATION.cff`.

## Licence

The data (the linkset in `ttl/` and the review tables in `review/`) is derived from IGVLL and licensed, like IGVLL,
under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (see [LICENSE-DATA.md](LICENSE-DATA.md)).
The code is licensed under the MIT License (see [LICENSE](LICENSE)).

## Review files

`review/unmatched.tsv` lists first the words that match several LiGre lemmas and then those that match none:

| Column | Content |
|---|---|
| `matches` | `several` or `none` |
| `greek` | the Greek word as written in IGVLL |
| `corrected` | the corrected Greek word, which is the one matched; empty if IGVLL's needs no correction |
| `latin` | the Latin loanword; for a part of a compound or a cognate, the loanword of its compound or cognate |
| `etymon` | the IRI of the etymon in IGVLL |
| `ligre_lemmas` | for `several`, every matching LiGre lemma: written representation, part of speech and id |
| `lsj_match` | how IGVLL links the word to LSJ: `exact` (`skos:exactMatch`), `broad` (`skos:broadMatch`, the nearest LSJ entry), `related` (`skos:relatedMatch`, a related LSJ entry) or `none`; with several, the first in this order |
| `lsj_urn` | the CITE URN of that LSJ entry, as given in IGVLL |
| `lsj_headword` | the LSJ headword of that URN, as written in the index of cite_lsj_cex (with the vowel lengths and hyphens of LSJ) |
| `lsj_link` | for an `exact` link, the LSJ entry in the [LSJ viewer of Furman University](https://folio2.furman.edu/lsj/), opened by its URN |

`review/lsj_matches.tsv` has the columns `greek`, `corrected`, `lsj_headword`, `ligre_lemma` (written
representation, part of speech and id), `latin`, `etymon` and `lsj_link`.

`review/corrections.tsv` lists every corrected word, also when it then matches one LiGre lemma, so that the
corrections can be reported to IGVLL. Its columns are `greek`, `corrected`, `corrections` (`Latin letters`,
`grave accent`), `latin`, `etymon` and `ligre_matches`: the number of LiGre lemmas the corrected word matches (empty
for a compound, which is not matched as a whole).

## Code

`igvll_to_ligre/` is the pipeline (`pipeline.py`), run by `__main__.py`, with its paths and pinned sources in
`settings.py`:

- `sources/` reads the inputs: `igvll.py` the Greek words of IGVLL with their Latin word and LSJ links, `ligre.py`
  the LiGre lemmas by written representation, `lsj.py` the LSJ headwords by URN;
- `linking/` matches the words: `corrections.py` corrects IGVLL's errors, `matcher.py` matches a word by its form or
  through LSJ;
- `output/` writes the results: `linkset.py` the Turtle linkset, `description.py` its description, `review.py`
  the review files;
- `rdf.py` holds the namespaces and the helpers for IRIs and text shared by these modules.
# igvll
# igvll
