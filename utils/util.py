import glob
import os, sys, winsound
from pathlib import Path
import ast
import importlib.util
from functools import reduce
from datetime import timedelta, datetime


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent


def list_files(folder, mask) -> []:
    """Get list of files full path from folder by mask"""
    return glob.glob(os.path.join(get_project_root(), folder, mask))


def filter_file(file:str, mask:str) -> str:
    res = file
    for p in mask.split('*'):
        res = res.replace(p,'')
    return res


def list_file_names(folder, mask) -> []:
    """Get list of file names from folder by mask"""
    ff = list_files(folder, mask)

    return list(map(lambda x: filter_file(os.path.basename(x), mask), ff))


def file_get_contents(filepath):
    """Get file contents"""
    with open(filepath) as f:
        return f.read()


def file_mtime(filepath):
    return os.path.getmtime(filepath)


def get_class_name(file):
    """Get class name from file path"""
    p = ast.parse(file_get_contents(file))
    classes = [node.name for node in ast.walk(p) if isinstance(node, ast.ClassDef)]
    return classes[0]


def import_file(folder, file):
    """Import file by file path"""
    path = os.path.join(get_project_root(), folder, file)
    class_name = get_class_name(path)
    spec = importlib.util.spec_from_file_location(folder, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    clazz = getattr(module, class_name)
    # return ".".join([clazz.__module__, clazz.__name__])
    return clazz


# Prevent windows to sleep
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
def prevent_sleep():
    import ctypes
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | \
        ES_SYSTEM_REQUIRED)

def allow_sleep():
    import ctypes
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS)

# Datetime section
def dt_diff_seconds(dt1:datetime) -> int:
    dt2 = datetime.utcnow()
    dt = dt2 - dt1
    return dt.total_seconds()

def sort(dic, from_top=None):
    sorted_results = sorted(dic.keys(), reverse=True)
    if from_top:
        sorted_results = sorted_results[:from_top]
    return dict((r, dic[r]) for r in sorted_results)

def beep():
    winsound.Beep(2500, 1500)

if __name__ == "__main__":
    ff = list_file_names('strategy', 'strat_*.py')
    print(ff)
    # for l in ff:
    #     print(import_file(l))