"""Simple example of using the threaded impl.

This will listen for OSC messages from VRChat to determine if you're muted or
not. Then send that status back to VRChat.

python -m examples.backgroundThreadingExample
"""

from vrchat_oscquery.threaded import vrc_osc
from vrchat_oscquery.common import vrc_client, dict_to_dispatcher
import time


client = vrc_client()


def onMuteChanged(unused_osc_addr, muted):
    """Called when the client mutes/unmutes."""
    if muted:
        client.send_message('/chatbox/input', ("Muted", True, False))
    else:
        client.send_message('/chatbox/input', ("Unmuted", True, False))


def backgroundThreadExample():
    # Starts the server in another thread.
    server = vrc_osc("background thread chatbox example", dict_to_dispatcher({
        "/avatar/parameters/MuteSelf": onMuteChanged
    }))

    # We can now do whatever we want, you'll see a notification in vrc when
    # vrc has connected to the server.
    for _ in range(30):
        time.sleep(1)
        print("Idle in main thread...")

    print("Shutting down")
    server.shutdown()


if __name__ == "__main__":
    backgroundThreadExample()
