import pytest
from pandoc_styles.utils import file_read, file_write
from fixtures import run_script, copy_from_config  # pylint: disable=W0611
# pylint: disable=W0621, W0613, W1401


@pytest.fixture
def test_filter(tmpdir, run_script, copy_from_config):
    def _test_filter(filt, args, fmts, base=TF_BASE):
        copy_from_config(f"filter/{filt}")
        test_base = base.format(filt, f"{{{args}}}")
        test_file = file_write("test.md", test_base, tmpdir)

        for fmt, fmt_txt, fmt_open, fmt_close in fmts:
            target = fmt_txt.format(fmt_open, fmt_close)
            ps = run_script(f'{test_file} -t {fmt}')
            assert ps
            assert ps.stdout == f"INFO: Build {fmt}\n"
            assert file_read(f"test.{fmt}", tmpdir) == target
    return _test_filter


def test_alignment(test_filter):
    test_filter('alignment.py', '.align .center',
                [('html', TF_HTML_BASE, '<div class="align_center">', '</div>'),
                 ('latex', TF_LATEX_BASE, '\\begin{center}\n', '\n\\end{center}')])


def test_custom_styles(test_filter):
    test_filter('custom_styles.py', '.custom .teststyle',
                [('html', TF_HTML_BASE, '<div class="teststyle">', '</div>'),
                 ('latex', TF_LATEX_BASE, '\\begin{teststyle}\n', '\n\\end{teststyle}')])
    test_filter('custom_styles.py', '.custom pdf=pdf_teststyle html=html_teststyle',
                [('html', TF_HTML_BASE, '<div class="html_teststyle">', '</div>'),
                 ('latex', TF_LATEX_BASE, '\\begin{pdf_teststyle}\n',
                  '\n\\end{pdf_teststyle}')])


def test_epigraph(test_filter):
    test_filter('epigraph.py', '.epigraph',
                [('html', TF_HTML_BASE, '<div class="Epigraph">', '</div>'),
                 ('latex', TF_LATEX_BASE, '\\dictum[]{',
                  '}\n\\par\n\\vspace{\\baselineskip}\n\\par\n\\noindent')])
    test_filter('epigraph.py', '.epigraph author="Sherlock Holmes"',
                [('html', TF_HTML_BASE,
                  '<div class="Epigraph">',
                  '<p class="EpigraphAuthor">Sherlock Holmes</p>\n</div>'),
                 ('latex', TF_LATEX_BASE,
                  '\\dictum[Sherlock Holmes]{',
                  '}\n\\par\n\\vspace{\\baselineskip}\n\\par\n\\noindent')])


def test_include(tmpdir, test_filter):
    incl_file = file_write("test_incl.md", "Text to Include", tmpdir)
    base = BASE.format("{}", f'~~~{{}}\n{incl_file}\n~~~')
    test_filter('include.py', '.include',
                [('html', HTML_BASE, '<p>Text to Include</p>', ''),
                 ('latex', LATEX_BASE, 'Text to Include', '')],
                base)


def test_new_page(test_filter):
    base = BASE.format("{}", '~~~{}\n\n~~~')
    test_filter('new_page.py', '.new_page',
                [('html', HTML_BASE, '<div class="pagebreak"></div>', ''),
                 ('latex', LATEX_BASE, r"\clearpage", '')],
                base)
    test_filter('new_page.py', '.new_page .odd-page',
                [('latex', LATEX_BASE, r"\cleardoublepage", '')],
                base)


def test_noindent(test_filter):
    test_filter('noindent.py', '.noindent',
                [('html', TF_HTML_BASE, '<div class="noindent">', '</div>'),
                 ('latex', TF_LATEX_BASE, '\\noindent\n', '')])


def test_quote(test_filter):
    test_filter('quote.py', '.quote author="Sher Holm" title=Test',
                [('html', TF_HTML_BASE,
                  '<div class="QuoteBlock">',
                  '<p class="QuoteScource">Test</p>\n'
                  '<p class="QuoteAuthor">Sher Holm</p>\n</div>'),
                 ('latex', TF_LATEX_BASE,
                  "\\begin{quote}\n",
                  "\n\n\\hspace*{\\fill}\\textbf{Test}\\linebreak"
                  "\\hspace*{\\fill}\\textit{Sher Holm}\n\\end{quote}")])
    test_filter('quote.py', '.quote .one-line author="Sher Holm" title=Test',
                [('html', TF_HTML_BASE,
                  '<div class="QuoteBlock">',
                  '<p class="QuoteSingle"><em>Sher Holm</em> &mdash; '
                  "<strong>Test</strong></p>\n</div>"),
                 ('latex', TF_LATEX_BASE,
                  "\\begin{quote}\n",
                  "\n\\hfill \\textit{Sher Holm} --- \\textbf{Test}\n\\end{quote}")])
    test_filter('quote.py', '.quote .top author="Sher Holm" title=Test',
                [('html', TF_HTML_BASE,
                  '<div class="QuoteBlock">\n'
                  '<p class="QuoteScourceTop">Test</p>\n'
                  '<p class="QuoteAuthorTop">Sher Holm</p>',
                  "</div>"),
                 ('latex', TF_LATEX_BASE,
                  "\\begin{quote}\n\\begin{center}\n\\large\\textbf{Test}\n"
                  "\n\\normalsize\\textit{Sher Holm}\n\\end{center}\n",
                  "\n\\end{quote}")])


BASE = """\
---
style-definition:
  all:
    command-line:
      filter: {}
  latex:
    command-line:
      wrap: none
---

The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.

{}

The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.
"""


TF_BASE = BASE.format("{}", """\
~~~{}
The campaign brought honours and promotion to many, but
for me it had nothing but misfortune and disaster. I was removed from my
brigade and attached to the Berkshires, with whom I served at the fatal battle
of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which
shattered the bone and grazed the subclavian artery. I should have
fallen into the hands of the murderous Ghazis had it not been for the
devotion and courage shown by Murray, my orderly, who threw me across a
pack-horse, and succeeded in bringing me safely to the British lines.
~~~
""")

HTML_BASE = """\
<p>The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.</p>
<p>There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.</p>
{}{}
<p>The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.</p>
<p>There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.</p>
"""

TF_HTML_BASE = HTML_BASE.format("", """\
{}
<p>The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.</p>
<p>There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.</p>
{}""")

LATEX_BASE = """\
The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.

{}{}

The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.
"""

TF_LATEX_BASE = LATEX_BASE.format("", """\
{}The campaign brought honours and promotion to many, but for me it had
nothing but misfortune and disaster. I was removed from my brigade and
attached to the Berkshires, with whom I served at the fatal battle of
Maiwand.

There I was struck on the shoulder by a Jezail bullet, which shattered
the bone and grazed the subclavian artery. I should have fallen into the
hands of the murderous Ghazis had it not been for the devotion and
courage shown by Murray, my orderly, who threw me across a pack-horse,
and succeeded in bringing me safely to the British lines.{}""")
