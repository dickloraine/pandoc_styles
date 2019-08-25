"""
Includes other markdown files given in a Code block with the class "include". One
file path per line.
"""
from os.path import isfile
from pandoc_styles import run_pandoc_styles_filter, CodeBlock, file_read


def include(self):
    new = "\n".join(file_read(line) for line in self.text.splitlines()
                    if not line[0] == "#" and isfile(line))
    return new


if __name__ == "__main__":
    run_pandoc_styles_filter(include, CodeBlock, "include")
