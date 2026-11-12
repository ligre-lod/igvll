from .. import settings
from ..linking.matcher import BY_FORM
from ..rdf import local_name
from .description import describe_linkset


def linkset_links(matches):
    links = [(match.etymon.iri, match.lemma.iri) for match in matches if match.status == BY_FORM]
    return sorted(links, key=lambda link: int(local_name(link[0])))


def write_linkset(directory, links):
    directory.mkdir(parents=True, exist_ok=True)
    description = describe_linkset(links).serialize(format="turtle").rstrip("\n") + "\n"
    lines = [f"<{etymon}> ontolex:canonicalForm <{lemma}> ." for etymon, lemma in links]
    (directory / settings.LINKSET_FILENAME).write_text(description + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
    (directory / settings.DESCRIPTION_FILENAME).write_text(description, encoding="utf-8")
