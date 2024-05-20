import panflute as pf
from panflute import (  # pylint: disable=unused-import
    Div,
    Element,
    ListContainer,
    Plain,
    RawBlock,
    RawInline,
    convert_text,
    run_filter,
)

from .constants import (
    EPUB,
    FIL_ALL,
    FIL_CHECK,
    FIL_OTHER,
    HTML,
    LATEX,
    LATEX_FORMATS,
    MD_PANDOC_STYLES_MD,
)
from .utils import make_list, yaml_dump, yaml_load


class PandocStylesFilter:
    """
    Base class for filters. Defines methods to help writing filters and to
    run them.
    """

    def __init__(self, func, filter_types=None, tags=None):
        self._add_method(func, "func")
        self.filter_types = make_list(filter_types or [])
        self.tags = make_list(tags or [])
        self._text = None

    def run(self):
        run_filter(self._pandoc_filter)

    def _pandoc_filter(self, elem, doc):
        self._init_filter(elem, doc)
        if not self.check():
            return
        self.new_text = self.func()  # pylint: disable=assignment-from-none
        return self._return_filter()

    @property
    def text(self):
        if self._text:
            return self._text
        return self.get_text()

    @text.setter
    def text(self, value):
        self._text = value

    def _init_filter(self, elem, doc):
        self.elem = elem
        self.doc = doc
        self.cfg = dict()
        self._get_format()
        self.classes = elem.classes if hasattr(elem, "classes") else None
        self.attributes = elem.attributes if hasattr(elem, "attributes") else None
        self.identifier = elem.identifier if hasattr(elem, "identifier") else None
        self._text = elem.text if hasattr(elem, "text") else None
        self.content = elem.content if hasattr(elem, "content") else None

    def _return_filter(self):
        if self.new_text is None:
            return
        elif self.new_text == []:
            return []
        elif isinstance(self.new_text, list):
            new = []
            for x in self.new_text:  # pylint: disable=not-an-iterable
                if isinstance(x, str):
                    x = convert_text(x)
                if isinstance(x, ListContainer):
                    new.extend(x)
                elif isinstance(x, list):
                    new.extend(x)
                else:
                    new.append(x)
            return new
        return convert_text(self.new_text)

    def _get_format(self):
        self.fmt = self.doc.format
        self.real_fmt = self.fmt
        if self.fmt in LATEX_FORMATS:
            self.fmt = LATEX
        elif self.fmt == EPUB:
            self.fmt = HTML

    def check(self):
        return (
            not self.filter_types
            or any(isinstance(self.elem, x) for x in self.filter_types)
        ) and (not self.tags or any(x in self.tags for x in self.classes))

    def func(self):
        return

    def _add_method(self, var, name):
        if var is not None:
            if callable(var):
                setattr(self, name, var.__get__(self))
            else:
                raise TypeError("Only functions are allowed in filter generation!")

    def get_metadata(self, key, default=None):
        """Gets metadata"""
        return self.doc.get_metadata(key, default)

    def get_pandoc_styles_metadata(self):
        """Return the pandoc_styles cfg as a dictionary"""
        try:
            self.cfg = yaml_load(self.get_metadata(MD_PANDOC_STYLES_MD))
        except FileNotFoundError:
            self.cfg = {}
        return self.cfg

    def save_pandoc_styles_metadata(self):
        """Save the given cfg in the cfg-file"""
        yaml_dump(self.cfg, self.get_metadata(MD_PANDOC_STYLES_MD))

    def stringify(self, elem=None):
        """Stringify an element"""
        return stringify(elem or self.elem)

    def transform(self, elem_type):
        """Transforms content of this element to elem_type. Return the new Element"""
        if isinstance(self.content, ListContainer):
            return elem_type(*self.content)
        return elem_type(self.content)

    def raw_block(self, text):
        """Return a RawBlock pandoc element in self.fmt. Accepts strings, tuples
        and lists as arguments.
        """
        return raw(self.fmt, text)

    def raw_inline(self, text):
        """Return a RawInline pandoc element in self.fmt. Accepts strings, tuples
        and lists as arguments.
        """
        return raw(self.fmt, text, element_type=RawInline)

    def convert_text(
        self, text=None, input_fmt="markdown", output_fmt="panflute", extra_args=None
    ):
        """Wrapper for panflutes convert_text"""
        text = text or self.text
        return convert_text(text, input_fmt, output_fmt, False, extra_args)

    def get_text(self, elem=None, output_fmt="markdown", extra_args=None):
        """
        Converts the content of the given Element to the output format. Use instead
        of stringify to retain inline formatting.
        """
        elem = self if elem is None else elem
        if isinstance(elem, ListContainer):
            elem = Plain(*elem)
        else:
            elem = getattr(elem, "content")
        return convert_text(elem, "panflute", output_fmt, False, extra_args)


def run_pandoc_styles_filter(func, filter_types=None, tags=None):
    """
    Run a filter with the given func. The function is now a method to a filter object
    and you can access its contents through self.

    Your filter can return:
    > None:   do nothing
    > string: convert the string from markdown to panflute elements
    > list:   The list can contain Panflute Elements or strings. Strings are converted
              like above.
    """
    PandocStylesFilter(func, filter_types, tags).run()


class TransformFilter(PandocStylesFilter):
    """
    Base class for filters. Defines methods to help writing filters and to
    run them.
    """

    # pylint: disable=super-init-not-called
    def __init__(
        self,
        tags=None,
        all_formats=None,
        other=None,
        filter_types=None,
        check=None,
        **kwargs,
    ):
        self.tags = make_list(tags or [])
        self.filter_types = filter_types if filter_types is not None else [Div]
        self.filter_types = make_list(self.filter_types)
        self._add_method(all_formats, FIL_ALL)
        self._add_method(other, FIL_OTHER)
        self._add_method(check, FIL_CHECK)
        self.funcs = kwargs

    def _pandoc_filter(self, elem, doc):
        self._init_filter(elem, doc)
        if not self.check():
            return
        for key, func in self.funcs.items():
            self._add_method(func, key)

        self.all_formats()
        self._call_filter()
        return self._return_filter()

    def _call_filter(self):
        try:
            self.new_text = getattr(self, self.fmt)()
        except AttributeError:
            # pylint: disable=assignment-from-none
            self.new_text = self.other()

    def _return_filter(self):
        if self.new_text is None:
            return
        elif self.new_text == []:
            return []
        elif isinstance(self.new_text, list):
            new = []
            for x in self.new_text:
                if isinstance(x, str):
                    x = raw(self.fmt, x)
                if isinstance(x, ListContainer):
                    new.extend(x)
                elif isinstance(x, list):
                    new.extend(x)
                else:
                    new.append(x)
            return new
        return self.raw_block(self.new_text)

    def all_formats(self):
        return

    def other(self):
        return

    def _add_method(self, var, name):
        if var is not None:
            if isinstance(var, str):
                setattr(self, name, lambda: var.format(text=self.convert_to_fmt()))
            elif isinstance(var, list):
                setattr(
                    self,
                    name,
                    lambda: [self.content if x == "text" else x for x in var],
                )
            elif callable(var):
                setattr(self, name, var.__get__(self))
            else:
                raise TypeError(
                    "Only strings and functions are allowed in filter generation!"
                )

    def convert_to_fmt(self, text=None, input_fmt="markdown", extra_args=None):
        """Converts text in input_fmt to self.fmt"""
        text = text or self.text
        return convert_text(text, input_fmt, self.fmt, False, extra_args)

    def get_text(self, elem=None, output_fmt=None, extra_args=None):
        """
        Converts the content of the given Element to the format. Use instead
        of stringify to retain inline formatting.
        """
        elem = self if elem is None else elem
        if isinstance(elem, ListContainer):
            elem = Plain(*elem)
        else:
            elem = getattr(elem, "content")
        return convert_text(elem, "panflute", output_fmt or self.fmt, False, extra_args)


def run_transform_filter(
    tags=None, all_formats=None, other=None, filter_types=None, check=None, **kwargs
):
    """
    Creates and runs a pandoc filter.

    tags: The default check method checks, if these tags are in the classes of
    the element the filter searches for. If it is [], check only checks for
    the element type

    kwargs: The name of the format and a value of: a function, string or a list.
    Frequently used formats: latex (for latex and pdf), html (for html and epubs),
                             markdown.

    > Function: These functions are registered as a method and are executed,
    if the format of the output matches the name. These methods have to
    either return a string/list of strings or an pandoc element/list of elements.

    > String: The string is returned as the output. The string can contain
    the formating {text], which gets replaced by the converted text
    of the element.

    > List: The list is returned as below. You can insert the string "text" inside the
            list. It is replaced with the content of the element.

    all_formats: This method is executed before the format specific methods
    and is used to execute shared code.

    filter_types: If the filter searches for an element other than a div. Can be
    a list of types

    check: Replace the default check method with your own.

    Your filter can return:
    > None:   do nothing
    > string: convert the string to a rawblock in the current format or
              from markdown to panflute elements if the format doesn't support rawblocks
    > list:   The list can contain Panflute Elements or strings. Strings are converted
              like above.
    """
    pandoc_filter = TransformFilter(
        tags, all_formats, other, filter_types, check, **kwargs
    )
    pandoc_filter.run()


def is_pandoc_element(ele):
    if isinstance(ele, Element):
        return True
    elif isinstance(ele, (list, tuple)):
        return is_pandoc_element(ele[0])
    return False


def raw(fmt, text, element_type=RawBlock):
    """Return a Raw pandoc element in the given format."""
    if fmt not in ["tex", "latex", "html", "context"]:
        return convert_text(text)
    return element_type(text, fmt)


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
