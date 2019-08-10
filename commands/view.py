from utils import tableutils


def run(message):
    gid = message["chat"]["id"]
    # TODO
    sender = message["from"]["id"]
    sender_name = "@{}".format(message["from"]["username"]) if "username" in message["from"] else "{} {}".format(message["from"].get("first_name", ""), message["from"].get("last_name", ""))
    account = tableutils.view_account(gid, sender)
    uids = account.keys()
    # values = account.values()
    usernames = tableutils.resolve_ids_to_names(list(uids))
    uids_to_usernames = dict(zip(uids, usernames))
    debit_lines = ["<code>{:16}  {:3.2f}</code>".format(uids_to_usernames[k], abs(v)) for k, v in account.items() if v < 0]
    debit_block = "\nYou owe these people money:\n{}".format("\n".join(debit_lines)) if len(debit_lines) > 0 else ""
    credit_lines = ["<code>{:16}  {:3.2f}</code>".format(uids_to_usernames[k], v) for k, v in account.items() if v > 0]
    credit_block = "\nThese people owe you money:\n{}".format("\n".join(credit_lines)) if len(credit_lines) > 0 else ""
    payload = {
        'method': 'sendMessage',
        'chat_id': gid,
        'text': "<b>Debts for {}</b> \n{}\n{}".format(sender_name, debit_block, credit_block),
        'parse_mode': 'HTML'
    }
    return payload
