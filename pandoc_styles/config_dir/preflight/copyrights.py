from pandoc_styles import run_preflight_script, file_read, file_write


def preflight(self):
    copyrights = self.cfg.get("copyrights")
    copyrights_header = self.cfg.get("copyrights-header", "Copyrights")
    if copyrights:
        copyrights = f'# {copyrights_header}{{.hidden}}\n<div class="copyrights">'\
                     f'{copyrights}\n</div>\n'
        file_write(self.files[-1], f"{file_read(self.files[-1])}\n{copyrights}")


if __name__ == '__main__':
    run_preflight_script(preflight)
