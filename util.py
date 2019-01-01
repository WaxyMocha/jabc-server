import json
from pprint import pprint


def check_if_logged(username, users):
    for user in users:
        if username == user["login"]:
            return True
    return False


def check_if_logged_by_handshake(handshake, users):
    for user in users:
        if handshake == user["handshake"]:
            return True
    return False


def get_username(handshake, users):
    for user in users:
        if handshake == user["handshake"]:
            return user["login"]
    return "unknown"


def get_user_handle(username, users):
    for user in users:
        if username == user["login"]:
            return user
    return None


async def error(message, handle):
    print("error:", message)
    await handle.send(json.dumps({"action": "error", "data": message}))


async def user_logged_in(username, users):
    for user in users:
        if username != user["login"]:
            try:
                await user["handle"].send(json.dumps({"action": "userLoggedIn", "data": username}))
            except:
                pass


async def user_logged_out(username, users):
    for user in users:
        if username != user["login"]:
            try:
                await user["handle"].send(json.dumps({"action": "userLoggedOut", "data": username}))
            except:
                pass
