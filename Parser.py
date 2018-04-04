# coding=utf-8
import io
import requests
from Porter import Porter
from pymystem3 import Mystem
from Entities import *
import re
from lxml import etree, html

def getXMLTreeByLink(link):
    page = requests.get(link)
    page.encoding = 'windows-1251'

    parser = html.HTMLParser()
    tree = html.parse(io.StringIO(page.text), parser)

    return tree

def getPorterText(text):
    text_porter = ''
    for word in text.split(' '):
        word1 = word.strip()
        word1 = re.sub(u'[^a-zA-Zа-яА-ЯйЙёЁ_]+', '', word1)
        if (re.match(Porter.RVRE, word1)):
            word1 = Porter.stem(word1)
            # print word1
            text_porter = text_porter + " " + Porter.stem(word1)
    return text_porter

def get_stem_text(text):
    m = Mystem()
    text_raw = re.sub(u'[^a-zA-Zа-яА-ЯйЙёЁ _]+', '', text)
    text_stem = m.lemmatize(text_raw)
    text_res = ''.join(text_stem).strip()
    return text_res


if (__name__) == "__main__":
    link = 'http://www.mathnet.ru/php/archive.phtml?jrnid=uzku&wshow=issue&bshow=contents&series=0&year=2008&volume=150&issue=3&option_lang=rus&bookID=1000'
    parser = html.HTMLParser()
    root_tree = getXMLTreeByLink(link)

    root = etree.Element('Math-Net')
    year = etree.SubElement(root, 'year')
    year.text = root_tree.xpath("// td[@width='70%'] / span[@class='red'] / font")[0].text_content().strip().split(' ')[0].replace(',', '')
    articles = etree.SubElement(root, 'articles')


    expresstion_article = "// td[@colspan='2'] / a[contains(@class, 'SLink')]".decode('utf-8')
    index = 0
    for element in root_tree.xpath(expresstion_article):
        article = etree.SubElement(articles, 'article')
        article.set("id", str(index))
        index += 1
        article_link = etree.SubElement(article, 'link')
        article_link.text = 'http://www.mathnet.ru%s' % element.attrib['href']
        article_title = etree.SubElement(article, 'title')
        article_title.text = element.text_content()

        article_title_porter = etree.SubElement(article, 'title-porter')
        title_raw = element.text_content()
        article_title_porter.text = getPorterText(title_raw)

        article_title_stem = etree.SubElement(article, 'title-mystem')
        article_title_stem.text = get_stem_text(title_raw)

        article_tree = getXMLTreeByLink(article_link.text)

        expression_annotation = "// b[contains(.,'Аннотация:')] / following-sibling::node()[following-sibling::br[count(// b[contains(.,'Аннотация:')] / following-sibling::br)]]".decode('utf-8')
        article_annotation = etree.SubElement(article, 'abstract')
        try:
            article_annotation.text =  article_tree.xpath(expression_annotation)[0]
        except IndexError:
            article_annotation.text = 'null'

        #porter
        article_porter = etree.SubElement(article, 'abstract-porter')
        try:
            text_raw = article_tree.xpath(expression_annotation)[0]
            article_porter.text =  getPorterText(text_raw)
        except IndexError:
            article_porter.text = 'null'

        #mystem
        article_stem = etree.SubElement(article, 'abstract-mystem')
        try:
            text_raw = article_tree.xpath(expression_annotation)[0]
            article_stem.text =  get_stem_text(text_raw)
        except IndexError:
            article_stem.text = 'null'

        expression_keywords = "// b[contains(.,'Ключевые слова:')] / following-sibling::i".decode('utf-8')
        article_keywords = etree.SubElement(article, 'keywords')

        try:
            keywords = article_tree.xpath(expression_keywords)[0].text_content().split(" ")
            for keyword_value in keywords:
                keyword_value = re.sub(u'[^a-zA-Zа-яА-ЯйЙёЁ]+', '', keyword_value)
                article_keyword = etree.SubElement(article_keywords, 'keyword')
                article_keyword.text = get_stem_text(keyword_value)
        except IndexError:
            pass


    output = open("result.xml", "w")
    output.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
    output.close()
    # print (etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))


