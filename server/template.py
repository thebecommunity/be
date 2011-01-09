import os
import threading

from genshi.core import Stream
from genshi.output import encode, get_serializer
from genshi.template import Context, TemplateLoader

loader = TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'templates'),
    auto_reload=True
)
templates = threading.local()

def output(filename, method='html', encoding='utf-8', **options):
    """Decorator for exposed methods to specify what template they should use
    for rendering, and which serialization method and options should be
    applied.
    """
    def decorate(func):
        def wrapper(*args, **kwargs):
            templates.templ = loader.load(filename)
            opt = options.copy()
            if method == 'html':
                opt.setdefault('doctype', 'html')
            serializer = get_serializer(method, **opt)
            stream = func(*args, **kwargs)
            if not isinstance(stream, Stream):
                return stream
            return encode(serializer(stream), method=serializer,
                          encoding=encoding)
        return wrapper
    return decorate

def render(*args, **kwargs):
    """Function to render the given data to the template specified via the
    ``@output`` decorator.
    """
    if args:
        assert len(args) == 1, \
            'Expected exactly one argument, but got %r' % (args,)
        template = loader.load(args[0])
    else:
        template = templates.templ
    ctxt = Context()
    ctxt.push(kwargs)
    return template.generate(ctxt).render('html')
