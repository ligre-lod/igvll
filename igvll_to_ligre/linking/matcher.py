from dataclasses import dataclass
from typing import Optional

from ..sources.igvll import Etymon
from ..sources.ligre import LigreLemma
from ..sources.lsj import lemma_form
from .corrections import correct

BY_FORM = "one"
THROUGH_LSJ = "through LSJ"
NONE = "none"
SEVERAL = "several"
COMPOUND = "compound"
MATCHED = (BY_FORM, THROUGH_LSJ)


@dataclass(frozen=True)
class Match:
    etymon: Etymon
    corrected: str
    corrections: tuple
    status: str
    lemmas: tuple
    lsj_headwords: tuple = ()
    lsj_lemma: Optional[LigreLemma] = None

    @property
    def lemma(self):
        if self.status == BY_FORM:
            return self.lemmas[0]
        return self.lsj_lemma


def match_through_lsj(etymon, lemma_bank, lsj_index):
    if etymon.lsj_match != "exact":
        return (), None
    headwords = tuple(word for word in map(lsj_index.headword, etymon.lsj_urns) if word)
    lemmas = set().union(*(lemma_bank.lemmas(lemma_form(word)) for word in headwords)) if headwords else set()
    return headwords, (lemmas.pop() if len(lemmas) == 1 else None)


def match(etymon, lemma_bank, lsj_index):
    corrected, corrections = correct(etymon.greek)
    lemmas = tuple(lemma_bank.lemmas(corrected))
    if etymon.compound:
        return Match(etymon, corrected, corrections, COMPOUND, lemmas)
    if len(lemmas) == 1:
        return Match(etymon, corrected, corrections, BY_FORM, lemmas)
    headwords, lsj_lemma = match_through_lsj(etymon, lemma_bank, lsj_index)
    if lsj_lemma is not None:
        return Match(etymon, corrected, corrections, THROUGH_LSJ, lemmas, headwords, lsj_lemma)
    return Match(etymon, corrected, corrections, SEVERAL if lemmas else NONE, lemmas)
