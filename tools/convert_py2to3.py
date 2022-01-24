"""Utility to convert py2 rhino-python files to py3 format"""
import os
import os.path as op
import shutil
from lib2to3.main import main  # this is what 2to3 cli utility uses


# read sources
SOURCE_DIR = r"../Scripts/"
DEST_DIR = r"../python3/"

ITEMS = [
    r"rhinoscript/",
    r"rhinoscriptsyntax.py",
    r"scriptcontext.py",
]


THIS_DIR = op.dirname(__file__)
ROOT_DIR = op.dirname(THIS_DIR)
print(f"{THIS_DIR=}")
print(f"{ROOT_DIR=}")


class SourceFile:
    """Context manager for a python source file"""

    def __init__(self, filename) -> None:
        self.filename = filename
        self.source = ""

    def __enter__(self):
        with open(self.filename, "r") as rf:
            self.source = rf.read()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        with open(self.filename, "w") as wf:
            wf.write(self.source)

    def replace(self, *args, **kwargs):
        """Replace string in source"""
        self.source = self.source.replace(*args, **kwargs)


def prep_dest(source, dest):
    """Prepare a new copy of source files"""
    if op.exists(dest):
        print(f"Deleting: {dest}")
        if op.isdir(dest):
            shutil.rmtree(dest)
        else:
            os.remove(dest)

    print(f"Updating: {dest}")
    if op.isdir(source):
        shutil.copytree(source, dest)
    else:
        shutil.copy(source, dest)


def convert_dest(dest):
    """Convert files to python3-compatible"""
    print(f"Converting: {dest}")
    main("lib2to3.fixes", args=["--write", "--nobackups", "--no-diffs", dest])


def apply_dest_fixes(dest):
    """Apply misc fixes to files"""

    def apply_fixes(item):
        item_name = op.splitext(op.basename(item))[0]
        fixer_func_name = f"{item_name}_fixes"
        if fixer_func := globals().get(fixer_func_name, None):
            fixer_func(item)

    print(f"Applying Fixes: {dest}")
    if op.isdir(dest):
        for dest_item in os.listdir(dest):
            apply_fixes(op.join(dest, dest_item))
    else:
        apply_fixes(dest)


# Fixers ======================================================================
# function naming format is <file_name>_fixes
# e.g. scriptcontext_fixes applies fixes to scriptcontext.py
# -----------------------------------------------------------------------------


def scriptcontext_fixes(item):
    """Fix misc items in scriptcontext.py"""
    with SourceFile(item) as sf:
        sf.replace("doc = None", "doc = __rhinodoc__")


def layer_fixes(item):
    """Fix misc items in rhinoscript/layer.py"""
    with SourceFile(item) as sf:
        sf.replace("if idx is 0:", "if idx == 0:")


# =============================================================================

if __name__ == "__main__":
    for item in ITEMS:
        source = op.normpath(op.join(THIS_DIR, SOURCE_DIR, item))
        dest = op.normpath(op.join(THIS_DIR, DEST_DIR, item))

        prep_dest(source, dest)
        convert_dest(dest)
        apply_dest_fixes(dest)