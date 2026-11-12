from collections import defaultdict
from dataclasses import dataclass

from rdflib import Graph
from rdflib.namespace import RDF, RDFS, SKOS

from ..rdf import LEMON_ETY, ONTOLEX, text_key

LSJ_LINK_TYPES = [("exact", SKOS.exactMatch), ("broad", SKOS.broadMatch), ("related", SKOS.relatedMatch)]


@dataclass(frozen=True)
class Etymon:
    iri: str
    greek: str
    latin: str
    compound: bool
    lsj_match: str
    lsj_urns: tuple


def is_subterm(predicate):
    return str(predicate).endswith("decomp:subterm") or str(predicate).endswith("decomp#subterm")


def latin_words(graph):
    latin = defaultdict(set)
    for entry in graph.subjects(RDF.type, ONTOLEX.LexicalEntry):
        word = graph.value(entry, RDFS.label)
        for etymology in graph.objects(entry, LEMON_ETY.etymology):
            for etymon in graph.objects(etymology, LEMON_ETY.etymon):
                latin[etymon].add(str(word))
    related = defaultdict(set)
    for subject, predicate, obj in graph:
        if is_subterm(predicate) or predicate == LEMON_ETY.cognate:
            related[obj].add(subject)
            related[subject].add(obj)
    for etymon in list(related):
        seen, todo = set(), [etymon]
        while todo:
            current = todo.pop()
            if current in seen:
                continue
            seen.add(current)
            todo += related[current]
        if not latin[etymon]:
            latin[etymon] = set().union(*(latin[e] for e in seen))
    return latin


def lsj_link(graph, etymon):
    for match, predicate in LSJ_LINK_TYPES:
        urns = tuple(sorted(str(urn) for urn in graph.objects(etymon, predicate)))
        if urns:
            return match, urns
    return "none", ()


def read_etymons(path):
    graph = Graph().parse(path, format="turtle")
    latin = latin_words(graph)
    compounds = {subject for subject, predicate, _object in graph if is_subterm(predicate)}
    etymons = []
    for etymon in sorted(graph.subjects(RDF.type, LEMON_ETY.Etymon), key=str):
        label = graph.value(etymon, RDFS.label)
        if label is None:
            continue
        lsj_match, lsj_urns = lsj_link(graph, etymon)
        etymons.append(Etymon(str(etymon), text_key(label), " ".join(sorted(latin.get(etymon, ()))),
                              etymon in compounds, lsj_match, lsj_urns))
    return etymons
