


from ..abc.sink  import Sink

...

# import asyncio, asyncssh, sys
#
# async def run_client():
#     async with asyncssh.connect('localhost') as conn:
#         async with conn.create_process('bc') as process:
#             for op in ['2+2', '1*2*3*4', '2^32']:
#                 process.stdin.write(op + '\n')
#                 result = await process.stdout.readline()
#                 print(op, '=', result, end='')
#
# try:
#     asyncio.get_event_loop().run_until_complete(run_client())
# except (OSError, asyncssh.Error) as exc:
#     sys.exit('SSH connection failed: ' + str(exc))