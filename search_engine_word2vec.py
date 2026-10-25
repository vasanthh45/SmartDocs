import re
import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity

# Load the banking FAQ dataset
dataset = pd.read_csv("banking_knowledge_base_1000.csv")

# Combine each question and answer into searchable text
dataset["Searchable_Text"] = (
    "Question: " + dataset["Question"].str.strip()
    + " Answer: " + dataset["Answer"].str.strip()
)

# Convert text into lowercase word lists
def tokenize_document(text):
    return re.findall(r"\b\w+\b", text.lower())

tokenized_documents = [
    tokenize_document(text)
    for text in dataset["Searchable_Text"]
]

# Train the Word2Vec model
word2vec_model = Word2Vec(
    sentences=tokenized_documents,
    vector_size=100,
    window=5,
    min_count=1,
    workers=4,
    seed=42,
    epochs=30
)

# Convert each document into an average word vector
def create_document_vector(words):
    known_vectors = [
        word2vec_model.wv[word]
        for word in words
        if word in word2vec_model.wv
    ]

    if not known_vectors:
        return np.zeros(word2vec_model.vector_size)

    return np.mean(known_vectors, axis=0)

document_vectors = np.array([
    create_document_vector(words)
    for words in tokenized_documents
])

# Search the FAQ dataset using Word2Vec
def search_banking_faqs_word2vec(user_question, number_of_results=5):
    question_words = tokenize_document(user_question)
    question_vector = create_document_vector(question_words)

    similarity_scores = cosine_similarity(
        question_vector.reshape(1, -1),
        document_vectors
    ).flatten()

    ranked_positions = similarity_scores.argsort()[::-1]
    top_positions = ranked_positions[:number_of_results]

    results = dataset.iloc[top_positions][
        ["Section", "Question", "Answer"]
    ].copy()

    results["Similarity_Score"] = similarity_scores[top_positions]

    return results.reset_index(drop=True)