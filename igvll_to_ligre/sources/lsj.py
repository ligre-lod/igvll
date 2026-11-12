import sys
import unicodedata
import urllib.request

from .. import settings
from ..rdf import text_key

LSJ_MARKS = {"-", "̄", "̆"}


class LsjIndex:
    def __init__(self, headwords):
        self.headwords = headwords

    @classmethod
    def from_file(cls, path):
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            print(f"downloading the LSJ index to {path}", file=sys.stderr)
            urllib.request.urlretrieve(settings.LSJ_INDEX_URL, path)
        headwords = {}
        with path.open(encoding="utf-8") as index:
            for line in index:
                fields = line.split("#")
                if len(fields) >= 2:
                    headwords[fields[0].strip()] = text_key(fields[1])
        return cls(headwords)

    def headword(self, urn):
        return self.headwords.get(urn.removeprefix(settings.LSJ_URN_PREFIX))


def lemma_form(headword):
    decomposed = unicodedata.normalize("NFD", headword)
    return unicodedata.normalize("NFC", "".join(char for char in decomposed if char not in LSJ_MARKS))


def viewer_link(urn):
    return settings.LSJ_VIEWER_URL.format(urn)
