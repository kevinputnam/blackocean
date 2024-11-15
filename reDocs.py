import docutils.nodes
from docutils import core
from docutils.writers.html4css1 import Writer,HTMLTranslator
from docutils.core import publish_doctree, publish_from_doctree
from docutils.parsers.rst import directives

from reDocdirectives import Details
from reDocdirectives import ContentCard
from reDocdirectives import Heading
directives.register_directive("details", Details)
directives.register_directive("contentcard",ContentCard)
directives.register_directive("heading",Heading)

from os import listdir, getcwd, chdir, makedirs, walk
from os.path import isdir, isfile, join, expanduser, relpath
from shutil import copyfile, copytree

contentDir = "_files"
settingsFile = "redocs.json"
headerFile = "header.rst"
contentsFile = "contents.rst"
baseURL="https://github.com/kata-containers/documentation"
gitHubMasterPath = "/tree/master"
ignoreFiles = [headerFile,contentsFile]

contentCSSList = ["css/plain.css","css/minimal.css","css/layout.css","css/custom.css","css/fortune_cards.css"]

contentExtraHead = '''
<link rel="stylesheet" href="css/plain.css" type="text/css" />
<link rel="stylesheet" href="css/minimal.css" type="text/css" />
<link rel="stylesheet" href="css/layout.css" type="text/css" />
<link rel="stylesheet" href="css/custom.css" type="text/css" />
'''

contentFrameFiles = ["header.html","contents.html"]

contentFrames = '''<div class="container">
<div class="header" id="header">
<iframe src="header.html" scrolling="no" frameborder="0" width="100%" height="100px">
</iframe>
</div>
<div class="row">
<div class="toc" id="table-of-contents">
<iframe src="contents.html" frameborder="0" height="800px">
</iframe>
</div>
'''

indexExtraHead = '''<base target="_parent">
<link rel="stylesheet" href="css/contents.css" type="text/css" />
'''
headerExtraHead = '''<base target="_parent">
<link rel="stylesheet" href="css/header.css" type="text/css" />
'''

class ContentsFragmentTranslator(HTMLTranslator):

    def visit_details(self, node):
        self.body.append(self.starttag(node, 'details', '\n'))
    
    def depart_details(self, node):
        self.body.append('</details>\n')

    def visit_summary(self, node):
        self.body.append(self.starttag(node, 'summary', ''))
    
    def depart_summary(self, node):
        self.body.append('</summary>\n')

    def visit_heading(self,node):
        headingLevel = node['level']

        self.body.append(self.starttag(node,'h'+headingLevel,''))

    def depart_heading(self,node):
        self.body.append('</h1>\n')


class reDocs:

    def __init__(self, sourcePath, targetPath):
        self.sourcePath = sourcePath
        self.targetPath = targetPath
        self.html_fragment_writer = Writer()
        self.sections = []
        self.currentDepth = 0
        self.headerHTML = ''
        self.contentsHTML = ''


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

    def rest2html(self,s,contents=False,header=False,path2root=''):
        docExtraHead = ''
        docPreBody = ''
        if contents:
            self.html_fragment_writer.translator_class = ContentsFragmentTranslator
            docExtraHead = indexExtraHead
            docFooter = '</div>\n</body>\n</html>'
        elif header:
            self.html_fragment_writer.translator_class = ContentsFragmentTranslator
            docExtraHead = headerExtraHead
            docFooter = '</div>\n</body>\n</html>'
        else:
            self.html_fragment_writer.translator_class = ContentsFragmentTranslator
            docExtraHead = ''
            for CSSFile in contentCSSList:
                CSSFilePath = join(path2root,CSSFile)
                CSSHTML = '<link rel="stylesheet" href="'+ CSSFilePath+ '" type="text/css" />\n'
                docExtraHead += CSSHTML
            docPreBody = contentFrames
            for frameFile in contentFrameFiles:
                frameFilePath = join(path2root,frameFile)
                docPreBody = docPreBody.replace(frameFile,frameFilePath)
            docFooter = '</div>\n</div>\n</div>\n</body>\n</html>'
        self.sections = []
        tree = publish_doctree(s)
        self.getSections(tree,1)
        htmlparts = core.publish_parts(s,writer=self.html_fragment_writer)

        docHeadPrefix = htmlparts['head_prefix']
        docHead = htmlparts['head']
        docBodyPrefix = htmlparts['body_prefix']
        docBodyPreInfo = htmlparts['body_pre_docinfo']
        docBody = htmlparts["body"]
        docTitle = htmlparts["title"]
        docTitle = docTitle.strip()
        #remove head and body but keep the section - need to add it lower down.
        docBodyPrefix = docBodyPrefix.replace("</head>","")
        docBodyPrefix = docBodyPrefix.replace("<body>","")

        theDoc = docHeadPrefix + docHead + docExtraHead + "</head>\n<body>\n" + docPreBody + docBodyPrefix + docBodyPreInfo + docBody + docFooter

        return docTitle, self.sections, theDoc

    def convertDoc2(self, path, doc):
        htmlTitle = ""
        itemPath = join(path,doc)
        extraPath = ''
        path2root = ''
        if path != self.sourcePath:
            extraPath = relpath(path,self.sourcePath)
            path2root = relpath(self.sourcePath,path)
        with open(itemPath, encoding="utf-8") as restFile:
            restText = restFile.read()
        if restText != None:
            htmlTitle, docSections, htmlText = self.rest2html(restText,False,False,path2root)
        htmlFileName = doc.replace(".rst",".html")
        finalPath = join(self.targetPath,extraPath)
        if not isdir(finalPath):
            makedirs(finalPath)
        htmlFilePath = join(finalPath,htmlFileName)
        with open(htmlFilePath,"w") as htmlFile:
            htmlFile.write(htmlText)

        return htmlTitle, docSections, htmlFileName

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
        with open(htmlFilePath,"w") as htmlFile:
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
        copytree(contentDir,targetContentPath,dirs_exist_ok=True)
        #for contentFile in listdir(contentDir):
        #    contentFilePath = join(contentDir,contentFile)
        #    if isfile(contentFilePath):
        #        copyfile(contentFilePath,join(targetContentPath,contentFile))
        for cssFile in listdir(cssDir):
            cssFilePath = join(cssDir,cssFile)
            if isfile(cssFilePath):
                copyfile(cssFilePath,join(targetCSSPath,cssFile))

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
        if not isdir(self.targetPath):
            makedirs(self.targetPath)
        self.convertDoc(headerFile,header=True)
        self.convertDoc(contentsFile,contents=True)
        for path, subdirs, files in walk(self.sourcePath):
            for name in files:
                if name.endswith(".rst"):
                    if name not in ignoreFiles:
                        print("converting " + join(path, name))
                        htmlTitle, docSections, htmlFileName = self.convertDoc2(path, name)
                    else:
                        continue
                    fileList.append(name)
                    if htmlTitle == "" or htmlTitle in newFileDict:
                        htmlTitle = htmlTitle + " " + str(noTitleCounter)
                        noTitleCounter += 1
                    newFileDict[htmlTitle]=[htmlFileName,docSections]
        if len(newFileDict) != 0:
            self.addSupportFiles()
            contentsFilePath = join(self.sourcePath,contentsFile)
            if not isfile(contentsFilePath):
                print("No contents file detected. One is being generated. Build again to add to project.")
                self.createIndex(newFileDict)

