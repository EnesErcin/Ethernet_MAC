import asyncio


async def listener(event):
    print(f'Waiting for event')
    await event.wait()
    print(f'Event processed')


async def main():
    myevent = asyncio.Event()

    # Spawn a Task to wait until 'event' is set.
    handler = asyncio.create_task(listener(myevent))

    # Sleep for 1 second and set the event.
    await asyncio.sleep(4)
    myevent.set()

    # Wait until processing is complete
    await handler


asyncio.run(main())
# Waiting for event
# Event processed