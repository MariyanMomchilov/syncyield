from core import get_scheduler
from async_io import AsyncStdInWrapper

scheduler = get_scheduler()
async_in = AsyncStdInWrapper()


async def sleeper():
    while True:
        print('...')
        await scheduler.sleep(2)


async def main():
    while True:
        chars = await async_in.read()
        print(f'Chars: {chars}')
        await scheduler.sleep(1)


scheduler.call_soon(main())
scheduler.call_soon(sleeper())
scheduler.run()
