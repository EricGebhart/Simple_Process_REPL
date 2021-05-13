# Do stuff with SPR.
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

Markdown uses these parts of the Application state.

%s

Populate markdown/md in the Application state,
with the markdown you wish to convert.
then convert to what you want and set it where you like
with a *send_html_to* command.
"""
    % yaml
)


def help():
    print(HelpText)


def load_from(*keys):
    """Load markdown from a value vector into markdown/md,
    Convert the markdown and assign it to markdown/html.
    example: md/load-from readme md"""
    md = A.get_in(*keys)
    html = m.markdown(md)
    A.set_in(["markdown", "md", md])
    A.set_in(["markdown", "html", html])


def send_to(*keys):
    """Convert the markdown held in markdown/md to HTML
    and assign it to the value vector given.
    example: md/send-to readme html"""
    md = A.get_in(["markdown", "md"])
    html = m.markdown(md)
    A.set_in(keys[0] + [html])
