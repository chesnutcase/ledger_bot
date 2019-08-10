from utils import tableutils


def run(message):
    gid = message["chat"]["id"]
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
