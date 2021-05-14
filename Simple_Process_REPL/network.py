import Simple_Process_REPL.dialog as D
import logging
import regex as re

import Simple_Process_REPL.appstate as A
import Simple_Process_REPL.utils as u
import Simple_Process_REPL.subcmd as S

logger = logging.getLogger()

yaml = u.dump_pkg_yaml("Simple_Process_REPL", "network.yaml")

# format and fill in as you wish.
HelpText = (
    """
network: - Network type stuff Currently only wifi for linux.  -

Uses dialogs and nmcli, network-manager, to establish a wifi connection.

network uses these parts of the Application state.

%s

connect-wifi always checks to see if there is a connection. If there is,
it simply remembers it.

The first time, on a fresh system, if network manager has never connected,
connect-wifi will search for networks and present a menu of choices.
This usually only happens once and only if the computer has never connected
to the wifi in that location.

At some point there may be some ssh type commands here. Currently none of them
do anything.

"""
    % yaml
)


def help():
    """Additional SPR specific Help for the Network Module."""
    logger.info("network help")
    print(HelpText)


def check_connection():
    "Check the wifi connection with Network manager"
    if A.islinux():
        logger.debug("check connection!")
        res = S.do_cmd(["nmcli", "device"])
        logger.debug(res)
        if len(re.findall("connected", res)):
            A.set_in(["network", "wifi-connected", True])
        else:
            A.set_in(["network", "wifi-connected", False])
            return False
        return True
    return False


def get_SSIDS():
    # get first column.
    cmd = ["nmcli", "connection", "show"]
    res = S.do_cmd(cmd)
    ssids = []
    for line in res.split("\n"):
        ssids.append(line.split(" ")[0])

    return ssids


def connect_SSID(ssid):
    """Connect the wifi to the SSID given."""
    cmd = ["nmcli", "device", "wifi", "connect", ssid]
    res = S.do_cmd(cmd)
    logger.info(res)


def connect_wifi():
    """
    Connect the wifi, get the SSID's, give a selection dialog to choose,
    then connect to the chosen SSID. Only implemented for linux for use
    with network manager.
    """
    if A.islinux():
        if not check_connection():
            ssids = get_SSIDS()
            menuitems = []
            for ssid in ssids:
                menuitems.append([ssid, ssid])
            ssid = D.select_choice("Choose an SSID to Connect.", menuitems)
            if ssid is not None:
                logger.info("Connecting to %s" % ssid)
                connect_SSID(ssid)


def confirm_tunnel():
    "Confirm the ssh tunnel is established"
    pass


def create_tunnel(pem_file, server):
    "Create an ssh tunnel."
    pass


def connect_tunnel():
    "Connect to an ssh tunnel"
    pass


def sendlog():
    "Send the log somewhere."
    pass
