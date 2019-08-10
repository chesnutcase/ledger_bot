import re
import os
import decimal

import msgutils
import tableutils
import teleutils

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
        command_match = re.match(r'/(\w+)@{}'.format(teleutils.BOT_NAME), message["text"])
        if command_match is not None:
            # open connection to database and set vars
            gid = int(message["chat"]["id"])
            mid = int(message["message_id"])
            tableutils.open_connections_and_tables()
            # check what command it is and dispatch
            command = command_match.group(1)
            try:
                # registration check
                if command != "register":
                    if tableutils.resolve_ids_to_names([message["from"]["id"]])[0] is None:
                        raise msgutils.MsgException(r'Please register yourself with the /register@{} command before using the bot!'.format(teleutils.BOT_NAME), gid)
                if command == "owe":
                    # TODO
                    sender = message["from"]["id"]
                    mentioned_name, nett_price, percentage_multiplier, description = msgutils.extract_mentions_and_payment_amounts(message)
                    receiver = tableutils.resolve_names_to_ids([mentioned_name])[mentioned_name]
                    if receiver is None:
                        raise msgutils.MsgException(r'User {} not found, is he registered in the ledger?'.format(mentioned_name), gid)
                    if receiver == sender:
                        raise msgutils.MsgException(r"You can't owe yourself money!", gid)
                    total_amt = decimal.Decimal(nett_price) + (decimal.Decimal(percentage_multiplier) / 100 * decimal.Decimal(nett_price))
                    total_amt = round(total_amt, 2)
                    if total_amt == 0:
                        raise msgutils.MsgException(r'Please enter a value more than 0!', gid)

                    tableutils.debit_transaction(gid, sender, receiver, total_amt, msg_id=message["message_id"], description=description)
                    sender_name = "@{}".format(message["from"]["username"]) if "username" in message["from"] else "{} {}".format(message["from"].get("first_name", ""), message["from"].get("last_name", ""))
                    payload = {
                        'method': 'sendMessage',
                        'chat_id': gid,
                        'text': "{}'s debt to {} has increased by ${:3.2f}".format(sender_name, mentioned_name, total_amt)
                    }
                    return payload

                elif command == "pay":
                    # TODO
                    sender = message["from"]["id"]
                    mentioned_name, nett_price, percentage_multiplier, description = msgutils.extract_mentions_and_payment_amounts(message)
                    receiver = tableutils.resolve_names_to_ids([mentioned_name])[mentioned_name]
                    if receiver is None:
                        raise msgutils.MsgException(r'User {} not found, is he registered in the ledger?'.format(mentioned_name), gid)
                    if receiver == sender:
                        raise msgutils.MsgException(r"You can't pay yourself money!", gid)
                    total_amt = decimal.Decimal(nett_price)
                    total_amt = round(total_amt, 2)
                    if total_amt == 0:
                        raise msgutils.MsgException(r'Please enter a value more than 0!', gid)

                    tableutils.credit_transaction(gid, sender, receiver, total_amt, msg_id=message["message_id"])
                    sender_name = "@{}".format(message["from"]["username"]) if "username" in message["from"] else "{} {}".format(message["from"].get("first_name", ""), message["from"].get("last_name", ""))
                    payload = {
                        'method': 'sendMessage',
                        'chat_id': gid,
                        'text': "{}'s debt to {} has decreased by ${:3.2f}".format(sender_name, mentioned_name, total_amt)
                    }
                    return payload
                elif command == "view":
                    # TODO
                    sender = message["from"]["id"]
                    sender_name = "@{}".format(message["from"]["username"]) if "username" in message["from"] else "{} {}".format(message["from"].get("first_name", ""), message["from"].get("last_name", ""))
                    account = tableutils.view_account(gid, sender)
                    uids = account.keys()
                    #values = account.values()
                    usernames = tableutils.resolve_ids_to_names(list(uids))
                    uids_to_usernames = dict(zip(uids, usernames))
                    debit_lines = ["{:10}  {}".format(uids_to_usernames[k], abs(v)) for k, v in account.items() if v < 0]
                    debit_block = "\nYou owe these people money:\n{}".format("\n".join(debit_lines)) if len(debit_lines) > 0 else ""
                    credit_lines = ["{:10}  {}".format(uids_to_usernames[k], v) for k, v in account.items() if v > 0]
                    credit_block = "\nThese people owe you money:\n{}".format("\n".join(credit_lines)) if len(credit_lines) > 0 else ""
                    payload = {
                        'method': 'sendMessage',
                        'chat_id': gid,
                        'text': "<b>Debts for {}</b> \n{}\n{}".format(sender_name, debit_block, credit_block),
                        'parse_mode': 'HTML'
                    }
                    return payload

                elif command == "resolve":
                    # TODO
                    raise msgutils.MsgException("Command not implemented yet", gid)
                    # tableutils.resolve_transactions("gid", "sender", "receiver", "amt")
                elif command == "register":
                    uid = int(message["from"]["id"])
                    name = "{} {}".format(message["from"].get("first_name", ""), message["from"].get("last_name", ""))
                    username = message["from"]["username"]
                    tableutils.register_user(uid, username=username, name=name)
                    payload = {
                        'method': 'sendMessage',
                        'chat_id': gid,
                        'text': r'Your user id *{}* has been registered!'.format(str(uid)),
                        'parse_mode': 'Markdown'
                    }
                    return payload
                elif command == "ping":
                    payload = {
                        'method': 'sendMessage',
                        'chat_id': gid,
                        'text': 'Pong!'
                    }
                    return payload
                else:
                    payload = {
                        'method': 'sendMessage',
                        'chat_id': gid,
                        'text': 'Nani?'
                    }
                    return payload
            except msgutils.MsgException as ex:
                return ex.error_payload

    # TODO implement
    return {
        'statusCode': 200,
        'body': "nothing interesting happens."
    }
