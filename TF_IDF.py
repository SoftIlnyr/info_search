# coding=utf-8
import io

import math
import requests
from Porter import Porter
from pymystem3 import Mystem
from Entities import *
import re
from lxml import etree, html
import operator

from Search_Mystem import *


def get_keywords(filename):
    keyword_set = set()
    tree = etree.parse(filename)
    root = tree.getroot()
    for article in root.iter("article"):
        keyword_set.update(keyword.text for keyword in article.find("keywords").findall("keyword"))
    return keyword_set


def get_documents(filename):
    tree = etree.parse(filename)
    root = tree.getroot()

    doc_dict = {}

    for doc_tag in root.iter("article"):
        doc = Document()
        doc.id = int(doc_tag.attrib["id"])
        doc.abstract = doc_tag.find("abstract-mystem").text
        doc.title = doc_tag.find("title-mystem").text
        doc_dict[doc.id] = doc

    return doc_dict


def get_doc_score(query):
    # достаем список слов

    word_dict = get_words("word_info_mystem.xml")
    doc_dict = get_documents("result.xml")

    doc_list, stemmed_words = get_documents_by_search(query, word_dict)

    result_doc_dict = {}

    for doc_id in doc_list:
        doc_obj = doc_dict[doc_id]

        doc_obj.tfidf_abstract = 0
        doc_obj.tfidf_title = 0
        doc_obj.tfidf_total = 0
        doc_obj.tfidf_full = 0

        result_doc_dict[doc_id] = doc_obj

    for word in stemmed_words:
        word_obj = word_dict.get(word)

        if (word_obj is None):
            continue

        # находим idf
        print(doc_list.intersection(word_obj.documents_article))
        if (len(doc_list.intersection(word_obj.documents_article)) > 0):
            idf_abstract = math.log(len(doc_list) / len(doc_list.intersection(word_obj.documents_article)))
        else:
            idf_abstract = 0

        print(doc_list.intersection(word_obj.documents_title))
        if (len(doc_list.intersection(word_obj.documents_title)) > 0):
            idf_title = math.log(len(doc_list) / len(doc_list.intersection(word_obj.documents_title)))
        else:
            idf_title = 0

        total_word_docs = set(word_obj.documents_article).intersection(doc_list)
        total_word_docs.update(doc_list.intersection(word_obj.documents_title))

        idf_full = math.log(len(doc_list) / len(total_word_docs))

        for doc_id_2 in total_word_docs:
            doc_obj = result_doc_dict[doc_id_2]
            article_abstract_text = doc_dict[doc_id_2].abstract
            article_title_text = doc_dict[doc_id_2].title

            tf_title = float(article_title_text.count(word)) / len(article_title_text.split(" "))
            doc_obj.tfidf_title += tf_title * idf_title

            tf_abstract = float(article_abstract_text.count(word)) / len(article_abstract_text.split(" "))
            doc_obj.tfidf_abstract += tf_abstract * idf_abstract

            article_full_text = article_title_text + " " + article_abstract_text

            tf_full = float(article_full_text.count(word)) / len(article_full_text.split(" "))
            doc_obj.tfidf_full += tf_full * idf_full

            # находим total tfidf
            doc_obj.tfidf_total += 0.4 * doc_obj.tfidf_abstract + 0.6 * doc_obj.tfidf_title

    #сортировка
    result = {}
    for doc in sorted(result_doc_dict.values(), key=operator.attrgetter("tfidf_full"), reverse=True):
        result[doc.id] = doc

    return result

if __name__ == "__main__":
    tf_scores = {}


    query = "алгоритмы анализа больших вертикальных"
    tf_scores[query] = get_doc_score(query)

    query = "возможность геометрических данных"
    tf_scores[query] = get_doc_score(query)

    query = "он показывает поле"
    tf_scores[query] = get_doc_score(query)

    root = etree.Element("TF_IDF")

    queries_tag = etree.SubElement(root, "queries")

    for q in tf_scores.keys():
        query_tag = etree.SubElement(queries_tag, "query")
        query_tag.set("value", q)
        documents_tag = etree.SubElement(query_tag, "documents")
        for doc_obj in tf_scores.get(q).values():
            document_tag = etree.SubElement(documents_tag, "document")
            document_tag.set("id", str(doc_obj.id))

            tfidf_full = etree.SubElement(document_tag, "tf_idf")
            tfidf_full.text = str(doc_obj.tfidf_full)

            tfidf_abstract = etree.SubElement(document_tag, "tf_idf_abstract")
            tfidf_abstract.text = str(doc_obj.tfidf_abstract)

            tfidf_title = etree.SubElement(document_tag, "tfidf_title")
            tfidf_title.text = str(doc_obj.tfidf_title)

            tfidf_total = etree.SubElement(document_tag, "tf_idf_full")
            tfidf_total.text = str(doc_obj.tfidf_total)

    output = open("tf_idf_queries.xml", "wb")
    output.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
    output.close()

    # для каждого ключевого слова находим tf, idf, tf-idf по abstract, по title и общий
