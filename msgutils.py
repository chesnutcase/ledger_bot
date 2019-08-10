"""
Module for parsing telegram text messages.
"""
import re

import teleutils


class MsgException(Exception):
    def __init__(self, msg, gid):
        self.error_payload = {
            'method': 'sendMessage',
            'chat_id': gid,
            'text': "<b>ERROR:</b> {}".format(msg),
            'parse_mode': 'HTML'
        }


def extract_mentions_and_payment_amounts(message):
    gid = int(message["chat"]["id"])
    mention_message_entities = [e for e in message["entities"] if e["type"] in ["mention", "text_mention"]]
    if len(mention_message_entities) == 0:
        raise MsgException(r'Please <b>mention</b> (type @) the user you want to owe/pay to as the first argument of the command!', gid)
    mention_message_entities.sort(key=lambda e: e["offset"])
    mention_message_entity = mention_message_entities.pop()
    mentioned_name = message["text"][mention_message_entity["offset"]:mention_message_entity["offset"] + mention_message_entity["length"]]
    number_matches = re.match(r'(\d+\.?\d*) ?(\d+\.?\d*)?', message["text"][mention_message_entity["offset"] + mention_message_entity["length"]:].strip())
    if number_matches is None:
        raise MsgException(r'I dont see the numbers, mason! Please enter the format /owe@{} <username> <amount> <?tax> <?description>'.format(teleutils.BOT_NAME), gid)
    nett_price = float(number_matches.group(1))
    percentage_multiplier = float(number_matches.group(2) or 0)
    description = message["text"][mention_message_entity["offset"] + mention_message_entity["length"]:].strip()[number_matches.span()[1]:].strip() or None
    return (mentioned_name, nett_price, percentage_multiplier, description)
