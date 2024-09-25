import asyncio

async def agen():
    print("IN agen")
    a = 0
    while True:
        a+=1
        print("Yelded a")
        yield a
        print("After yield")

g = agen()

async def getmsg():
    print("before 1 agen await")
    a = await anext(g)
    print("after 1 agen await")
    print("before time sleep")
    await asyncio.sleep(10)
    print("after time sleep")
    print(f"Recieved message {a}")

async def selfsetting():
    print("self Start")
    while True:
        print("before 1 adef await")
        await getmsg()
        print("after 1 adef await")

async def other():
    while True:
        print("Other worker")
        await asyncio.sleep(2)

async def s10():
    await asyncio.sleep(6)
    print("6")

async def s1():
    await asyncio.sleep(1)
    print("1")


async def main():
    print("Started main")
    t1 = asyncio.create_task(selfsetting())
    t2 = asyncio.create_task(other())
    await t1
    print("Next phase")
    while True:
        await t2

asyncio.run(main())