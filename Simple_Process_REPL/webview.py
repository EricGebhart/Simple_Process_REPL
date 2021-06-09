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

The easiest way to use them is by using a with as it is not currently
possible to give a None, or use keyword arguments otherwise.

 with /foo

 '
 url : http://ericgebhart.com
 title: My viewer title.
 open_tab: True

 web/view

 web/browse

 pop-with

 with /foo web/view

 with /foo web/browse


The viewer is very basic.
The browser only understands urls, and if you want a new tab or window.

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


def view(html=None, url=None, title=""):
    """
    The html wins over url if both are given.

    Uses PyWebViewer

    example: with /readme web/view

    """
    webview.create_window(
        title,
        html=html,
        url=url,
        confirm_close=True,
    )
    webview.start()


def browse(url, open_tab=None):
    """Browse the url, Will try to use your default browser.

    If open tab is not set, use the setting
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
