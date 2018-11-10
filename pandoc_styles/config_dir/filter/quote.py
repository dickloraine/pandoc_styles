"""
Formats quotes with a title and author. The quote has to be inside a Code block with
the class "quote".
There are two optional attributes that can be set:
author: The author of the quote
title: The title/source of the quote

In addition you can set a style. Either global by adding the "quote-style" field to
the metadata style definition or by setting the style as a class in the code block.
The three styles are: "bottom", "top" and "one-line".
"""

from pandoc_styles import run_transform_filter


def all_formats(self):
    self.style = self.get_metadata("quote-style", "bottom")
    if "top" in self.classes:
        self.style = "top"
    elif "bottom" in self.classes:
        self.style = "bottom"
    elif "one-line" in self.classes:
        self.style = "one-line"


def latex(self):
    new = [r"\begin{quote}", "\n"]

    if self.style == "top" and ("title" in self.attributes or "author" in self.attributes):
        new.extend([r"\begin{center}", '\n'])
        if "title" in self.attributes:
            new.extend([r"\large\textbf{", self.attributes["title"], "}\n"])
        if "author" in self.attributes:
            new.extend(["\n", r"\normalsize\textit{", self.attributes["author"], "}\n"])
        new.extend([r"\end{center}", '\n'])

    new.extend([self.convert_text(), "\n"])

    if self.style == "one-line" and "author" in self.attributes \
                     and "title" in self.attributes:
        new.extend([r"\hfill \textit{", self.attributes["author"], "} --- ",
                    r"\textbf{", self.attributes["title"], "}\n"])
    elif self.style != "top":
        if "title" in self.attributes and "author" in self.attributes:
            new.extend(["\n", r"\hspace*{\fill}", r"\textbf{",
                        self.attributes["title"], "}", r"\linebreak"])
            new.extend([r"\hspace*{\fill}", r"\textit{",
                        self.attributes["author"], "}\n"])
        elif "author" in self.attributes:
            new.extend(["\n", r"\hspace*{\fill}", r"\textit{",
                        self.attributes["author"], "}\n"])
        elif "title" in self.attributes:
            new.extend(["\n", r"\hspace*{\fill}", r"\textbf{",
                        self.attributes["title"], "}\n"])

    new.extend([r"\end{quote}", "\n"])
    return new


def html(self):
    new = ['<div class="QuoteBlock">']
    if self.style == "top" and "title" in self.attributes:
        new.extend(["\n<p class='QuoteScourceTop'>",
                    self.attributes["title"], "</p>"])
    if self.style == "top" and "author" in self.attributes:
        new.extend(["\n<p class='QuoteAuthorTop'>",
                    self.attributes["author"], "</p>"])
    new.extend(["\n", self.convert_text()])
    if self.style == "one-line" and "author" in self.attributes and\
            "title" in self.attributes:
        new.extend(["\n<p class='QuoteSingle'><em>", self.attributes["author"], "</em>",
                    " &mdash; <strong>", self.attributes["title"], "</strong></p>"])
    elif self.style != "top":
        if "title" in self.attributes:
            new.extend(["\n", "<p class='QuoteScource'>", self.attributes["title"], "</p>"])
        if "author" in self.attributes:
            new.extend(["\n", "<p class='QuoteAuthor'>", self.attributes["author"], "</p>"])
    new.extend(['\n</div>'])
    return new


def other(self):
    new = []
    if self.style == "top" and "title" in self.attributes:
        new.extend(["> __", self.attributes["title"], "__\n"])
    if self.style == "top" and "author" in self.attributes:
        new.extend(["> _", self.elem.attributes["author"], "_\n"])
    if self.style == "top" and ("author" in self.attributes or "title" in self.attributes):
        new.extend(["> \n"])
    for line in self.text.split("\n"):
        new.extend(["> ", line, "\n"])
    if self.style == "one-line" and "author" in self.attributes and\
            "title" in self.attributes:
        new.extend(['>\n>_', self.attributes["author"], '_ --- __',
                    self.attributes["title"], '__', "\n"])
    elif self.style != "top":
        if "title" in self.attributes:
            new.extend(['>\n >__', self.attributes["title"], '__', "\n"])
        if "author" in self.attributes:
            new.extend(['>\n >_', self.attributes["author"], '_', "\n"])
    return new


if __name__ == "__main__":
    run_transform_filter(["quote"], latex, html, other, all_formats)
