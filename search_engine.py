import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Load the banking FAQ dataset
dataset = pd.read_csv("banking_knowledge_base_1000.csv")

# Combine each question and answer into searchable text
dataset["Searchable_Text"] = (
    "Question: " + dataset["Question"].str.strip()
    + " Answer: " + dataset["Answer"].str.strip()
)

# Create a TF-IDF representation of every FAQ
tfidf_vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english"
)

document_vectors = tfidf_vectorizer.fit_transform(
    dataset["Searchable_Text"]
)



def search_banking_faqs(user_question, number_of_results=5):
    """Return the most relevant banking FAQs for a question."""

    search_question = user_question
    question_lower = user_question.lower()

    # Improve searches about personal-loan documents
    if (
        "personal loan" in question_lower
        and any(word in question_lower for word in ["document", "paper", "proof"])
    ):
        search_question += " required documents identity proof address proof"

    # Improve searches about lost or stolen debit cards
    if (
        "debit card" in question_lower
        and any(word in question_lower for word in ["lose", "lost", "missing", "stolen"])
    ):
        search_question += " block my debit card card block request"

    question_vector = tfidf_vectorizer.transform([search_question])

    similarity_scores = cosine_similarity(
        question_vector, document_vectors
    ).flatten()

    ranked_positions = similarity_scores.argsort()[::-1]
    top_positions = ranked_positions[:number_of_results]

    results = dataset.iloc[top_positions][
        ["Section", "Question", "Answer"]
    ].copy()

    results["Similarity_Score"] = similarity_scores[top_positions]

    return results.reset_index(drop=True)
