# IGVLL to LiGre

The [Index Graecorum Vocabulorum in Linguam Latinam](https://github.com/CIRCSE/index-graecorum-vocabulorum)
(IGVLL) lists Latin loanwords from Greek. Its Latin words are linked to LiLa lemmas, but its Greek words
(`lemonEty:Etymon`) are only strings. This repository links them to lemmas of the LiGre Lemma Bank, and lists the
ones it cannot link.

## Running

```bash
uv run igvll-to-ligre
```

It reads IGVLL and the LiGre lemma bank from local copies, downloads the LSJ index on the first run, reads the
decisions in `review/`, and writes:

| File | Content |
|---|---|
| `ttl/IGVLL_LiGre.ttl` | the linkset: every Greek word that matches one LiGre lemma by its form, and every Greek word linked after review, linked to its lemma, with the description of the linkset |
| `ttl/IGVLL_LiGre_description.ttl` | the description of the linkset on its own |
| `review/decisions_lsj.tsv` | decision file: the Greek words matched to one LiGre lemma through the headword of their LSJ entry |
| `review/decisions_ambiguous.tsv` | decision file: the Greek words that match several LiGre lemmas |
| `review/list_unmatched.tsv` | list: the Greek words that match no LiGre lemma |
| `review/list_corrected_forms.tsv` | list: the Greek words corrected before matching |

The names in `review/` say what a file is for: a `decisions_` file is filled in by hand and read back by every run
(see *Review workflow*), a `list_` file is only written by the pipeline and is overwritten by every run, and
`check_sample.tsv` is the manual check of a random sample of 100 automatic links, with its judgement and date.

It prints how many words it checked, how many match one LiGre lemma by their form, through LSJ, several or none,
how many it corrected, how many decisions it read, how many words it linked and how the words that match none or
several link to LSJ.

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

`ttl/IGVLL_LiGre.ttl` links every Greek word matched by its form (step 2), and every Greek word linked by a decision
(see *Review workflow*), to its LiGre lemma, with the property IGVLL itself uses for the citation form of an etymon:

```turtle
<http://lila-erc.eu/data/lexicalResources/IGVLL/id/etymon/1> ontolex:canonicalForm <https://w3id.org/ligre/data/id/lemma/27> .
```

The words matched through LSJ (step 3) and those that match several LiGre lemmas are linked only once they are
decided; the words that match none are not linked.

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

## Review workflow

The workflow is the one of [papygreek-to-ligre](https://github.com/ligre-lod/papygreek) (`decisions_wr_lv.tsv`),
with the same decisions. The pipeline writes two decision files in `review/`:

- `decisions_lsj.tsv`: the words that match one LiGre lemma through their LSJ headword (step 3), with that lemma
  prefilled in `ligre_lemma`;
- `decisions_ambiguous.tsv`: the words that match several LiGre lemmas, with the candidates in `candidates` and
  `ligre_lemma` empty.

Every run adds the words that are still open, keeps everything you filled in, and drops undecided rows that are no
longer open; undecided rows come first. A row you have not filled in is ignored; a row that is filled in but
incomplete or wrong is skipped with a warning that names the row, so you can decide part of a file and run again.
A row for another word, such as one in `list_unmatched.tsv`, can be added to a decision file by hand: a decided row
is kept even when the pipeline does not list the word.

| Column | Content |
|---|---|
| `greek` | the Greek word as written in IGVLL |
| `ligre_lemma` | the id of the LiGre lemma the decision is about; prefilled in `decisions_lsj.tsv` |
| `decision` | empty (not decided yet) or one of the values below |
| `new_lemma` | for `wr`, `lv`, `correct-ligre` and `new`: the spelling LiGre gets; empty means IGVLL's (corrected) word |
| `new_pos`, `new_gender` | for `new`: the part of speech (Universal Dependencies, `PROPN` for a name) and, for `NOUN`, the gender (`m`, `f`, `n`), which a `PROPN` may leave empty when it has none (an indeclinable name); for `lv` and `correct-ligre` only to deviate from the LiGre lemma's |
| `note` | free text |
| `corrected` | the corrected Greek word, which is the one matched; empty if IGVLL's needs no correction |
| `latin` | the Latin loanword; for a part of a compound or a cognate, the loanword of its compound or cognate |
| `candidates` | the matching LiGre lemmas: written representation, part of speech, gender and id |
| `lsj_headword` | the headword of the LSJ entry IGVLL links the word to, as written in the index of cite_lsj_cex (with the vowel lengths and hyphens of LSJ) |
| `lsj_link` | for an `exact` link, the LSJ entry in the [LSJ viewer of Furman University](https://folio2.furman.edu/lsj/), opened by its URN |
| `etymon` | the IRI of the etymon in IGVLL, which identifies the row |

| `decision` | Meaning | What happens |
|---|---|---|
| `link` | the LiGre lemma is the word's lemma; IGVLL's form is another form of it or a spelling error (γλυκίζειν, γλυκίζω) | the word links to `ligre_lemma` |
| `wr` | IGVLL's spelling is a WR of `ligre_lemma` (αἴθρα, αἴθρη) | LiGre gets the spelling (`add-wr`); the word links to `ligre_lemma` |
| `lv` | IGVLL's word is an LV of `ligre_lemma` (γαυσάπης, γαύσαπος) | LiGre gets it as a new lemma, a lemma variant of `ligre_lemma` (`add` and `add-variant`); the word links to it once LiGre has it |
| `correct-ligre` | LiGre's spelling is wrong, IGVLL's is right | LiGre corrects the spelling of `ligre_lemma` (`correct`); the word links to it |
| `new` | a word that LiGre lacks | LiGre gets `new_lemma` (or IGVLL's word) as a new lemma with `new_pos` and `new_gender` (`add`); leave `ligre_lemma` empty; the word links to it once LiGre has it |
| `reject` | the match is wrong | the word is not linked |

WR and LV follow Swaelens, Mambrini & Passarotti (2026): a WR differs only in spelling and leaves the inflection
unchanged (θάλασσα, θάλαττα); an LV is another inflected form of the same word that can serve as lemma (γράφω,
γράφομαι).

### Submitting the changes to LiGre

`scripts/export_ligre_corrections.py` writes the LiGre changes of both decision files (`wr`, `lv`,
`correct-ligre`, `new`) as `ligre_corrections/igvll-review.tsv`, in the format of the lemma bank's
`data/corrections/` (see its `data/corrections/README.md`), with IGVLL and the LSJ entry as evidence. It leaves out
the changes the LiGre dump already has, so the decision files can stay as they are. Copy the file into a branch of
the lemma bank and run its check:

```bash
uv run python scripts/export_ligre_corrections.py
cp ligre_corrections/igvll-review.tsv ../ligre-webinterface/ligre_lemmabank/data/corrections/YYYY-MM-DD_igvll-review.tsv
```

Once a LiGre release contains the changes, the next run links the words of `lv` and `new`.

## Lists

`review/list_unmatched.tsv` lists the words that match no LiGre lemma, with the columns `greek`, `corrected`,
`latin`, `etymon`, `lsj_match` (how IGVLL links the word to LSJ: `exact` (`skos:exactMatch`), `broad`
(`skos:broadMatch`, the nearest LSJ entry), `related` (`skos:relatedMatch`, a related LSJ entry) or `none`; with
several, the first in this order), `lsj_urn` (the CITE URN of that LSJ entry, as given in IGVLL), `lsj_headword`
and `lsj_link`.

`review/list_corrected_forms.tsv` lists every corrected word, also when it then matches one LiGre lemma, so that the
corrections can be reported to IGVLL. Its columns are `greek`, `corrected`, `corrections` (`Latin letters`,
`grave accent`), `latin`, `etymon` and `ligre_matches`: the number of LiGre lemmas the corrected word matches (empty
for a compound, which is not matched as a whole).

## Code

`igvll_to_ligre/` is the pipeline (`pipeline.py`), run by `__main__.py`, with its paths and pinned sources in
`settings.py`:

- `sources/` reads the inputs: `igvll.py` the Greek words of IGVLL with their Latin word and LSJ links, `ligre.py`
  the LiGre lemmas by written representation, `lsj.py` the LSJ headwords by URN;
- `linking/` matches the words: `corrections.py` corrects IGVLL's errors, `matcher.py` matches a word by its form or
  through LSJ, `decisions.py` reads, checks and updates the decision files;
- `output/` writes the results: `linkset.py` the Turtle linkset, `description.py` its description, `review.py`
  the decision files and the lists;
- `rdf.py` holds the namespaces and the helpers for IRIs and text shared by these modules.

`scripts/export_ligre_corrections.py` writes the LiGre changes of the decisions (see *Submitting the changes to
LiGre*).
# igvll
# igvll
