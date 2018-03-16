# coding=utf-8

from lxml import etree, html

class Document:
    title = ''
    id = 0
    dict = {}

class Word:
    def __init__(self, value):
        self.value = value
        self.count = 0
        self.documents = []


if (__name__ == "__main__"):
    tree = etree.parse("result.xml")

    root = tree.getroot()

    i = 0

    documents = []
    full_dict = {}

    for article in root.iter("article"):
        i += 1
        doc = Document()
        doc.id = i
        doc.title = article.find("title").text.strip()
        doc_text = article.find("abstract-porter").text
        for word in doc_text.split(" "):
            word = word.strip()
            if (len(word) > 0):
                if (not doc.dict.has_key(word)):
                    doc.dict[word] = 0
                    if (not full_dict.has_key(word)):
                        word_obj = Word(word)
                        word_obj.documents.append(doc.id)
                        full_dict[word] = word_obj
                if (not doc.id in full_dict[word].documents):
                    full_dict[word].documents.append(doc.id)
                doc.dict[word] += 1
                full_dict[word].count += 1

        documents.append(doc)

    doc_m = documents[0]

    root = etree.Element('Math-Net')


    # for document in documents:
    #     doc = etree.SubElement(root, 'document')
    #     doc.set("id", str(document.id))
    #     doc.set("title", document.title)
    #     for w in sorted(document.dict):
    #         word = etree.SubElement(doc, 'word')
    #         word.set('value', w)
    #         word.set('count', str(document.dict[w]))
    #         word_docs = etree.SubElement(word, 'documents')
    #         for d in full_dict[w]:
    #             word_doc = etree.SubElement(word_docs, 'document')
    #             word_doc.set('id', str(d))

    for w in sorted(full_dict):
        word = etree.SubElement(root, 'word')
        word.set('value', w)
        word.set('total_count', str(full_dict[w].count))
        word.set('doc_count', str(len(full_dict[w].documents)))
        word_docs = etree.SubElement(word, 'documents')
        for d in full_dict[w].documents:
            word_doc = etree.SubElement(word_docs, 'document')
            word_doc.set('id', str(d))

    output = open("word_info_porter.xml", "w")
    output.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
    output.close()



