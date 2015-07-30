import os


def is_subdir(parent_dir, subdir):
        if parent_dir == subdir:
            return False
        head, tail = os.path.split(subdir)
        if not tail:
            return False
        if head == parent_dir:
            return True
        return is_subdir(parent_dir, head)
