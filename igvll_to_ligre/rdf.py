import unicodedata

from rdflib import Namespace

LEMON_ETY = Namespace("http://lari-datasets.ilc.cnr.it/lemonEty#")
LILA = Namespace("http://lila-erc.eu/ontologies/lila/")
ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")


def text_key(text):
    return unicodedata.normalize("NFC", str(text).strip())


def local_name(iri):
    return str(iri).rstrip("/").rsplit("/", 1)[-1].rsplit("#", 1)[-1]
