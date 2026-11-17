import sys

from .. import settings
from ..linking.decisions import linked_lemma
from ..linking.matcher import BY_FORM
from ..rdf import local_name
from .description import describe_linkset


def automatic_links(matches):
    return {match.etymon.iri: match.lemma.iri for match in matches if match.status == BY_FORM}


def reviewed_links(words, lemma_bank, automatic):
    links, pending = {}, []
    for word in words:
        lemma = linked_lemma(word, lemma_bank)
        if lemma is None:
            if word.decision.value in ("lv", "new"):
                pending.append(word)
            continue
        if word.etymon in automatic:
            if automatic[word.etymon] != lemma.iri:
                print(f"Warning: {word.where}: {word.greek} already matches LiGre lemma "
                      f"{local_name(automatic[word.etymon])} by its form; the decision is not used", file=sys.stderr)
            continue
        links[word.etymon] = lemma.iri
    return links, pending


def sorted_links(links):
    return sorted(links.items(), key=lambda link: int(local_name(link[0])))


def write_linkset(directory, links):
    directory.mkdir(parents=True, exist_ok=True)
    description = describe_linkset(links).serialize(format="turtle").rstrip("\n") + "\n"
    lines = [f"<{etymon}> ontolex:canonicalForm <{lemma}> ." for etymon, lemma in links]
    (directory / settings.LINKSET_FILENAME).write_text(description + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
    (directory / settings.DESCRIPTION_FILENAME).write_text(description, encoding="utf-8")
