import uuid


def uniqid():
    return uuid.uuid3(
        uuid.uuid1(),
        uuid.uuid4().hex
    ).hex


def node_uniqid():
    uid = uniqid()
    node_uid = 'node%s' % uid
    return node_uid[:-4]


def line_uniqid():
    uid = uniqid()
    node_uid = 'line%s' % uid
    return node_uid[:-4]
