"""
Formats poems. The poem has to be inside a Code block with the class "poem".
There are many optional attributes that can be set:
author: The author of the poem
title: The title of the poem
altverse: true or false
poemlines: true or false

In addition you can set a style. Either global by adding the "quote-style" field to
the style definition or by setting the style as a class in the code block.
The three styles are: "bottom", "top" and "one-line".
"""
import re
from pandoc_styles import run_transform_filter, strip_html_tag


def all_formats(self):
    self.get_pandoc_styles_metadata()
    self.style = self.cfg.get("poem-style", "bottom")
    if "top" in self.classes:
        self.style = "top"
    elif "bottom" in self.classes:
        self.style = "bottom"
    elif "one-line" in self.classes:
        self.style = "one-line"


def latex(self):
    new = []
    if self.style == "top" and "title" in self.attributes:
        new.extend([r"\poemtitle*{", self.attributes["title"], "}\n"])

    if "versewidth" in self.attributes:
        new.extend([r"\settowidth{\versewidth}{", self.attributes["versewidth"],
                    "}", "\n", r"\begin{verse}[\versewidth]", "\n"])
    elif "no_versewidth" in self.classes:
        new.extend([r'\begin{verse}', "\n"])
    else:
        lst = []
        for line in self.text.split("\n"):
            if line and line[0] not in ["!", "[", "{"]:
                lst.append((len(line), line))
        _, max_line = max(lst)
        new.extend([r"\settowidth{\versewidth}{", max_line,
                    "}\n", r"\begin{verse}[\versewidth]", "\n"])

    if "poemlines" in self.attributes:
        new.extend([r"\poemlines{", self.attributes["poemlines"], "}\n"])

    if "altverse" in self.classes:
        new.extend([r"\begin{altverse}", "\n"])

    for line in self.text.split("\n"):
        if line == "":
            if "altverse" in self.classes:
                new.extend([r"\\!", r"\end{altverse}", "\n\n", r"\begin{altverse}", "\n"])
            else:
                new.extend([r"\\!", "\n"])
        else:
            new.extend([self.convert_text(line).strip("\n"), r"\\", "*", "\n"])
    new.extend([r"\\!", "\n"])

    if self.style == "top" and "author" in self.attributes:
        new.extend([r"\hspace*{\fill}", r"\rightskip2em \textit{",
                    self.attributes["author"], "}\n"])

    elif self.style == "one-line" and "author" in self.attributes and\
            "title" in self.attributes:
        new.extend([r"\hfill \rightskip2em \textit{", self.attributes["author"],
                    "} --- ", r"\textbf{", self.attributes["title"], "}\n"])
    elif self.style != "top":
        if "title" in self.attributes and "author" in self.attributes:
            new.extend([r"\hspace*{\fill}", r"\rightskip2em \textbf{",
                        self.attributes["title"], "}", r"\linebreak"])
            new.extend([r"\hspace*{\fill}", r"\rightskip2em \textit{",
                        self.attributes["author"], "}\n"])
        elif "author" in self.attributes:
            new.extend([r"\hspace*{\fill}", r"\rightskip2em \textit{",
                        self.attributes["author"], "}\n"])
        elif "title" in self.attributes:
            new.extend([r"\hspace*{\fill}", r"\rightskip2em \textbf{",
                        self.attributes["title"], "}\n"])

    if "altverse" in self.classes:
        new.extend([r"\end{altverse}", "\n"])

    if "poemlines" in self.attributes:
        new.extend([r"\poemlines{0", "}\n"])

    new.append(r"\end{verse}")

    new = ''.join(new)
    new = re.sub(r'\\\\\*\n\\\\!', '\\\\\!\n', new)
    return new


def html(self):
    new = ['<div class="Poem">']
    if self.style == "top" and "title" in self.attributes:
        new.extend(["\n<p class='PoemTitleTop'>", self.attributes["title"], "</p>"])
    if self.style == "top" and "author" in self.attributes:
        new.extend(["\n<p class='PoemAuthorTop'>", self.attributes["author"], "</p>"])
    new.extend(['\n<div class="Stanza">'])
    i = 0
    for line in self.text.split("\n"):
        if line == "":
            if "altverse" in self.classes:
                i = 1
            new.extend(['\n</div>\n<p>&nbsp;</p>\n<div class="Stanza">'])
        elif "altverse" in self.classes:
            if i % 2 == 0:
                new.extend(["\n", self.convert_text(line)])
            else:
                new.extend(["\n<p class='PoemAltverse'>",
                            strip_html_tag(self.convert_text(line)), "</p>"])
        else:
            new.extend(["\n", self.convert_text(line)])
        i += 1
    new.extend(['\n</div>'])
    if self.style == "one-line" and "author" in self.attributes and\
            "title" in self.attributes:
        new.extend(["\n<p class='PoemSingle'><em>", self.attributes["author"], "</em>",
                    " &mdash; <strong>", self.attributes["title"], "</strong></p>"])
    elif self.style != "top":
        if "title" in self.attributes:
            new.extend(["\n<p class='PoemTitle'>", self.attributes["title"], "</p>"])
        if "author" in self.attributes:
            new.extend(["\n<p class='PoemAuthor'>", self.attributes["author"], "</p>"])
    new.extend(['\n</div>'])
    return new


def other(self):
    new = []
    if self.style == "top" and "title" in self.attributes:
        new.extend(["| __", self.attributes["title"], "__\n"])
    if self.style == "top" and "author" in self.attributes:
        new.extend(["| _", self.attributes["author"], "_\n"])
    if self.style == "top" and ("author" in self.attributes or "title" in self.attributes):
        new.extend(["| \n"])
    i = 0
    for line in self.text.split("\n"):
        if line == "":
            if "altverse" in self.classes:
                i = 1
            new.extend(['| ', "\n"])
        elif "altverse" in self.classes:
            if i % 2 == 0:
                new.extend(['| ', line, "\n"])
            else:
                new.extend(['|      ', line, "\n"])
        else:
            new.extend(['| ', line, "\n"])
        i += 1
    if self.style == "one-line" and "author" in self.attributes and\
            "title" in self.attributes:
        new.extend(['| \n| _', self.attributes["author"], '_ --- __',
                    self.attributes["title"], '__\n'])
    elif self.style != "top":
        if "title" in self.attributes:
            new.extend(['| \n| __', self.attributes["title"], '__\n'])
        if "author" in self.attributes:
            new.extend(['| \n| _', self.attributes["author"], '_\n'])

    new = ''.join(new)
    new = re.sub(r'\|\s\|', '|', new, flags=re.MULTILINE)
    return new


if __name__ == "__main__":
    run_transform_filter(["poem"], latex, html, other, all_formats)
