import unicodedata

LATIN_LETTERS = "Latin letters"
GRAVE_ACCENT = "grave accent"
LATIN_LOOKALIKES = str.maketrans({"v": "ν", "o": "ο"})
GRAVE, ACUTE = "̀", "́"


def correct(greek):
    corrections = []
    corrected = greek.translate(LATIN_LOOKALIKES)
    if corrected != greek:
        corrections.append(LATIN_LETTERS)
    decomposed = unicodedata.normalize("NFD", corrected)
    if GRAVE in decomposed and " " not in corrected:
        corrected = unicodedata.normalize("NFC", decomposed.replace(GRAVE, ACUTE))
        corrections.append(GRAVE_ACCENT)
    return corrected, tuple(corrections)
