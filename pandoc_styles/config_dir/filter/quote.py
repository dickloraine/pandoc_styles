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

from pandoc_styles import run_transform_filter, BlockQuote


def all_formats(self):
    self.style = self.get_metadata("quote-style", "bottom")
    if "top" in self.classes:
        self.style = "top"
    elif "bottom" in self.classes:
        self.style = "bottom"
    elif "one-line" in self.classes:
        self.style = "one-line"


def latex(self):
    new = [r"\begin{quote}"]

    if self.style == "top" and ("title" in self.attributes or "author" in self.attributes):
        new.append(r'\begin{center}')
        if "title" in self.attributes:
            new.append(f'\\large\\textbf{{{self.attributes["title"]}}}')
        if "author" in self.attributes:
            new.append(f'\\normalsize\\textit{{{self.attributes["author"]}}}')
        new.append(r"\end{center}")

    new.extend(self.content)

    if self.style == "one-line" and "author" in self.attributes \
                     and "title" in self.attributes:
        new.append(f'\\hfill \\textit{{{self.attributes["author"]}}} --- '
                   f'\\textbf{{{self.attributes["title"]}}}')
    elif self.style != "top":
        if "title" in self.attributes and "author" in self.attributes:
            new.append(f'\\hspace*{{\\fill}}\\textbf{{{self.attributes["title"]}}}')
            new.append(f'\\hspace*{{\\fill}}\\textit{{{self.attributes["author"]}}}')
        elif "author" in self.attributes:
            new.append(f'\\hspace*{{\\fill}}\\textit{{{self.attributes["author"]}}}')
        elif "title" in self.attributes:
            new.append(f'\\hspace*{{\\fill}}\\textbf{{{self.attributes["title"]}}}')

    new.append(r"\end{quote}")
    return new


def html(self):
    new = ['<div class="QuoteBlock">']
    if self.style == "top" and "title" in self.attributes:
        new.append(f'<p class="QuoteScourceTop">{self.attributes["title"]}</p>')
    if self.style == "top" and "author" in self.attributes:
        new.append(f'<p class="QuoteAuthorTop">{self.attributes["author"]}</p>')
    new.extend(self.content)
    if self.style == "one-line" and "author" in self.attributes and\
            "title" in self.attributes:
        new.append(f'<p class="QuoteSingle"><em>{self.attributes["author"]}</em>&mdash;'
                   f'<strong>{self.attributes["title"]}</strong></p>')
    elif self.style != "top":
        if "title" in self.attributes:
            new.append(f'<p class="QuoteScource">{self.attributes["title"]}</p>')
        if "author" in self.attributes:
            new.append(f'<p class="QuoteAuthor">{self.attributes["author"]}</p>')
    new.append('</div>')
    return new


def other(self):
    new = []
    if self.style == "top" and "title" in self.attributes:
        new.append(f'> __{self.attributes["title"]}__')
    if self.style == "top" and "author" in self.attributes:
        new.append(f'> _{self.elem.attributes["author"]}_')
    if self.style == "top" and ("author" in self.attributes or "title" in self.attributes):
        new.append("> ")

    new.append(self.transform(BlockQuote))

    if self.style == "one-line" and "author" in self.attributes and\
            "title" in self.attributes:
        new.append(f'>\n>_{self.attributes["author"]}_ --- '
                   f'__{self.attributes["title"]}__')
    elif self.style != "top":
        if "title" in self.attributes:
            new.append(f'>__{self.attributes["title"]}__')
        if "author" in self.attributes:
            new.append(f'>_{self.attributes["author"]}_')
    return new


if __name__ == "__main__":
    run_transform_filter(["quote"], all_formats, other, latex=latex, html=html)
