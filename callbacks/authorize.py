import time
from datetime import datetime

from utils import tableutils
from utils import teleutils


def run(callback_query):
    print(callback_query)
    gid = callback_query["message"]["chat"]["id"]
    mid = callback_query["message"]["message_id"]  # of the bot's, not the original user message
    transaction = tableutils.find_transaction(gid, callback_query["message"]["reply_to_message"]["message_id"])
    # cannot find transaction, whoops
    if transaction is None:
        payload = {
            'method': 'answerCallbackQuery',
            'callback_query_id': callback_query["id"],
            'text': 'ERROR: Transaction not found!'
        }
        return payload
    # don't allow others to authorize this charge on their behalf
    if callback_query["from"]["id"] != transaction["to"]:
        payload = {
            'method': 'answerCallbackQuery',
            'callback_query_id': callback_query["id"],
            'text': 'Only the indebted can authorize the charge!'
        }
        return payload
    # all correct
    transaction["on_hold"] = False
    tableutils.update_transaction(transaction)
    sender_name, mentioned_name = tableutils.resolve_ids_to_names([transaction["from"], transaction["to"]])
    total_amt, description = transaction["amt"], transaction.get("description")
    time_now = int(time.time())
    same_day = (time_now - int(transaction["timestamp"])) // 86400 == 0
    if same_day:
        authorized_timestamp = datetime.utcfromtimestamp(time_now).strftime('%H:%M')
    else:
        authorized_timestamp = datetime.utcfromtimestamp(time_now).strftime('%Y-%m-%d %H:%M')
    if description is not None:
        text_message = "{} has charged {} ${:3.2f} for {}.\n<b>Authorized at {}</b>.".format(sender_name, mentioned_name, total_amt, description, authorized_timestamp)
    else:
        text_message = "{} has charged {} ${:3.2f}.\n<b>Authorized at {}</b>".format(sender_name, mentioned_name, total_amt, authorized_timestamp)
    update_payload = {
        'chat_id': gid,
        'message_id': mid,
        'text': text_message,
        'parse_mode': 'HTML'
    }
    update_result = teleutils.call_method("editMessageText", update_payload)
    payload = {
        'method': 'answerCallbackQuery',
        'callback_query_id': callback_query["id"],
        'text': "Charge authorised!"
    }
    return payload
