"""
Includes other markdown files given in a Code block with the class "include. One
file path per line.
"""
from os.path import isfile
from pandoc_styles import run_filter, CodeBlock, convert_text, file_read


def include(elem, doc):
    if isinstance(elem, CodeBlock) and "include" in elem.classes:
        new = "\n".join(file_read(line) for line in elem.text.splitlines()
                        if not line[0] == "#" and isfile(line))
        return convert_text(new)


if __name__ == "__main__":
    run_filter(include)
