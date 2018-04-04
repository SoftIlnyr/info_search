# coding=utf-8


from lxml import etree, html

from Entities import *
from Parser import *

def get_words(filename):
    tree = etree.parse(filename)
    root = tree.getroot()

    word_dict = {}

    for word_tag in root.iter("word"):
        word_val = word_tag.attrib["value"]
        word = Word(word_val)
        doc_article = word_tag.find("documents_article")
        doc_title = word_tag.find("documents_title")
        for doc in doc_article.findall("document"):
            word.documents_article.append(int(doc.attrib["id"]))
        for doc in doc_title.findall("document"):
            word.documents_title.append(int(doc.attrib["id"]))
        word_dict[word_val] = word

    return word_dict

def get_documents_by_search(query, word_dict):
    doc_set = set()
    stemmed_words = []

    for word in query.split(" "):
        if (len(word.strip()) == 0):
            continue
        s_word = get_stem_text(word)
        word_obj = word_dict.get(s_word)
        if (word_obj == None):
            continue
        print(word_obj.value)
        if "-" in word:
            doc_set.difference_update(word_dict[s_word].documents_article)
            doc_set.difference_update(word_dict[s_word].documents_title)
        else:
            stemmed_words.append(s_word)
            doc_set.update(word_dict[s_word].documents_article)
            doc_set.update(word_dict[s_word].documents_title)

    doc_set = set(map(lambda x: int(x), doc_set))

    return doc_set, stemmed_words

if __name__ == '__main__':
    word_dict = get_words("word_info_mystem.xml")

    query = "алгоритмы анализа -данных"#.decode("utf8")

    doc_set = get_documents_by_search(query, word_dict)
    print(doc_set)

    output = open("search_result.txt", "a", encoding="utf8")
    output.write(query)
    output.write(str(doc_set))
    output.write("\n")
    output.close()

    # print query
    #