import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
import asyncio
import aiohttp
import contextlib
import os
from dotenv import load_dotenv
load_dotenv()





from limoo import LimooDriver

                
async def respond(event):
    # We only process events that inform us of new messages being created.
    # We have to make sure that the created message is not a system message and
    # that it was not created by us. Non-system messages have "null" as their
    # "type".
    if os.environ['ENDPOINT'] != "":
        endpoint_url = os.environ['ENDPOINT']
    else:
        endpoint_url = 'https://gitlab.com/api/v4/projects?owned=True'
    if (event['event'] == 'message_created'
        and not (event['data']['message']['type']
                 or event['data']['message']['user_id'] == self['id'])):
        message_id = event['data']['message']['id']
        thread_root_id = event['data']['message']['thread_root_id']
        direct_reply_message_id = event['data']['message']['thread_root_id'] and event['data']['message']['id']
        # If the received message is part of a thread, it will have
        # thread_root_id set and we need to reuse that thread_root_id so that
        # our message ends up in the same thread. We also set
        # direct_reply_message_id to the id of the message so our message is
        # sent as a reply to the received message. If however, the received
        # message does not have thread_root_id set, we will create a new thread
        # by setting thread_root_id to the id of the received message. In this
        # case, we must set direct_reply_message_id to None.
        # for User_access in User_accesses:
        text = event['data']['message']['text']
        command = text.split(' ')
        service_name = command[0].replace('/', '')
        token = command[1]

        # res = await send_request(
        #     # url='https://gitlab.com/api/v4/projects/29089846',
        #     # url='https://gitlab.com/api/v4/projects?owned=True',
        #     # auth_token='okRu4VC3giur9XWSYCjt'
        #     url='https://gitlab.com/api/v4/projects?owned=True',
        #     auth_token=token
        # )
        headers={"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(endpoint_url) as res:
                if res.status == 200:
                    projects = await res.json()
                    if type(projects) == list:
                        for project in projects:
                            if project['visibility'] == 'private':
                                response = await ld.messages.create(
                                    event['data']['workspace_id'],
                                    event['data']['message']['conversation_id'],
                                    project['name'],
                                    thread_root_id=thread_root_id or message_id,
                                    direct_reply_message_id=thread_root_id and message_id
                                )
                    else:
                        response = await ld.messages.create(
                                event['data']['workspace_id'],
                                event['data']['message']['conversation_id'],
                                projects['message'],
                                thread_root_id=thread_root_id or message_id,
                                direct_reply_message_id=thread_root_id and message_id
                            )
                else:
                    response = await ld.messages.create(
                        event['data']['workspace_id'],
                        event['data']['message']['conversation_id'],
                        f"""عملیات دریافت اطلاعات از گیتلب با مشکل مواجه شده است
                        وضعیت : {res.status}"""
                        ,
                        thread_root_id=thread_root_id or message_id,
                        direct_reply_message_id=thread_root_id and message_id
                    )
                


async def listen(ld):
    forever = asyncio.get_running_loop().create_future()
    # The given event_handler will be called on the event loop thread for each
    # event received from the WebSocket. Also it must be a normal function and
    # not a coroutine therefore we create our own task so that our coroutine
    # gets executed.
    ld.set_event_handler(lambda event: asyncio.create_task(respond(event)))
    await forever

async def main():
    global ld, self
    username = os.environ['USER']
    password = os.environ['PASS']
    async with contextlib.AsyncExitStack() as stack:
        ld = LimooDriver('web.limoo.im', username, password)
        stack.push_async_callback(ld.close)
        # Calling ld.users.get without any arguments gets information
        # about the currently logged in user
        self = await ld.users.get()
        await listen(ld)


asyncio.run(main())
