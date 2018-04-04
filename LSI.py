from string import punctuation

from pymystem3 import Mystem

import numpy as np

from Parser import get_stem_text
from TF_IDF import get_documents, get_words


def build_matrix(documents, words, tf_idf=False):
    matrix = np.zeros((len(words), len(documents)), dtype=int)
    for i, word in enumerate(words):
        for j, doc in documents.items():
            matrix[i, j] = doc.abstract.count(word)
    # если используем tf_idf
    if tf_idf:
        docs_count = len(documents)
        model = np.zeros((len(words), len(documents)), dtype=float)
        for i, word in enumerate(words):
            for j, doc in enumerate(documents):
                tf = matrix[i, j] / len(doc)
                if matrix[i, j] != 0:
                    idf = np.log(docs_count / sum(matrix[i] > 0))
                else:
                    idf = 0
                model[i, j] = tf * idf
    return matrix


# нормализуем запрос
def prepare_query(words, query):
    word_list = set()
    for i, word in enumerate(words):
        word_list.add(word)
    word_list = sorted(word_list)
    result = np.zeros(len(word_list))
    query_list = get_stem_text(query)
    i = 0
    for word in sorted(query_list.split(" ")):
        while word > word_list[i]:
            i += 1
        if word == word_list[i]:
            result[i] += 1
    return result


# сингулярно разлогаем и выделяем нужное колисетво столбцов
def svd_with_approximation(matrix, k):
    u, s, v = np.linalg.svd(matrix)
    s = np.diag(s)
    return u[:, :k], s[:k, :k], v[:k, :]


# вычисляем косинусную меру для двух векторов ( запроса и документа)
def similarity(x, y):
    return (x @ y) / (np.linalg.norm(x) * np.linalg.norm(y))


def calc_lsi(documents, words, k, matrix, query):
    pr_query = prepare_query(words, query)
    u_k, s_k, v_k = svd_with_approximation(matrix, k)
    query_coordinates = pr_query.T @ u_k @ np.linalg.pinv(s_k)  # вычисляем q = q_T * u_k * s_k ^-1
    doc_coordinates = matrix.T @ u_k @ np.linalg.pinv(s_k)  # вычисляем A = A_T * u_k * s_k ^-1

    # берем срез вектора вдоль главной оси и вычисляем косинусную меру
    # для каждого документа считаем его косинусную меру
    result = np.apply_along_axis(lambda row: similarity(query_coordinates, row), axis=1, arr=doc_coordinates)
    ranking = np.argsort(-result)
    return ranking


if __name__ == "__main__":
    # берем документы
    documents = get_documents("result.xml")
    # берем слова
    words = get_words("word_info_mystem.xml")
    # строим матрицу
    matrix = build_matrix(documents, words)

    result_file = open("result_lsi.txt", "w", encoding="utf8")

    query = "он показывает поле"
    k = 5

    result_list = calc_lsi(documents, words, k, matrix, query)
    print(result_list)
    result_file.write(query)
    result_file.write(str(result_list))
    result_file.write("\n")


    query = "возможность геометрических данных"
    result_list = calc_lsi(documents, words, k, matrix, query)
    print(result_list)
    result_file.write(query)
    result_file.write(str(result_list))
    result_file.write("\n")


    result_file.close()
