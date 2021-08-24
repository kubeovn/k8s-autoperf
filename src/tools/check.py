
def check_int(data):
    if not isinstance(data, int):
        raise Exception("data not int")


def check_msglen(msglen):
    check_int(msglen)
    if msglen < 14:
        raise Exception("message length must greater than 14")


def check_protocol(protocol):
    if protocol != "tcp" and protocol != "udp":
        raise Exception("protocol unsupported")


def check_port(port):
    check_int(port)
    if port < 1024 or port > 65535:
        raise Exception("port unsupported")

