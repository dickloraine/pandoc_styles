import re
from pandoc_styles import run_preflight_script, file_read, file_write


def preflight(self):
    dedication = self.cfg.get("dedication")
    dedication_header = self.cfg.get("dedication-header", "Dedication")
    if dedication:
        dedication = f'# {dedication_header}{{.hidden}}\n<div class="dedication">'\
                     f'{dedication}\n</div>\n'
        dedication = re.sub(r'(.?-{3}.*?(\n\.{3}\n|\n-{3}\n))',
                            rf"\1\n{dedication}", file_read(self.files[0]),
                            flags=re.DOTALL)
        file_write(self.files[0], dedication)


if __name__ == '__main__':
    run_preflight_script(preflight)
