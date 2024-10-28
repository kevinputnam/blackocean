from docutils import nodes, utils
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
from docutils.parsers import rst
from docutils.nodes import paragraph, container, Inline, Element
from os.path import join, dirname

class details(Inline,container):

    pass

class summary(Inline,paragraph):

    pass

class heading(Inline,paragraph):

    pass

class Heading(rst.Directive):

    required_arguments = 1
    optional_arguments = 0
    has_content = False
    final_argument_whitespace = True
    option_spec = {'level' : int}

    def run(self):
        theNode = heading()
        if 'level' not in self.options:
            headingLevel = 1
        else:
            headingLevel = self.options['level']
        if headingLevel in range(1,4):
            headingLevel = str(headingLevel)
        else:
            headingLevel = "4"
        theNode['level'] = headingLevel
        theNode['classes'].append('arbitrary')
        print(self.arguments)
        newNode = nodes.Text(self.arguments[0])
        theNode.append(newNode)
        self.state.nested_parse(self.content,self.content_offset,theNode)
        return[theNode]

class Details(rst.Directive):

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'title': directives.unchanged,
                   'link': directives.uri}
    has_content = True

    def run(self):
        theNode = details(rawsource=self.content)
        if 'title' not in self.options:
            self.options['title'] = "Need to add title"
        parentNode = summary()
        if 'link' in self.options:
            refNode = nodes.reference(text=self.options['title'])
            refNode["name"]=self.options['title']
            refNode["refuri"] = self.options['link']
            targetNode = nodes.target()
            targetNode["refuri"] = self.options['link']
            targetNode["ids"].append(nodes.make_id(self.options['title']))
            targetNode["names"].append(nodes.fully_normalize_name(self.options['title']))
            parentNode.insert(0,targetNode)
            parentNode.insert(0,refNode)
        else:
            titleNode = nodes.paragraph(text=self.options['title'])
            parentNode.insert(0,titleNode)
        self.state.nested_parse(self.content,self.content_offset,theNode)
        theNode.insert(0,parentNode)
        return [theNode]

class ContentCard(rst.Directive):

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        path = directives.path(self.arguments[0])
        theNode = nodes.container()
        theNode['classes'].append("contentcard")
        restText = ''
        with open(path, encoding="utf-8") as restFile:
            restText = restFile.read()
        document = utils.new_document(path, self.state.document.settings)
        parser = rst.Parser()
        parser.parse(restText,document)
        try:
            docTitle = next(iter(document.traverse(nodes.title)))
        except:
            docTitle = nodes.title()
            docTitleText = nodes.Text("No Title")
            docTitle.append(docTitleText)
        try:
            docImage = next(iter(document.traverse(nodes.image)))
            imgPath = docImage['uri']
            docRelPath = dirname(path)
            imgRelPath = join(docRelPath,imgPath)
            docImage['uri'] = imgRelPath
        except:
            docImage = nodes.image()
            docImage['uri']="null"
            docImage['alt'] = "No Image Available"
        try:
            docSummary = next(iter(document.traverse(nodes.paragraph)))
        except:
            docSummary = nodes.paragraph()
            docText = nodes.Text("No summary.")
            docSummary.append(docText)
        docSummary['classes'].append("summary")
        cardTitle = nodes.paragraph()
        cardTitle['classes'].append("title")
        cardLink = nodes.reference()
        cardLink['refuri']=path.split('.')[0]+'.html'
        for item in docTitle:
            cardLink.append(item)
        cardTitle.append(cardLink)
        # Image attributes are reset by css
        docImage.delattr('width')
        docImage.delattr('height')
        docImage['align'] = 'left'
        docImage['classes'].append('thumbnail')
        imageRef = nodes.reference()
        imageRef['refuri'] = path.split('.')[0]+'.html'
        imageRef.append(docImage)
        theNode.append(imageRef)
        theNode.append(cardTitle)
        theNode.append(docSummary)
        return [theNode]
