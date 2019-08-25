from pandoc_styles import run_transform_filter


def latex(self):
    author = self.attributes["author"] if "author" in self.attributes else ""
    return ([f'\\dictum[{author}]{{',
             self.content,
             '}\n\n'
             '\\par\n\\vspace{\\baselineskip}\n\\par\n\\noindent'])


def html(self):
    author = f'<p class="EpigraphAuthor">{self.attributes["author"]}</p>\n' \
             if "author" in self.attributes else ""
    return (['<div class="Epigraph">',
             self.content,
             f'{author}</div>'])


if __name__ == "__main__":
    run_transform_filter(["epigraph"], latex=latex, html=html)
