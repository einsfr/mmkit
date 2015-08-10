import os


def in_path(parent, child):
    if parent == child:
        return False
    head, tail = os.path.split(child)
    if not tail:
        return False
    if head == parent:
        return True
    return in_path(parent, head)
