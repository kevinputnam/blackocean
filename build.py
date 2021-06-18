from reDocs import reDocs
from os import getcwd
from os.path import join

cwd = getcwd()
targetPath = join(cwd + "/_build/reDocs")

redocs = reDocs(cwd,targetPath)
redocs.buildDocs()
