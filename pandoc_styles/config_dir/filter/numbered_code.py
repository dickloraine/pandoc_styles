from pandoc_styles import run_pandoc_styles_filter, CodeBlock


def numbered(self):
    self.classes.append("numberLines")


if __name__ == "__main__":
    run_pandoc_styles_filter(numbered, CodeBlock)
