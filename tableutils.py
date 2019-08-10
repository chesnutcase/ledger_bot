import boto3
import time
import decimal
from boto3.dynamodb.conditions import Key, Attr

CONN = None
TRANSACTIONS_TABLE_NAME = None
USERS_TABLE_NAME = None
TRANSACTIONS_TABLE = None
USERS_TABLE = None


def open_connections_and_tables():
    global CONN
    global TRANSACTIONS_TABLE
    global USERS_TABLE
    CONN = boto3.resource('dynamodb')
    TRANSACTIONS_TABLE = CONN.Table(TRANSACTIONS_TABLE_NAME)
    USERS_TABLE = CONN.Table(USERS_TABLE_NAME)


def resolve_names_to_ids(names):
    ids = []
    for name in names:
        field_to_use = 'username' if name[0] == "@" else 'name'
        value_to_use = name[1:] if name[0] == "@" else name
        items = USERS_TABLE.scan(
            FilterExpression=Attr(field_to_use).eq(value_to_use)
        )["Items"]
        if len(items) != 0:
            ids.append(items.pop()["id"])
        else:
            ids.append(None)
    return dict(zip(names, ids))


def resolve_ids_to_names(ids):
    names = []
    for id in ids:
        items = USERS_TABLE.query(
            KeyConditionExpression=Key('id').eq(id),
        )["Items"]
        if len(items) > 0:
            names.append("@{}".format(items[0]["username"]) if "username" in items[0] else items[0]["name"])
        else:
            names.append(None)
    return names


def debit_transaction(gid, sender, receiver, amt, *, msg_id=None, description=""):
    with decimal.localcontext(boto3.dynamodb.types.DYNAMODB_CONTEXT) as ctx:
        ctx.traps[decimal.Inexact] = False
        ctx.traps[decimal.Rounded] = False
        timestamp = ctx.create_decimal_from_float(time.time())
        item = {
            'group_id': gid,
            'id': msg_id,
            'from': sender,
            'to': receiver,
            'amt': -abs(amt),
            'timestamp': round(timestamp, 2)
        }
        if description is not None and description.strip() != "":
            item["description"] = description.strip()
        TRANSACTIONS_TABLE.put_item(Item=item)


def credit_transaction(gid, sender, receiver, amt, *, msg_id=None):
    with decimal.localcontext(boto3.dynamodb.types.DYNAMODB_CONTEXT) as ctx:
        ctx.traps[decimal.Inexact] = False
        ctx.traps[decimal.Rounded] = False
        timestamp = ctx.create_decimal_from_float(time.time())
        TRANSACTIONS_TABLE.put_item(Item={
            'group_id': gid,
            'id': msg_id,
            'from': sender,
            'to': receiver,
            'amt': abs(amt),
            'timestamp': round(timestamp, 2)
        })


def view_account(gid, user):
    gid = int(gid)
    user = int(user)
    response = TRANSACTIONS_TABLE.query(
        Select='ALL_ATTRIBUTES',
        KeyConditionExpression=Key('group_id').eq(int(gid)) & Key('timestamp').gt(0),
        FilterExpression=Attr('from').eq(int(user)) | Attr('to').eq(int(user))
    )
    entries = response["Items"]
    account = {}
    for entry in entries:
        is_payment = entry["amt"] > 0
        is_receiver = entry["to"] == user
        print(entry, is_payment, is_receiver)

        dict_key = entry["from"] if is_receiver else entry["to"]
        if dict_key not in account:
            account[dict_key] = 0
        account[dict_key] = account[dict_key] + (entry["amt"] * (-1 if is_receiver else 1))
    return account


def register_user(uid, *, username="", name=""):
    data = {
        "id": int(uid)
    }
    username = username.strip()
    name = name.strip()
    if username != "":
        data["username"] = username
    if name != "":
        data["name"] = name
    USERS_TABLE.put_item(Item=data)
