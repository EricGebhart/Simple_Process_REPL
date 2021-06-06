"""
This is basic functionality to view a chunk of html or a url

So far, this is really basic usage of webbrowser and pywebview.

   https://docs.python.org/3/library/webbrowser.html

   https://pywebview.flowrl.com
"""
import Simple_Process_REPL.appstate as A
import Simple_Process_REPL.utils as u
import os
import logging

import webbrowser
import webview
import time

logger = logging.getLogger()

# Name where we keep our stuff.
Root = "web"

yaml = u.dump_pkg_yaml("Simple_Process_REPL", "webview.yaml")

# format and fill in as you wish.

HelpText = (
    """
Web: - View HTML from a url or a chunk.  -

Web uses these parts of the Application state.

%s

Web View will show the HTML, instead of the url if both are given.

SPR:> set foo http://ericgebhart.com
SPR:> web/view-url-from "window title" my Place Where I put the settings I want to View

The browser only undertands urls, and if you want a new tab or window.

SPR:> web/browse-url-from my Place Where I put my url
SPR:> web/browse-with my Place Where I put the settings that I want to View

"""
    % yaml
)


def help():
    """Additional SPR specific Help for the Web Module."""
    print(HelpText)


# Get something out of my part of the config.
# A.get_in_config([Root, "foo"])

# Put something into my part of the Appstate.
# A.set_in([Root, "foo" "bar" 10])

# Get something out of my part of the Appstate.
# A.get_in([Root, "foo" "bar"])


def view_html_from(title, *keys):
    """View a chunk of HTML from somewhere, Using PyWebViewer.
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
    """View a url from somewhere, Using PyWebViewer.

    example: view-url-from "window title" readme url
    """
    open = A.get_in_config(["webview" "browser" "open"])
    url = A.get_in(*keys)
    logger.info("view url: %s" % url)
    webview.create_window(
        title,
        url=url,
        confirm_close=True,
    )
    webview.start()


def browse_url_from(path):
    """Browse a url from somewher. Using webbrowser.
    example: browse-url-from readme url
    """
    url = A.get_from_path(path)
    logger.info("browse url: %s" % url)
    webbrowser.open(url)


def view(html=None, url=None, title=""):
    """
    The html wins over url if both are given.

    Uses PyWebViewer

    example: with /readme
             web/view

    """
    webview.create_window(
        title,
        html=html,
        url=url,
        confirm_close=True,
    )
    webview.start()


def view_with(path):
    """Given a path, use the values located there for title, html, and url.
    The html wins over url if both are given.

    Uses PyWebViewer

    example: view-with readme

    With luck, the value vector given will contain title,
    a url and/or a chunk of html.
    """

    # I think this can be a lot easier, with kwargs. - refactor
    html, url, title = A.get_vals_in(path, ["html", "url", "title"])
    view(html, url, title)


def browse(url, open_tab=None):
    """Browse the url, if open tab is not set, use the setting
    in /config/browser/open-tab.
    If not true, a new browser window will open.
    """
    if open_tab is None:
        open_tab = A.get_in_config([Root, "browser", "open-tab"])

    if open_tab:
        webbrowser.open_new_tab(url)
    else:
        webbrowser.open_new(url)

    webview.start()


def browse_with(path):
    """Given a value vector, use the values located there for url and open.
    if open-tab is set to anything the url will be opened in a new tab if possible.
    A new window will be opened otherwise.

    Uses Webbrowser

    example: browse-with readme

    The value vector given should contain at least a url, if
    open-tab is present, that value will over ride the value set
    in the configuration.
    """

    tab = A.get_in_config([Root, "browser", "open-tab"])
    # I think this can be a lot easier, with kwargs. - refactor
    url, ltab = A.get_vals_in(path, ["url", "open-tab"])

    if ltab:
        browse(url, ltab)
    else:
        browse(url, tab)
