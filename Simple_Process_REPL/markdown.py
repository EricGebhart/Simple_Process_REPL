"""
This is the markdown module for SPR, it can convert markdown to html.
"""
import Simple_Process_REPL.appstate as A
import Simple_Process_REPL.utils as u
import markdown as m
import logging

logger = logging.getLogger()

# Name where we keep our stuff.
Root = "markdown"

yaml = u.dump_pkg_yaml("Simple_Process_REPL", "markdown.yaml")

# format and fill in as you wish.
HelpText = (
    """
markdown: - Converting Markdown to HTML  -


Works with 'With'. so put your markdown in _markdown_.
call md/html,
pop the result where you want it. Probabaly 'html'.


The rest can be ignored I think....

Markdown uses these parts of the Application state.

%s

Populate markdown/md in the Application state,
with the markdown you wish to convert.
Then use 'md/html-to some/value/vector' to convert and
save it.

Alternatively use md/html-from, give it the vector for
your markdown content, and the html will placed right
next to it in the data structure.
"""
    % yaml
)


def help():
    """Additional SPR help For the markdown Module."""
    print(HelpText)


def html(markdown):
    """
    convert markdown to html
    """
    return m.markdown(markdown)


def html_from(*keys):
    """Convert markdown from a value vector

    Convert the markdown and assign it to
    html in the same tree node as the markdown.

    example: md/html-from readme md

    This will convert readme/md from markdown into
    html and place the contents in readme/html
    """
    vv = keys[0][:-1]
    md = A.get_in(*keys)
    html = m.markdown(md)
    A.set_in(vv + ["html", html])


def html_to(*keys):
    """Convert the markdown held in markdown/md to HTML
    and assign it to the value vector given.
    example: md/send-to readme html"""
    md = A.get_in(["markdown", "md"])
    html = m.markdown(md)
    A.set_in(keys[0] + [html])
