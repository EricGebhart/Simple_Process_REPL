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

Markdown uses these parts of the Application state.

%s

with /foo

'
markdown: A bunch of markdown.


md/html

pop result html
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
