# coding=utf-8

class Document:
    title = ''
    id = 0
    dict = {}
    count = 0

    def __init__(self, title):
        self.title = title
        self.id = self.count
        Document.count += 1


class Word:
    def __init__(self, value):
        self.value = value
        self.count = 0
        self.documents_article = []
        self.documents_title = []

    def __hash__(self):
        return self.value