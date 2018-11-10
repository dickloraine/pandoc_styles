from pandoc_styles import run_transform_filter


def latex(self):
    author = self.attributes["author"] if "author" in self.attributes else ""
    return (f'\\dictum[{author}]'
            f'{{{self.convert_text()}}}'
            f'\n\\par\n\\vspace{{\\baselineskip}}\n'
            f'\\par\n\\noindent\n')


def html(self):
    author = f'\n<p class="EpigraphAuthor">{self.attributes["author"]}</p>' \
             if "author" in self.attributes else ""
    return (f'<div class="Epigraph">\n'
            f'{self.convert_text()}'
            f'{author}\n</div>')


if __name__ == "__main__":
    run_transform_filter(["epigraph"], latex, html)
