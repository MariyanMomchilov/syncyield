import sys
import os
from core import get_scheduler
from async_io import AsyncTextIOWrapper

scheduler = get_scheduler()
f = open('./samples/test.txt', mode='r', encoding='utf-8')
async_in = AsyncTextIOWrapper(f)
async_out = AsyncTextIOWrapper(sys.stdout)


async def sleeper():
    while True:
        print('...')
        await scheduler.sleep(10)


async def main():
    while True:
        chars = await async_in.read()
        await async_out.write(chars)
        await scheduler.sleep(1)


scheduler.call_soon(main())
scheduler.call_soon(sleeper()) 
scheduler.run()
