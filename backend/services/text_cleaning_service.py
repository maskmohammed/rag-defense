import re


def clean_text(text: str) -> str:
    """
    Nettoyage simple du texte :
    - supprime les espaces multiples
    - normalise les sauts de ligne
    - enlève les lignes vides répétées
    """
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)

    lines = [line.strip() for line in text.split("\n")]

    cleaned_lines = []
    previous_empty = False

    for line in lines:
        if line == "":
            if not previous_empty:
                cleaned_lines.append(line)
            previous_empty = True
        else:
            cleaned_lines.append(line)
            previous_empty = False

    text = "\n".join(cleaned_lines).strip()

    return text