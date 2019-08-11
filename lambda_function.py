import re
import os
import importlib

from utils import msgutils
from utils import tableutils
from utils import teleutils

teleutils.BOT_NAME = os.environ.get("BOT_NAME")
BOT_API_KEY = os.environ.get("BOT_API_KEY")
teleutils.API_URL = r'https://api.telegram.org/bot{}'.format(BOT_API_KEY)
tableutils.TRANSACTIONS_TABLE_NAME = os.environ.get("TRANSACTIONS_TABLE_NAME")
tableutils.USERS_TABLE_NAME = os.environ.get("USERS_TABLE_NAME")


"""
Entry point for API
All exit points must return a message to send back to Telegram.
"""


def lambda_handler(event, context):
    if(event.get("message") is not None):
        message = event["message"]
        if msgutils.message_is_forward(message):
            return "message is forward, ignoring"
        command_match = re.match(r'/(\w+)@{}'.format(teleutils.BOT_NAME), message["text"])
        if command_match is not None:
            # open connection to database and set vars
            gid = message["chat"]["id"]
            # mid = int(message["message_id"])
            tableutils.open_connections_and_tables()
            # check what command it is and dispatch
            command = command_match.group(1)
            try:
                # registration check
                if command != "register":
                    if tableutils.resolve_ids_to_names([message["from"]["id"]])[0] is None:
                        raise msgutils.MsgException(r'Please register yourself with the /register@{} command before using the bot!'.format(teleutils.BOT_NAME), gid)
                try:
                    command_module = importlib.import_module("commands.{}".format(command))
                    return command_module.run(message)
                except ModuleNotFoundError:
                    payload = {
                        'method': 'sendMessage',
                        'chat_id': gid,
                        'text': 'Nani?'
                    }
                    return payload
            except msgutils.MsgException as ex:
                return ex.error_payload
    elif event.get("callback_query") is not None:
        callback_name = event["callback_query"].get("data")
        try:
            if callback_name is not None:
                callback_module = importlib.import_module("callbacks.{}".format(callback_name))
                tableutils.open_connections_and_tables()
                return callback_module.run(event["callback_query"])
            else:
                raise ModuleNotFoundError()
        except ModuleNotFoundError:
            payload = {
                'method': 'answerCallbackQuery',
                'callback_query_id': event["callback_query"]["id"],
                'text': 'Unrecognised callback data'
            }
            return payload

    # TODO implement
    return {
        'statusCode': 200,
        'body': "nothing interesting happens."
    }
