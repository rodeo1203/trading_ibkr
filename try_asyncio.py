# #!/usr/bin/env python3
# # countasync.py

import asyncio
import time

async def count1():
    print("One")
    await asyncio.sleep(20)
    await asyncio.sleep(10)
    print("Two")
    await asyncio.sleep(2)
    print("seven")
async def count2():
    print("Three")
    # await asyncio.sleep(1)
    time.sleep(10)
    print("Four")
    await asyncio.sleep(1)
    print("five")

async def main():
    # await count1()
    # await count2()
    await asyncio.gather(count1(), count2())


asyncio.run(main())





# import asyncio
# import random
# import time

# async def part1(n):
#     i = random.randint(0, 10)
#     print(f"part1({n}) sleeping for {i} seconds.")
#     await asyncio.sleep(i)
#     print(f"Returning part1({n}")
#     return n

# async def part2(n):
#     i = random.randint(0, 10)
#     print(f"part2{n} sleeping for {i} seconds.")
#     await asyncio.sleep(i)

#     print(f"Returning part2{n }")
#     return n

# async def chain(n):
#     start = time.time()
#     p1 = await part1(n)
#     p2 = await part2(n+1)
#     end = time.time()-start
#     print(f"{end}")

# async def main(*args):
#     await asyncio.gather(part1(1), part2(1))


# s=time.time()
# asyncio.run(main(2))
# print(time.time()-s)
