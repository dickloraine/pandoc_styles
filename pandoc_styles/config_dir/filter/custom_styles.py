from pandoc_styles import run_transform_filter


def all_formats(self):
    self.classes.remove("custom")


def latex(self):
    return [f'\\begin{{{self.classes[0]}}}',
            self.content,
            f'\\end{{{self.classes[0]}}}']

if __name__ == "__main__":
    run_transform_filter(["custom"], all_formats, latex=latex)
