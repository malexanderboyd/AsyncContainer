import random
import dataclasses
import asyncio
import uuid
import os
from src.async_subprocess import call


@dataclasses.dataclass
class ImageInstanceGroup:
    name: str
    type: str
    path: str
    id: int = dataclasses.field(default=uuid.uuid4())


async def kickoff(test_items):
    try:
        kickoff_id = uuid.uuid4()
        await test(kickoff_id, test_items)
    except Exception as e:
        print(f'Exception raised during kickoff ({kickoff_id})\n {e}')
    finally:
        loop.stop()


async def test(kickoff_id, test_items):
    print(f'Starting testing for kickoff {kickoff_id}')
    queue = asyncio.Queue()
    image_building_coros = [handle_build_exceptions(image_building(queue, item)) for item in test_items]
    wrapped_attacking = handle_attack_exceptions(attacking(queue))

    await asyncio.gather(*image_building_coros, wrapped_attacking)


async def handle_build_exceptions(coro):
    try:
        await coro
    except Exception as e:
        print(f'exception during image building - {e}')


async def image_building(queue, item):
    print(f'building image {item.name} ({item.id})')
    await call(' '.join(['docker', 'build', '-t', f'{item.name}', f'{item.path}']))
    await queue.put(item)
    print(f'finished building {item.name} ({item.id})')


async def attacking(queue):
    while True:
        iig = await queue.get()
        asyncio.create_task(attack_image(iig))


async def attack_image(iig):
    print(f'Attacking {iig.name} ({iig.id})')
    for i in range(random.randint(1, 3)):
        await call(f'docker run -d -p {random.randint(8000,9000)}:8000 {iig.name}')
    print(f'Done attacking {iig.name} ({iig.id})')


def cleanup_kickoff(msg, fut):
    print(f'Done {msg}')


async def handle_attack_exceptions(coro):
    try:
        await coro
    except Exception as e:
        print(f'exception during coroutine - {e}')


if __name__ == '__main__':

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'apps')

    build_items = [ImageInstanceGroup(name='python_build_1', type='Python', path=path),
                   ImageInstanceGroup(name='python_build_2', type='Python', path=path)
                   # ImageInstanceGroup(name='python_build_3 ', type='Python', path=path)
                   ]

    loop = asyncio.get_event_loop()

    try:
        loop.create_task(kickoff(build_items))
        loop.run_forever()
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        loop.stop()
