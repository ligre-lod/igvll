from pathlib import Path

REPOSITORY_DIRECTORY = Path(__file__).resolve().parent.parent
LIGRE_LOD_DIRECTORY = REPOSITORY_DIRECTORY.parent

DEFAULT_IGVLL_TURTLE = LIGRE_LOD_DIRECTORY.parent / "index-graecorum-vocabulorum" / "IGVLL.ttl"
DEFAULT_LIGRE_TURTLE = LIGRE_LOD_DIRECTORY / "ligre-webinterface" / "ligre_lemmabank" / "ttl" / "ligre_lemmabank.ttl"

DEFAULT_DATA_DIRECTORY = REPOSITORY_DIRECTORY / "data"
DEFAULT_REVIEW_DIRECTORY = REPOSITORY_DIRECTORY / "review"
DEFAULT_OUTPUT_DIRECTORY = REPOSITORY_DIRECTORY / "ttl"

LSJ_INDEX_COMMIT = "6a7b603bdbe9a16536a094a86066700343c87752"
LSJ_INDEX_URL = f"https://raw.githubusercontent.com/Eumaeus/cite_lsj_cex/{LSJ_INDEX_COMMIT}/lsj_index.txt"
LSJ_INDEX_FILENAME = "lsj_index.txt"
LSJ_URN_PREFIX = "urn:cite2:hmt:lsj.chicago_md:"
LSJ_VIEWER_URL = "https://folio2.furman.edu/lsj/index.html?urn={}"

UNMATCHED_FILENAME = "unmatched.tsv"
CORRECTIONS_FILENAME = "corrections.tsv"
LSJ_MATCHES_FILENAME = "lsj_matches.tsv"
LINKSET_FILENAME = "IGVLL_LiGre.ttl"
DESCRIPTION_FILENAME = "IGVLL_LiGre_description.ttl"

LINKSET_VERSION = "0.1.0"
LINKSET_IRI = "https://w3id.org/ligre/data/linksets/IGVLL/id/linkset"
LINKSET_DISTRIBUTION_IRI = "https://w3id.org/ligre/data/linksets/IGVLL/id/distribution"
LINKSET_TITLE = "IGVLL–LiGre linkset"
LINKSET_DESCRIPTION = (
    "Links from the Greek source words (etymons) of the Index Graecorum Vocabulorum in Linguam Latinam (IGVLL), "
    "an index of Latin loanwords from Greek, to their lemmas in the LiGre Lemma Bank for Ancient Greek: one link "
    "for every Greek word whose spelling matches exactly one LiGre lemma."
)
LINKSET_REPOSITORY_URL = "https://github.com/ligre-lod/igvll"
LINKSET_DOWNLOAD_URL = (
    LINKSET_REPOSITORY_URL.replace("github.com", "raw.githubusercontent.com")
    + f"/v{LINKSET_VERSION}/ttl/{LINKSET_FILENAME}"
)
LINKSET_CREATORS = (
    {"name": "Paulien Lemay", "iri": "https://orcid.org/0009-0004-2388-9233"},
)
LINKSET_PUBLISHER = {"name": "Ghent University", "iri": "https://ror.org/00cv9y106"}
LINKSET_LICENSE_URL = "https://creativecommons.org/licenses/by-nc-sa/4.0/"
LINKSET_LICENSE_TITLE = "Creative Commons Attribution Non Commercial Share Alike 4.0 International"
KNOWLEDGE_BASE_IRI = "https://w3id.org/ligre/data/id/KnowledgeBase"
KNOWLEDGE_BASE_HOMEPAGE = "https://ligre-lod.github.io/"
LIGRE_LEMMA_BANK_IRI = "https://w3id.org/ligre/data/id/lemma/LemmaBank"
IGVLL_LEXICON_IRI = "http://lila-erc.eu/data/lexicalResources/IGVLL/Lexicon"
IGVLL_REPOSITORY_URL = "https://github.com/CIRCSE/index-graecorum-vocabulorum"
