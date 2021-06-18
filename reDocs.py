import docutils.nodes
from docutils import core
from docutils.writers.html4css1 import Writer,HTMLTranslator
from docutils.core import publish_doctree, publish_from_doctree
from docutils.parsers.rst import directives

from reDocdirectives import Details
from reDocdirectives import ContentCard
directives.register_directive("details", Details)
directives.register_directive("contentcard",ContentCard)

from os import listdir, getcwd, chdir, makedirs
from os.path import isdir, isfile, join, expanduser
from shutil import copyfile

contentDir = "_files"
settingsFile = "redocs.json"
headerFile = "header.rst"
contentsFile = "contents.rst"
baseURL="https://github.com/kata-containers/documentation"
gitHubMasterPath = "/tree/master"

class HTMLFragmentTranslator( HTMLTranslator ):

    def __init__( self, document ):
        HTMLTranslator.__init__( self, document )
        self.head_prefix = ['','','','','']
        headerFrame = "<div class=\"header\" id=\"header\">\n<iframe src=\"header.html\" frameborder=\"0\" width=\"100%\" height=\"100px\">\n</iframe>\n</div>\n"
        contentsFrame = "<div class=\"toc\" id=\"table-of-contents\">\n<iframe src=\"contents.html\" frameborder=\"0\" height=\"800px\">\n</iframe>\n</div>\n"
        cssLinks = "<link rel=\"stylesheet\" href=\"css/plain.css\" type=\"text/css\" />\n<link rel=\"stylesheet\" href=\"css/minimal.css\" type=\"text/css\" />\n<link rel=\"stylesheet\" href=\"css/layout.css\" type=\"text/css\" />\n<link rel=\"stylesheet\" href=\"css/custom.css\" type=\"text/css\" />\n"
        self.body_prefix = [cssLinks + '</head>\n</body>\n<div class="container">\n' + headerFrame + '<div class="row">\n' + contentsFrame]
        self.body_suffix = ['</div>\n</div>\n</body>\n</html>\n']
        self.stylesheet = []

class HeaderFragmentTranslator(HTMLTranslator):

    def __init__( self, document ):
        HTMLTranslator.__init__( self, document )
        self.head_prefix = ['','','','','']
        baseTarget = "<base target=\"_parent\">\n"
        cssLinks = "<link rel=\"stylesheet\" href=\"css/contents.css\" type=\"text/css\" />\n"
        self.body_prefix.insert(0,cssLinks)
        self.body_prefix.insert(0,baseTarget)
        self.stylesheet = []


class ContentsFragmentTranslator(HTMLTranslator):

    def __init__( self, document ):
        HTMLTranslator.__init__( self, document )
        self.head_prefix = ['','','','','']
        baseTarget = "<base target=\"_parent\">\n"
        cssLinks = "<link rel=\"stylesheet\" href=\"css/contents.css\" type=\"text/css\" />\n"
        self.body_prefix.insert(0,cssLinks)
        self.body_prefix.insert(0,baseTarget)
        self.stylesheet = []


    def visit_details(self, node):
        self.body.append(self.starttag(node, 'details', '\n'))
    
    def depart_details(self, node):
        self.body.append('</details>\n')

    def visit_summary(self, node):
        self.body.append(self.starttag(node, 'summary', ''))
    
    def depart_summary(self, node):
        self.body.append('</summary>\n')


class reDocs:

    def __init__(self, sourcePath, targetPath):
        self.sourcePath = sourcePath
        self.targetPath = targetPath
        self.html_fragment_writer = Writer()
        self.sections = []
        self.currentDepth = 0

    def getSections(self,tree,depth):
        for element in tree:
            if isinstance(element,docutils.nodes.section):
                if isinstance(element[0],docutils.nodes.title):
                    sectionTitle = element[0].astext()
                self.sections.append([depth,sectionTitle,element["ids"][0]])
                self.getSections(element,depth+1)

    def setURLs(self,tree):
        counter = 0
        for element in tree.traverse():
            counter += 1
            if isinstance(element,docutils.nodes.target):
                uri = element["refuri"]
                if(baseURL in uri and gitHubMasterPath in uri):
                    uri = uri.replace(baseURL,"")
                    uri = uri.replace(gitHubMasterPath,"")
                    element["refuri"]=uri
                    print(uri)
        return tree

    def rest2html(self,s,contents=False,header=False):
        if contents:
            self.html_fragment_writer.translator_class = ContentsFragmentTranslator
        elif header:
            self.html_fragment_writer.translator_class = HeaderFragmentTranslator
        else:
            self.html_fragment_writer.translator_class = HTMLFragmentTranslator
        self.sections = []
        tree = publish_doctree(s)
        #print(tree)
        self.getSections(tree,1)
        #self.setURLs(tree)
        htmlparts = core.publish_parts(s,writer=self.html_fragment_writer)
        docTitle = htmlparts["title"]
        docTitle = docTitle.strip()
        return docTitle, self.sections, publish_from_doctree(tree, writer = self.html_fragment_writer)

    def convertDoc(self, doc, restText="",contents=False, header=False):
        htmlTitle = ""
        if restText == "":
            itemPath = join(self.sourcePath,doc)
            with open(itemPath, encoding="utf-8") as restFile:
                restText = restFile.read()
        if restText != None:
            htmlTitle, docSections, htmlText = self.rest2html(restText,contents,header)
        htmlFileName = doc.replace(".rst",".html")
        htmlFilePath = join(self.targetPath,htmlFileName)
        with open(htmlFilePath,"wb") as htmlFile:
            htmlFile.write(htmlText)

        return htmlTitle, docSections, htmlFileName

    def addSupportFiles(self):
        targetCSSPath = join(self.targetPath,"css")
        targetContentPath = join(self.targetPath,contentDir)
        if not isdir(targetCSSPath):
            makedirs(targetCSSPath)
        if not isdir(targetContentPath):
            makedirs(targetContentPath)
        cssDir = join(getcwd(),"css")
        htmlDir = join(getcwd(),"html")
        for contentFile in listdir(contentDir):
            contentFilePath = join(contentDir,contentFile)
            if isfile(contentFilePath):
                copyfile(contentFilePath,join(targetContentPath,contentFile))
        for cssFile in listdir(cssDir):
            cssFilePath = join(cssDir,cssFile)
            if isfile(cssFilePath):
                copyfile(cssFilePath,join(targetCSSPath,cssFile))
        #for htmlFile in listdir(htmlDir):
        #    htmlFilePath = join(htmlDir,htmlFile)
        #    if isfile(htmlFilePath):
        #        copyfile(htmlFilePath,join(self.targetPath,htmlFile))


    def determineIndent(self,depth):
        indent = ""
        if depth != self.currentDepth:
            indent += "\n"
            self.currentDepth = depth
        indent += depth * 2 * " "
        return indent

    def createIndex(self,htmlList):
        indexString = "Index\n#####\n\n"
        for title,fileInfo in htmlList.items():
            self.currentDepth = 0
            fileName = fileInfo[0]
            indexString += "\n.. details:: \n   :title: " + title + "\n   :link: " + fileName + "\n"
            for section in fileInfo[1]:
                depth = section[0]
                sectionTitle = section[1]
                sectionAnchor = section[2]
                indent = self.determineIndent(depth)
                indexString += indent + "-  `" + sectionTitle + " <" + fileName + "#" + sectionAnchor +">`__\n"
        self.convertDoc(contentsFile,indexString,contents=True)
        contentsFilePath = join(self.sourcePath,contentsFile)
        with open(contentsFilePath, "w", encoding="utf-8") as outFile:
            outFile.write(indexString)


    def buildDocs(self):
        print("building into " + str(self.targetPath) + ".")
        fileList = []
        newFileDict = {}
        settingsPath = join(self.sourcePath,settingsFile)
        if isfile(settingsPath):
            print("using existing settings file: " + str(settingsPath))
        noTitleCounter = 0
        for item in listdir(self.sourcePath):
            itemPath = join(self.sourcePath,item)
            if isfile(itemPath) and item.endswith(".rst"):
                if not isdir(self.targetPath):
                    makedirs(self.targetPath)
                if item == contentsFile:
                    htmlTitle, docSections, htmlFileName = self.convertDoc(item,contents=True)
                elif item == headerFile:
                    htmlTitle, docSections, htmlFileName = self.convertDoc(item, header=True)
                else:
                    htmlTitle, docSections, htmlFileName = self.convertDoc(item)
                fileList.append(item)
                if htmlTitle == "" or htmlTitle in newFileDict:
                    htmlTitle = htmlTitle + " " + str(noTitleCounter)
                    noTitleCounter += 1
                newFileDict[htmlTitle]=[htmlFileName,docSections]
        if len(newFileDict) != 0:
            self.addSupportFiles()
            contentsFilePath = join(self.sourcePath,contentsFile)
            if not isfile(contentsFilePath):
                self.createIndex(newFileDict)

