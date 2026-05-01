#!python3
from __future__ import division
import math
import os
import platform
from tkinter import *
from tkinter import messagebox
import string

print('Python version ', platform.python_version())

# PREPROCESS FUNCTION 
def preprocess(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.split()

#  GUI SETUP 
root = Tk()
root.title("Vector Space Model")
root.geometry("800x400")

Label(root, text="VECTOR SPACE MODEL CALCULATOR",
      fg="blue",
      font=("Franklin Gothic Book", 20)).pack(pady=10)

Label(root, text="Enter Query",
      font=("Franklin Gothic Book", 16)).pack()

# MAIN FUNCTION 
def fetch():
    query = e.get().strip()

    if not query:
        messagebox.showinfo("Error", "Please enter a query")
        return

    # CHECK FOLDER 
    if not os.path.exists("documents"):
        messagebox.showinfo("Error", "documents folder not found")
        return

    # LOAD DOCUMENTS 
    documents = []
    file_names = []

    for file in sorted(os.listdir("documents")):
        if file.endswith(".txt"):
            path = os.path.join("documents", file)
            with open(path, "r", encoding="utf-8") as f:
                documents.append(f.read())
                file_names.append(file)

    if len(documents) < 5:
        messagebox.showinfo("Error", "Minimum 5 documents required")
        return

    # PREPROCESS 
    docs_tokens = [preprocess(doc) for doc in documents]
    query_tokens = preprocess(query)

    # VOCABULARY 
    all_words = list(set(word for doc in docs_tokens for word in doc))
    N = len(documents)

    # TF 
    tf_docs = []
    for doc in docs_tokens:
        tf = {}
        for word in all_words:
            tf[word] = doc.count(word)
        tf_docs.append(tf)

    tf_query = {word: query_tokens.count(word) for word in all_words}

    # DF 
    df = {}
    for word in all_words:
        df[word] = sum(1 for tf in tf_docs if tf[word] > 0)

    # IDF 
    idf = {}
    for word in all_words:
        idf[word] = math.log10(N / (df[word] + 1))

    # TF-IDF 
    tfidf_docs = []
    for tf in tf_docs:
        tfidf = {}
        for word in all_words:
            tfidf[word] = tf[word] * idf[word]
        tfidf_docs.append(tfidf)

    tfidf_query = {}
    for word in all_words:
        tfidf_query[word] = tf_query[word] * idf[word]

    # COSINE SIMILARITY 
    def euclidean_length(vec):
        return math.sqrt(sum(v**2 for v in vec.values()))

    query_len = euclidean_length(tfidf_query)

    if query_len == 0:
        messagebox.showinfo("Result", "No matching terms found")
        return

    scores = []

    for i, doc_vec in enumerate(tfidf_docs):
        dot = sum(doc_vec[w] * tfidf_query[w] for w in all_words)
        doc_len = euclidean_length(doc_vec)

        if doc_len == 0:
            score = 0
        else:
            score = dot / (doc_len * query_len)

        scores.append((file_names[i], score))

    # SORT 
    scores.sort(key=lambda x: x[1], reverse=True)

    # DISPLAY RESULTS
    result = ""
    for name, score in scores:
        result += f"{name} : score = {round(score, 4)}\n"

    messagebox.showinfo("Ranking Results", result)

    e.delete(0, END)

# INPUT FIELD 
e = Entry(root, width=40)
e.pack(pady=10, ipady=5)
e.focus()

e.bind('<Return>', lambda event: fetch())

Button(root, text='Search', command=fetch).pack()

root.mainloop()