"""
Swiftsuru related services to Tsuru
"""
import os
import random
import socket
import syslog
from aclapiclient import Client, L4Opts


from swiftsuru import conf


def generate_container_name():
    return os.urandom(3).encode('hex')


def generate_password(pw_length=8):
    """ Generate a password
        From: http://interactivepython.org/runestone/static/everyday/2013/01/3_password.html
    """
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*"
    mypw = ""

    for i in range(pw_length):
        next_index = random.randrange(len(alphabet))
        mypw = mypw + alphabet[next_index]

    return mypw


aclcli = None


def aclapi_cli():
    global aclcli
    if aclcli is None:
        aclcli = Client(conf.ACLAPI_USER, conf.ACLAPI_PASS, conf.ACLAPI_URL)
    return aclcli


def permit_keystone_access(unit_host):
    syslog.syslog("Permitting access to keystone host...")
    syslog.syslog("Host is: {} port: {}; unit host is: {}".format(conf.KEYSTONE_HOST, conf.KEYSTONE_PORT, unit_host))
    l4_opts = L4Opts("eq", conf.KEYSTONE_PORT, "dest")
    resp = aclapi_cli().add_tcp_permit_access(
        desc="keystone access (swift service) for tsuru unit: {}".format(unit_host),
        source="{}/32".format(unit_host),
        dest="{}/32".format(socket.gethostbyname(conf.KEYSTONE_HOST)),
        l4_opts=l4_opts
    )
    syslog.syslog("Response is: {} - {}".format(resp.status_code, resp.content))


def permit_swift_access(unit_host):
    syslog.syslog("Permitting access to swift host...")
    syslog.syslog("Host is: {} port: {}; unit host is: {}".format(conf.SWIFT_API_HOST, conf.SWIFT_API_PORT, unit_host))
    l4_opts = L4Opts("eq", conf.SWIFT_API_PORT, "dest")
    resp = aclapi_cli().add_tcp_permit_access(
        desc="swift api access (swift service) for tsuru unit: {}".format(unit_host),
        source="{}/32".format(unit_host),
        dest="{}/32".format(socket.gethostbyname(conf.SWIFT_API_HOST)),
        l4_opts=l4_opts
    )
    syslog.syslog("Response is: {} - {}".format(resp.status_code, resp.content))
