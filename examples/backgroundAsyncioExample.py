"""Simple example of using the asyncio impl.

This will listen for OSC messages from VRChat to determine if you're muted or
not. Then send that status back to VRChat.

python -m examples.backgroundAsyncioExample
"""

import asyncio
from vrchat_oscquery.asyncio import vrc_osc
from vrchat_oscquery.common import vrc_client, dict_to_dispatcher


client = vrc_client()


def onMuteChanged(unused_osc_addr, muted):
    """Called when the client mutes/unmutes."""
    if muted:
        client.send_message('/chatbox/input', ("Muted", True, False))
    else:
        client.send_message('/chatbox/input', ("Unmuted", True, False))


async def main():
    # Starts the server in another event loop.
    await vrc_osc("background async chatbox example", dict_to_dispatcher({
        "/avatar/parameters/MuteSelf": onMuteChanged
    }))

    # We can now do whatever we want, you'll see a notification in vrc when
    # vrc has connected to the server.
    for _ in range(10):
        await asyncio.sleep(1)
        print("Other asyncio tasks can run.")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
