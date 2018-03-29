# coding=utf-8


from lxml import etree, html

from Entities import *
from Parser import *



if __name__ == '__main__':

    tree = etree.parse("word_info_mystem.xml")
    root = tree.getroot()

    word_dict = {}

    for word_tag in root.iter("word"):
        word_val = word_tag.attrib["value"]
        word = Word(word_val)
        doc_article = word_tag.find("documents_article")
        doc_title = word_tag.find("documents_title")
        for doc in doc_article.findall("document"):
            word.documents_article.append(doc.attrib["id"])
        for doc in doc_title.findall("document"):
            word.documents_title.append(doc.attrib["id"])
        word_dict[word_val] = word



    # query = raw_input("enter your request: ").decode("utf8")
    query = "алгоритмы анализа данных -без -потери атомной -бомбы".decode("utf8")

    doc_set = set()

    for word in query.split(" "):
        if (len(word.strip()) == 0):
            continue
        s_word = getStemText(word)
        word_obj = word_dict.get(s_word)
        if (word_obj == None):
            continue
        print word_obj.value
        if "-" in word:
            doc_set.difference_update(word_dict[s_word].documents_article)
            doc_set.difference_update(word_dict[s_word].documents_title)
        else:
            doc_set.update(word_dict[s_word].documents_article)
            doc_set.update(word_dict[s_word].documents_title)

    print doc_set

    # print query
    #