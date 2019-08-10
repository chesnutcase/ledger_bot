import decimal

from utils import msgutils
from utils import tableutils


def run(message):
    sender = message["from"]["id"]
    gid = message["chat"]["id"]
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
