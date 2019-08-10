def run(message):
    gid = message["chat"]["id"]
    payload = {
        'method': 'sendMessage',
        'chat_id': gid,
        'text': 'Pong!'
    }
    return payload
