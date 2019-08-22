import panflute as pf
from panflute import (  # pylint: disable=unused-import
    Null, HorizontalRule, Space, SoftBreak, LineBreak, Str,
    Code, BlockQuote, Note, Div, Plain, Para, Emph, Strong, Strikeout,
    Superscript, Subscript, SmallCaps, Span, RawBlock, RawInline, Math,
    CodeBlock, Link, Image, BulletList, OrderedList, DefinitionList,
    LineBlock, Header, Quoted, Cite, Table, ListContainer,
    convert_text, Element, run_filter)
from .constants import (HTML, PDF, LATEX, EPUB, MD_PANDOC_STYLES_MD,
                        FIL_OTHER, FIL_ALL, FIL_CHECK)
from .utils import make_list, yaml_load, yaml_dump


class PandocStylesFilter():
    '''
    Base class for filters. Defines methods to help writing filters and to
    run them.
    '''
    def __init__(self, func, filter_types=None, tags=None):
        self._add_method(func, "func")
        self.filter_types = make_list(filter_types or [])
        self.tags = make_list(tags or [])

    def run(self):
        run_filter(self._pandoc_filter)

    def _pandoc_filter(self, elem, doc):
        self._init_filter(elem, doc)
        if not self.check():
            return
        self.new_text = self.func()  # pylint: disable=assignment-from-none
        return self._return_filter()

    def _init_filter(self, elem, doc):
        self.elem = elem
        self.doc = doc
        self.cfg = dict()
        self._get_format()
        self.classes = elem.classes if hasattr(elem, "classes") else None
        self.attributes = elem.attributes if hasattr(elem, "attributes") else None
        self.text = elem.text if hasattr(elem, "text") else None
        self.content = elem.content if hasattr(elem, "content") else None

    def _return_filter(self):
        if self.new_text is None:
            return
        elif self.new_text == [] or is_pandoc_element(self.new_text):
            return self.new_text
        return convert_text(self.new_text)

    def _get_format(self):
        self.fmt = self.doc.format
        self.real_fmt = self.fmt
        if self.fmt == PDF:
            self.fmt = LATEX
        elif self.fmt == EPUB:
            self.fmt = HTML

    def check(self):
        return (not self.filter_types
                or any(isinstance(self.elem, x) for x in self.filter_types))\
                and (not self.tags or any(x in self.tags for x in self.classes))

    def func(self):
        return

    def _add_method(self, var, name):
        if var is not None:
            if callable(var):
                setattr(self, name, var.__get__(self))
            else:
                raise TypeError("Only strings and functions are allowed in filter generation!")

    def get_metadata(self, key, default=None):
        '''Gets metadata'''
        return self.doc.get_metadata(key, default)

    def get_pandoc_styles_metadata(self):
        '''Return the pandoc_styles cfg as a dictionary'''
        try:
            self.cfg = yaml_load(self.get_metadata(MD_PANDOC_STYLES_MD))
        except FileNotFoundError:
            self.cfg = {}
        return self.cfg

    def save_pandoc_styles_metadata(self):
        '''Save the given cfg in the cfg-file'''
        yaml_dump(self.cfg, self.get_metadata(MD_PANDOC_STYLES_MD))

    def stringify(self, elem=None):
        '''Stringify an element'''
        return stringify(elem or self.elem)

    def raw_block(self, *args):
        '''Return a RawBlock pandoc element in self.fmt. Accepts strings, tuples
        and lists as arguments.
        '''
        return raw(self.fmt, *args)

    def raw_inline(self, *args):
        '''Return a RawInline pandoc element in self.fmt. Accepts strings, tuples
        and lists as arguments.
        '''
        return raw(self.fmt, *args, element_type=RawInline)


def run_pandoc_styles_filter(func, filter_types=None, tags=None):
    """
    Run a filter with the given func. The function is now a method to a filter object
    and you can access its contents through self.
    """
    PandocStylesFilter(func, filter_types, tags).run()

class TransformFilter(PandocStylesFilter):
    '''
    Base class for filters. Defines methods to help writing filters and to
    run them.
    '''

    # pylint: disable=super-init-not-called
    def __init__(self, tags=None, latex=None, html=None, other=None,
                 all_formats=None, filter_types=None, check=None):
        self.tags = make_list(tags or [])
        self.filter_types = filter_types if filter_types is not None else [CodeBlock]
        self.filter_types = make_list(self.filter_types)
        self._add_method(latex, LATEX)
        self._add_method(html, HTML)
        self._add_method(other, FIL_OTHER)
        self._add_method(all_formats, FIL_ALL)
        self._add_method(check, FIL_CHECK)

    def _pandoc_filter(self, elem, doc):
        self._init_filter(elem, doc)
        if not self.check():
            return

        self.all_formats()
        self._call_filter()
        return self._return_filter()

    # pylint: disable=assignment-from-none
    def _call_filter(self):
        if self.fmt == LATEX:
            self.new_text = self.latex()
        elif self.fmt == HTML:
            self.new_text = self.html()
        else:
            self.new_text = self.other()

    def _return_filter(self):
        if self.new_text is None:
            return
        elif self.new_text == [] or is_pandoc_element(self.new_text):
            return self.new_text
        return self.raw_block(self.new_text)

    def all_formats(self):
        return

    def latex(self):
        return None

    def html(self):
        return None

    def other(self):
        return None

    def _add_method(self, var, name):
        if var is not None:
            if isinstance(var, str):
                setattr(self, name, lambda: var.format(text=self.convert_text()))
            elif callable(var):
                setattr(self, name, var.__get__(self))
            else:
                raise TypeError("Only strings and functions are allowed in filter generation!")

    def convert_text(self, text=None, input_fmt='markdown', extra_args=None):
        '''Converts text in input_fmt to self.fmt'''
        text = text or self.text
        return convert_text(text, input_fmt, self.fmt, False, extra_args)


def run_transform_filter(tags=None, latex=None, html=None, other=None,
                         all_formats=None, filter_type=None, check=None):
    '''
    Creates and runs a pandoc filter.

    tags: The default check method checks, if these tags are in the classes of
    the element the filter searches for. If it is [], check only checks for
    the element type

    latex, html, other: Accepts either a function or a string.

    > Function: These functions are registered as a method and are executed,
    if the format of the output matches the name. These methods have to
    either return a string/list of strings or an pandoc element/list of elements.

    > String: The string is returned as the output. The string can contain
    the formating {text], which gets replaced by the converted text
    of the element.

    all_formats: This method is executed before the format specific methods
    and is used to execute shared code.

    filter_type: If the filter searches for an element other than a CodeBlock. Can be
    a list of types

    check: Replace the default check method with your own.
    '''
    pandoc_filter = TransformFilter(tags, latex, html, other, all_formats, filter_type,
                                    check)
    pandoc_filter.run()


def is_pandoc_element(ele):
    if isinstance(ele, Element):
        return True
    elif isinstance(ele, (list, tuple)):
        return is_pandoc_element(ele[0])
    return False


def raw(fmt, *args, element_type=RawBlock):
    '''Return a Raw pandoc element in the given format. Accepts strings,
    lists and tuples as arguments.
    '''
    text = []
    for s in args:
        if isinstance(s, str):
            text.append(s)
        elif isinstance(s, list):
            text.extend(s)
        elif isinstance(s, tuple):
            text.extend(list(s))
        else:
            raise TypeError('Only strings and lists/tuples of strings are allowed in raw')

    if fmt not in ['tex', 'latex', 'html', 'context']:
        return convert_text(''.join(text))
    return element_type(''.join(text), fmt)


def stringify(elem, newlines=True):
    """
    Return the raw text version of an element (and its children elements).
    Example:
        >>> e1 = Emph(Str('Hello'), Space, Str('world!'))
        >>> e2 = Strong(Str('Bye!'))
        >>> para = Para(e1, Space, e2)
        >>> stringify(para)
        'Hello world! Bye!\n\n'
    :param newlines: add a new line after a paragraph (default True)
    """
    if isinstance(elem, ListContainer):
        elem = Plain(*elem)
    return pf.stringify(elem, newlines)


def strip_html_tag(text, tag="p"):
    text = text.replace(f"<{tag}>", "")
    return text.replace(f"</{tag}>", "")
