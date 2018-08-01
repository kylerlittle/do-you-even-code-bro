import os

def get_absolute_path(relative_path):
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, relative_path)