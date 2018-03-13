# coding=utf-8
import re
from pymystem3 import Mystem

word = "Hello,"

word1 = re.sub(r'\W+', '', word)

print word
print word1

text = "Красивая (мама) красиво мыла раму"
text = text.strip()
text = re.sub(u'[^a-zA-Zа-яА-ЯйЙёЁ _]+', '', text)
m = Mystem()
lemmas = m.lemmatize(text)
print(''.join(lemmas))
