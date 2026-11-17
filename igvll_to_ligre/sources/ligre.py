from collections import defaultdict
from dataclasses import dataclass

from rdflib import Graph, Literal
from rdflib.namespace import OWL, RDF

from ..rdf import LILA, ONTOLEX, local_name, text_key

UNIVERSAL_TAG_BY_LILA_PART_OF_SPEECH = {
    "adjective": "ADJ", "adposition": "ADP", "adverb": "ADV", "auxiliary": "AUX", "coordinating_conjunction": "CCONJ",
    "determiner": "DET", "interjection": "INTJ", "noun": "NOUN", "numeral": "NUM", "particle": "PART",
    "pronoun": "PRON", "proper_noun": "PROPN", "punctuation": "PUNCT", "subordinating_conjunction": "SCONJ",
    "symbol": "SYM", "verb": "VERB", "other": "X",
}
UNIVERSAL_TAGS = frozenset(UNIVERSAL_TAG_BY_LILA_PART_OF_SPEECH.values())
GENDERED_TAGS = frozenset({"NOUN", "PROPN"})
GENDER_BY_LILA_GENDER = {"masculine": "m", "feminine": "f", "neuter": "n"}


@dataclass(frozen=True)
class LigreLemma:
    iri: str
    written: str
    pos: str
    label: str = ""
    tags: frozenset = frozenset()
    genders: frozenset = frozenset()

    @property
    def lemma_id(self):
        return local_name(self.iri)

    @property
    def tag(self):
        return sorted(self.tags)[0] if self.tags else ""

    @property
    def gender(self):
        return sorted(self.genders)[0] if self.tag in GENDERED_TAGS and self.genders else ""

    def describe(self):
        gender = "/".join(sorted(self.genders))
        return f"{self.written} {self.pos}{' ' + gender if gender else ''} {self.lemma_id}"


def by_id(lemma):
    return int(lemma.lemma_id) if lemma.lemma_id.isdigit() else lemma.lemma_id


class LemmaBank:
    def __init__(self, lemmas_by_written, lemmas_by_id=None, written_by_id=None, variants_by_id=None):
        self.lemmas_by_written = lemmas_by_written
        self.lemmas_by_id = lemmas_by_id or {}
        self.written_by_id = written_by_id or {}
        self.variants_by_id = variants_by_id or {}

    @classmethod
    def from_turtle(cls, path):
        graph = Graph().parse(path, format="turtle")
        lemmas_by_written = defaultdict(set)
        lemmas_by_id, written_by_id, variants_by_id = {}, defaultdict(set), defaultdict(set)
        for lemma in graph.subjects(RDF.type, LILA.Lemma):
            if (lemma, OWL.deprecated, Literal(True)) in graph:
                continue
            parts_of_speech = sorted(local_name(p) for p in graph.objects(lemma, LILA.hasPOS))
            pos = "/".join(parts_of_speech) or "?"
            tags = frozenset(UNIVERSAL_TAG_BY_LILA_PART_OF_SPEECH.get(p, "X") for p in parts_of_speech)
            genders = frozenset(GENDER_BY_LILA_GENDER[local_name(g)] for g in graph.objects(lemma, LILA.hasGender)
                                if local_name(g) in GENDER_BY_LILA_GENDER)
            lemma_id = local_name(lemma)
            for variant in graph.objects(lemma, LILA.lemmaVariant):
                variants_by_id[lemma_id].add(local_name(variant))
            written_forms = sorted(text_key(written) for written in graph.objects(lemma, ONTOLEX.writtenRep))
            for written in written_forms:
                entry = LigreLemma(str(lemma), written, pos, written_forms[0], tags, genders)
                lemmas_by_written[written].add(entry)
                written_by_id[lemma_id].add(written)
                lemmas_by_id.setdefault(lemma_id, entry)
        return cls(dict(lemmas_by_written), lemmas_by_id, dict(written_by_id), dict(variants_by_id))

    def lemmas(self, written):
        return sorted(self.lemmas_by_written.get(written, ()), key=by_id)

    def lemma(self, lemma_id):
        return self.lemmas_by_id.get(lemma_id)

    def lemma_with(self, written, tag, gender):
        for lemma in self.lemmas(written):
            if tag in lemma.tags and (tag not in GENDERED_TAGS or not gender or gender in lemma.genders):
                return lemma
        return None

    def has_written(self, lemma_id, written):
        return written in self.written_by_id.get(lemma_id, ())

    def are_variants(self, lemma_id, other_id):
        return other_id in self.variants_by_id.get(lemma_id, ()) or lemma_id in self.variants_by_id.get(other_id, ())
