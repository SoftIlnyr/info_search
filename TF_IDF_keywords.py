# coding=utf-8
import io

import math
import requests
from Porter import Porter
from pymystem3 import Mystem
from Entities import *
import re
from lxml import etree, html

def get_keywords(filename):
    keyword_set = set()
    tree = etree.parse(filename)
    root = tree.getroot()
    for article in root.iter("article"):
        keyword_set.update(keyword.text for keyword in article.find("keywords").findall("keyword"))
    return keyword_set



if __name__ == "__main__":
    #достаем список слов
    tree = etree.parse("word_info_mystem.xml")
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

    #достаем ключевые слова
    tree_article = etree.parse("result.xml")
    root_article = tree_article.getroot()
    articles = []
    for article in root_article.iter("article"):
        articles.append(article)


    keyword_set = get_keywords("result.xml")



    for word in keyword_set:
        print(word)

        word_obj = word_dict.get(word)

        if (word_obj is None):
            continue

        #находим idf
        if (len(word_obj.documents_article) > 0):
            idf_abstract = math.log(len(articles) / len(word_obj.documents_article))
        else:
            idf_abstract = 0

        if (len(word_obj.documents_title) > 0):
            idf_title = math.log(len(articles) / len(word_obj.documents_title))
        else:
            idf_title = 0

        total_word_docs = set(word_obj.documents_article)
        total_word_docs.update(word_obj.documents_title)

        idf_full = math.log(len(articles) / len(total_word_docs))

        for doc_id in total_word_docs:
            article_abstract_text = articles[doc_id].find("abstract-mystem").text
            article_title_text = articles[doc_id].find("title-mystem").text

            #находим tf и tfidf
            print(article_title_text.count(word))
            print(float(len(article_title_text.split(" "))))

            tf_title =  float(article_title_text.count(word)) / len(article_title_text.split(" "))
            word_obj.tfidf_title = tf_title * idf_title

            tf_abstract = float(article_abstract_text.count(word)) / len(article_abstract_text.split(" "))
            word_obj.tfidf_abstract = tf_abstract * idf_abstract

            article_full_text = article_title_text + " " + article_abstract_text

            tf_full = float(article_full_text.count(word)) / len(article_full_text.split(" "))
            word_obj.tfidf_full = tf_full

            #находим total tfidf
            word_obj.tfidf_total = 0.4 * word_obj.tfidf_abstract + 0.6 * word_obj.tfidf_title

    #выводим результат
    root_tf = etree.Element('TF_IDF')

    for word in keyword_set:
        word_obj = word_dict.get(word)

        if (word_obj is None):
            continue

        word_tag = etree.SubElement(root_tf, "word")
        word_tag.set("value", word)

        documents_tag = etree.SubElement(word_tag, "documents")

        total_word_docs = set(word_obj.documents_article)
        total_word_docs.update(word_obj.documents_title)

        for doc_id in total_word_docs:
            doc_tag = etree.SubElement(documents_tag, "document")

            tfidf_full = etree.SubElement(doc_tag, "tf_idf")
            tfidf_full.text = str(word_obj.tfidf_full)

            tfidf_abstract = etree.SubElement(doc_tag, "tf_idf_abstract")
            tfidf_abstract.text = str(word_obj.tfidf_abstract)

            tfidf_title = etree.SubElement(doc_tag, "tfidf_title")
            tfidf_title.text = str(word_obj.tfidf_title)

            tfidf_total = etree.SubElement(doc_tag, "tf_idf_full")
            tfidf_total.text = str(word_obj.tfidf_total)


    output = open("tf_idf_result.xml", "w")
    output.write(etree.tostring(root_tf, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
    output.close()




    #для каждого ключевого слова находим tf, idf, tf-idf по abstract, по title и общий


