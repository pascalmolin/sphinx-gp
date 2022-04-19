from docutils.nodes import literal_block
from docutils.parsers.rst import Directive, directives
from sphinx.util.nodes import set_source_info
from sphinx.errors import ExtensionError
from sphinx.util.osutil import ensuredir, copyfile
import os, shutil
from tempfile import mkdtemp

from sphinx.util import logging
logger = logging.getLogger(__name__)
logger.info('loading extension %s'%__name__)

__version__ = '0.1.0'

class codeeval(literal_block): pass
class gpeval(literal_block): pass
class xcaseval(literal_block): pass

def visit_gpeval_html(self, node):
    self.body.append(
        """
        <div id="codeshell">
        <button class="eval" onclick="return gpeval(this)" data-tip="run ⇧⏎"></button>
        <pre class="highlight-gp code" id="input"
             contenteditable="true" ondblclick="return gpeval(this)"
             onkeydown="shiftenter(this)">"""
        )

def visit_xcaseval_html(self, node):
    self.body.append(
        """
        <div id="codeshell">
        <div class="eval" onclick="return xcaseval(this)">&eacute;valuer</div>
        <pre class="highlight-xcas code" id="input"
             contenteditable="true" ondblclick="return xcaseval(this)">"""
        )
def depart_html(self, node):
        #<button type="button" onclick="return eval(this)">run</button>
    self.body.append(
        """</pre>
        <button class="insert" onclick="return newcell(this)" data-tip="new cell"></button>
        </div>
        """
        )
def visit_latex(self, node):
  if node['notex']:
      self.body.append('\\iffalse\n')
  self.body.append('\n\\begin{program}\\begin{alltt}\\small\n')
def depart_latex(self, node):
  self.body.append('\n\\end{alltt}\\caption{%s}\\end{program}\n'%node['title'])
  if node['notex']:
      self.body.append('\\fi\n')

class Codeeval(Directive):

    language = None
    nodeclass = None
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
            'class': directives.class_option,
            'name': directives.unchanged,
            'title': directives.unchanged,
            'notex': directives.flag,
            }

    def run(self):
        code = u'\n'.join(self.content)
        code = code.replace('\\lt ','<')
        code = code.replace('\\gt ','>')

        literal = self.nodeclass(code, code)
        literal['language'] = self.language
        literal['classes'] += self.options.get('class', [])
        literal['title'] = self.options.get('title','code gp')
        literal['notex'] = self.options.get('notex',False)

        set_source_info(self, literal)

        self.add_name(literal)

        return [literal]

class GPeval(Codeeval):
    language = 'gp'
    nodeclass = gpeval

class Xcaseval(Codeeval):
    language = 'xcas'
    nodeclass = xcaseval

### copied from sphinxcontrib.katex
### allows to put stylesheet and gp.js here

def setup_static_path(app):
    app._gpcode_static_path = mkdtemp()
    if app._gpcode_static_path not in app.config.html_static_path:
        app.config.html_static_path.append(app._gpcode_static_path)
    logger.info(f'html_static_path = {app.config.html_static_path}')

def copy_contrib_file(app, file_name):
    pwd = os.path.abspath(os.path.dirname(__file__))
    source = os.path.join(pwd, file_name)
    dest = os.path.join(app._gpcode_static_path, file_name)
    if os.path.exists(source+'_t'):
        source += '_t'
        dest += '_t'
    ensuredir(os.path.dirname(dest))
    copyfile(source, dest)

filename_css = 'evalcode.css'
filename_js = 'gp.js'
def builder_inited(app):
    # Ensure the static path is setup to hold KaTeX CSS and autorender files
    setup_static_path(app)
    # custom js and CSS
    copy_contrib_file(app, filename_css)
    copy_contrib_file(app, filename_js)

    if not (app.config.gp_js_path):
        raise ExtensionError('GP paths not set')
    # add this path to html_context, so that it is available in template
    if app.config.gp_js_path != 'default':
        #add_js(app.config.gp_js_path)
        logger.warning('using gp files %s'%app.config.gp_js_path)
        logger.warning('make sure files are correctly deployed')
    else:
        logger.warning('using local gp files, may be outdated')
        gp_js_path = '_static'
        app.config.gp_js_path = gp_js_path
        pwd = os.path.abspath(os.path.dirname(__file__))
        gp_static_path = os.path.join(pwd, gp_js_path)
        outpath = os.path.join(app.outdir, '_static')
        ensuredir(outpath)
        for f in ['gp-sta.js','gp-sta.wasm']:
            logger.info(f'copy  {gp_static_path}/{f} to {outpath}/{f}')
            copyfile(f'{gp_static_path}/{f}', f'{outpath}/{f}')
    app.config.html_context['gp_js_path'] = app.config.gp_js_path

def has_gp_node(doctree):
    if doctree is None:
        return False
    return any( True for _ in doctree.traverse(gpeval) )

def html_page_context(app, pagename, templatename, context, doctree):
    """ add gp if necessary for this page """
    if has_gp_node(doctree):
        app.add_js_file(filename_js, loading_method='async')
        app.add_css_file(filename_css)

def builder_finished(app, exception):
    # Delete temporary dir used for _static file
    shutil.rmtree(app._gpcode_static_path)

def setup(app):
    app.add_node(gpeval, html=(visit_gpeval_html, depart_html),
                        latex=(visit_latex, depart_latex))
    app.add_node(xcaseval, html=(visit_xcaseval_html, depart_html))

    app.add_config_value('gp_version', '2.14', False)
    # if set, do not load the local gp files provided here
    app.add_config_value('gp_js_path', 'default', False)
    app.add_directive('gp', GPeval)
    app.add_directive('xcas', Xcaseval)

    ## no longer used
    #app.config.html_context['gp'] = True
    #app.config.html_context['xcas'] = True
   
    # add stylesheets after env inited
    app.connect('builder-inited', builder_inited)
    app.connect('html-page-context', html_page_context)
    app.connect('build-finished', builder_finished)

    return {'version': __version__, 'parallel_read_safe': True}
