from pandoc_styles import run_filter, CodeBlock


def numbered(elem, doc):
    if type(elem) == CodeBlock:
        elem.classes.append("numberLines")


if __name__ == "__main__":
    run_filter(numbered)
