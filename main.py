#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets
from pprint import pprint

import util

logging.basicConfig()

users = []


async def JABC(websocket, _):
    try:
        # await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            if data['action'] == 'message':
                await send_message(data, websocket)
            elif data['action'] == 'login':
                await login(data, websocket)
            elif data['action'] == 'logout':
                await logout(data, websocket)
            else:
                logging.error(
                    "unsupported event: {}", data)
    finally:
        pass


async def login(data, websocket):
    if not util.check_if_logged(data['data'], users):
        handshake = hash(data['data'])
        users.append({"login": data['data'], "handshake": handshake, "handle": websocket})

        await websocket.send(json.dumps({"action": "login", "data": str(handshake)}))
        await util.user_logged_in(data['data'], users)
    else:
        # await util.error("User already logged, logout first", websocket)
        await logout({"data": util.get_user_handle(data['data'], users)["handshake"]}, websocket)
        await login(data, websocket)


async def logout(data, websocket):
    pprint(data)
    if util.check_if_logged_by_handshake(int(data['data']), users):
        for user in users:
            if int(data["data"]) == user["handshake"]:
                users.remove(user)
                break

        await websocket.send(json.dumps({"action": "logout", "data": ""}))
        await util.user_logged_out(util.get_username(int(data['data']), users), users)
    else:
        await util.error("Unknown handshake", websocket)


async def send_message(data, handle):
    try:
        if data['handshake'] is not None and data['recipient'] is not None:
            if not util.check_if_logged(data['recipient'], users):
                await util.error("Sorry! The user you want to send the message to is inactive", handle)
                return

            print(
                util.get_username(int(data["handshake"]), users),
                "send message:",
                "'" + data["data"] + "'",
                "to",
                data["recipient"]
            )

            recipient = util.get_user_handle(data["recipient"], users)
            await \
                recipient["handle"].send(json.dumps({
                    "action": "message",
                    "data": data["data"],
                    "recipient": util.get_username(int(data['handshake']), users)
                }))
            # await handle.send(json.dumps({"action": "message", "data": data["data"]}))
        else:
            await util.error("Message is incorrectly formed, or you are not logged in", handle)
    except KeyError:
        await util.error("Message is incorrectly formed, or you are not logged in", handle)


asyncio.get_event_loop().run_until_complete(websockets.serve(JABC, '192.168.0.199', 6789))
asyncio.get_event_loop().run_forever()
