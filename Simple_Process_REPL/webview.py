import Simple_Process_REPL.appstate as A
import Simple_Process_REPL.utils as u
import os
import logging

import webview
import time

logger = logging.getLogger()

# Name where we keep our stuff.
Root = "webview"

yaml = u.dump_pkg_yaml("Simple_Process_REPL", "webview.yaml")

# format and fill in as you wish.
HelpText = (
    """
Web view: - View HTML from a url or a chunk.  -

webview uses these parts of the Application state.
If you wish to use view_html_with, this is more or
less what you need to create for webview to use it.

Web view will show the HTML, instead of the url if both are given.

SPR:> set foo http://ericgebhart.com
SPR:> web/view-url-from "window title" foo

The easy way to get a structure to use view-with,
is to copy the default and change the values.
'set-from your place from: config webview'

%s

So far, this is really basic usage of pywebview.

   https://pywebview.flowrl.com

Feel free to extend this module and do a pull request.

"""
    % yaml
)


def help():
    print(HelpText)


# Get something out of my part of the config.
# A.get_in_config([Root, "foo"])

# Put something into my part of the Appstate.
# A.set_in([Root, "foo" "bar" 10])

# Get something out of my part of the Appstate.
# A.get_in([Root, "foo" "bar"])


def view_html_from(title, *keys):
    """View a chunk of HTML from somewhere.
    example: view-html-from "window title" readme html
    """
    html = A.get_in(*keys)
    webview.create_window(
        title,
        html=html,
        confirm_close=True,
    )
    webview.start()


def view_url_from(title, *keys):
    """View a url from somewhere.
    example: view-url-from "window title" readme url
    """
    url = A.get_in(*keys)
    logger.info("view url: %s" % url)
    webview.create_window(
        title,
        url=url,
        confirm_close=True,
    )
    webview.start()


def view_html_with(*keys):
    """Given a value vector, use the values located there for title, html, and url
    html wins over url if both are given.
    example: view-html-with readme

    With luck, the value vector given will contain title,
    a url and/or a chunk of html.
    """

    # I think this can be a lot easier, with kwargs. - refactor
    html, url, title = A.get_vals_in(*keys, "html", "url", "title")
    webview.create_window(
        title,
        html=html,
        url=url,
        confirm_close=True,
    )
    webview.start()
