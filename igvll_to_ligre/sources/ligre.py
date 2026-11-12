from collections import defaultdict
from dataclasses import dataclass

from rdflib import Graph, Literal
from rdflib.namespace import OWL, RDF

from ..rdf import LILA, ONTOLEX, local_name, text_key


@dataclass(frozen=True)
class LigreLemma:
    iri: str
    written: str
    pos: str

    @property
    def lemma_id(self):
        return local_name(self.iri)

    def describe(self):
        return f"{self.written} {self.pos} {self.lemma_id}"


def by_id(lemma):
    return int(lemma.lemma_id) if lemma.lemma_id.isdigit() else lemma.lemma_id


class LemmaBank:
    def __init__(self, lemmas_by_written):
        self.lemmas_by_written = lemmas_by_written

    @classmethod
    def from_turtle(cls, path):
        graph = Graph().parse(path, format="turtle")
        lemmas_by_written = defaultdict(set)
        for lemma in graph.subjects(RDF.type, LILA.Lemma):
            if (lemma, OWL.deprecated, Literal(True)) in graph:
                continue
            pos = "/".join(sorted(local_name(p) for p in graph.objects(lemma, LILA.hasPOS))) or "?"
            for written in graph.objects(lemma, ONTOLEX.writtenRep):
                lemmas_by_written[text_key(written)].add(LigreLemma(str(lemma), text_key(written), pos))
        return cls(dict(lemmas_by_written))

    def lemmas(self, written):
        return sorted(self.lemmas_by_written.get(written, ()), key=by_id)
