from reDocs import reDocs
from reDocs import ignoreFiles
from os import getcwd
from os.path import join

cwd = getcwd()
targetPath = join(cwd + "/_build/reDocs")

ignoreFiles.append('js_basic_game')
redocs = reDocs(cwd,targetPath)
redocs.buildDocs()
