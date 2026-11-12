from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, FOAF, RDF, XSD

from .. import settings
from ..rdf import ONTOLEX

VOID = Namespace("http://rdfs.org/ns/void#")
DCAT_VERSION = URIRef(str(DCAT) + "version")
TURTLE_FORMAT = URIRef("http://www.w3.org/ns/formats/Turtle")
TURTLE_MEDIA_TYPE = URIRef("https://www.iana.org/assignments/media-types/text/turtle")
ANCIENT_GREEK = URIRef("http://lexvo.org/id/iso639-3/grc")


def integer(value):
    return Literal(value, datatype=XSD.integer)


def add_agent(graph, dataset, predicate, agent):
    node = URIRef(agent["iri"])
    graph.add((dataset, predicate, node))
    graph.add((node, RDF.type, FOAF.Agent))
    graph.add((node, FOAF.name, Literal(agent["name"])))


def describe_linkset(links):
    graph = Graph()
    for prefix, namespace in (("void", VOID), ("dcat", DCAT), ("dcterms", DCTERMS), ("foaf", FOAF),
                              ("ontolex", ONTOLEX), ("xsd", XSD)):
        graph.bind(prefix, namespace, override=True)
    linkset = URIRef(settings.LINKSET_IRI)
    distribution = URIRef(settings.LINKSET_DISTRIBUTION_IRI)
    download = URIRef(settings.LINKSET_DOWNLOAD_URL)
    license_document = URIRef(settings.LINKSET_LICENSE_URL)

    graph.add((linkset, RDF.type, VOID.Linkset))
    graph.add((linkset, RDF.type, DCAT.Dataset))
    graph.add((linkset, DCTERMS.title, Literal(settings.LINKSET_TITLE, lang="en")))
    graph.add((linkset, DCTERMS.description, Literal(settings.LINKSET_DESCRIPTION, lang="en")))
    for creator in settings.LINKSET_CREATORS:
        add_agent(graph, linkset, DCTERMS.creator, creator)
    add_agent(graph, linkset, DCTERMS.publisher, settings.LINKSET_PUBLISHER)
    graph.add((linkset, DCTERMS.license, license_document))
    graph.add((license_document, RDF.type, DCTERMS.LicenseDocument))
    graph.add((license_document, DCTERMS.title, Literal(settings.LINKSET_LICENSE_TITLE, lang="en")))
    graph.add((linkset, DCTERMS.language, ANCIENT_GREEK))
    graph.add((linkset, DCTERMS.source, URIRef(settings.IGVLL_REPOSITORY_URL)))
    graph.add((linkset, DCTERMS.isPartOf, URIRef(settings.KNOWLEDGE_BASE_IRI)))
    graph.add((linkset, DCAT_VERSION, Literal(settings.LINKSET_VERSION)))
    graph.add((linkset, DCAT.landingPage, URIRef(settings.LINKSET_REPOSITORY_URL)))
    graph.add((linkset, FOAF.homepage, URIRef(settings.KNOWLEDGE_BASE_HOMEPAGE)))

    graph.add((linkset, DCAT.distribution, distribution))
    graph.add((distribution, RDF.type, DCAT.Distribution))
    graph.add((distribution, DCTERMS.title, Literal("Linkset in Turtle", lang="en")))
    graph.add((distribution, DCAT.downloadURL, download))
    graph.add((distribution, DCAT.mediaType, TURTLE_MEDIA_TYPE))
    graph.add((distribution, DCTERMS.license, license_document))
    graph.add((linkset, VOID.dataDump, download))
    graph.add((linkset, VOID.feature, TURTLE_FORMAT))

    graph.add((linkset, VOID.subjectsTarget, URIRef(settings.IGVLL_LEXICON_IRI)))
    graph.add((linkset, VOID.objectsTarget, URIRef(settings.LIGRE_LEMMA_BANK_IRI)))
    graph.add((linkset, VOID.linkPredicate, ONTOLEX.canonicalForm))
    graph.add((linkset, VOID.vocabulary, URIRef(str(ONTOLEX))))
    graph.add((linkset, VOID.triples, integer(len(links))))
    graph.add((linkset, VOID.distinctSubjects, integer(len({etymon for etymon, _lemma in links}))))
    graph.add((linkset, VOID.distinctObjects, integer(len({lemma for _etymon, lemma in links}))))
    if links:
        graph.add((linkset, VOID.exampleResource, URIRef(links[0][0])))
    return graph
