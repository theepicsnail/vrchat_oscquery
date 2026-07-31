"""Simple example of using the threaded impl.

This will listen for OSC messages from VRChat to determine if you're muted or
not. Then send that status back to VRChat.

python -m examples.foregroundThreadingExample
"""

from vrchat_oscquery.threaded import vrc_osc
from vrchat_oscquery.common import vrc_client, dict_to_dispatcher


client = vrc_client()


def onMuteChanged(unused_osc_addr, muted):
    """Called when the client mutes/unmutes."""
    if muted:
        client.send_message('/chatbox/input', ("Muted", True, False))
    else:
        client.send_message('/chatbox/input', ("Unmuted", True, False))


def foregroundThreadExample():
    # Starts the server in the current thread, blocking forever.
    try:
        vrc_osc("foreground thread chatbox example", dict_to_dispatcher({
            "/avatar/parameters/MuteSelf": onMuteChanged
        }), foreground=True)
    except KeyboardInterrupt:
        print("Exiting!")


if __name__=="__main__":
    foregroundThreadExample()
    