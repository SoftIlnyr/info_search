# coding=utf-8

from lxml import etree, html

from Entities import *


if (__name__ == "__main__"):
    tree = etree.parse("result.xml")

    root = tree.getroot()


    documents = []
    full_dict = {}

    for article in root.iter("article"):
        doc = Document(article.find("title").text.strip())
        doc_text = article.find("abstract-mystem").text
        for word in doc_text.split(" "):
            word = word.strip()
            if (len(word) > 0):
                if (not doc.dict.has_key(word)):
                    doc.dict[word] = 0
                    if (not full_dict.has_key(word)):
                        word_obj = Word(word)
                        word_obj.documents_article.append(doc)
                        full_dict[word] = word_obj
                if (not doc in full_dict[word].documents_article):
                    full_dict[word].documents_article.append(doc)
                doc.dict[word] += 1
                full_dict[word].count += 1

        doc_title = article.find("title-mystem").text
        for word in doc_title.split(" "):
            word = word.strip()
            if (len(word) > 0):
                if (not doc.dict.has_key(word)):
                    doc.dict[word] = 0
                    if (not full_dict.has_key(word)):
                        word_obj = Word(word)
                        word_obj.documents_title.append(doc)
                        full_dict[word] = word_obj
                if (not doc in full_dict[word].documents_title):
                    full_dict[word].documents_title.append(doc)
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
        word.set('doc_article_count', str(len(full_dict[w].documents_article)))
        word.set('doc_title_count', str(len(full_dict[w].documents_title)))
        word_docs = etree.SubElement(word, 'documents_article')
        for d in full_dict[w].documents_article:
            word_doc = etree.SubElement(word_docs, 'document')
            word_doc.set('id', str(d.id))
            word_doc.set('title', d.title)
        word_docs = etree.SubElement(word, 'documents_title')
        for d in full_dict[w].documents_title:
            word_doc = etree.SubElement(word_docs, 'document')
            word_doc.set('id', str(d.id))
            word_doc.set('title', d.title)

    output = open("word_info_mystem.xml", "w")
    output.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
    output.close()



