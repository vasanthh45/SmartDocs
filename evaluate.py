
import pandas as pd
from search_engine import search_banking_faqs

# Load the evaluation queries
evaluation_data = pd.read_csv("evaluation_queries.csv")

required_columns = {"query", "expected_question"}

if not required_columns.issubset(evaluation_data.columns):
    raise ValueError(
        "evaluation_queries.csv must contain "
        "'query' and 'expected_question' columns."
    )

if evaluation_data.empty:
    raise ValueError("The evaluation dataset is empty.")

top1_correct = 0
reciprocal_ranks = []
recall_at_5_correct = 0
failures = []

for _, row in evaluation_data.iterrows():
    query = str(row["query"]).strip()
    expected_question = str(row["expected_question"]).strip()

    results = search_banking_faqs(query, number_of_results=5)

    # Compare questions without differences in capitalization
    # or leading/trailing spaces.
    ranked_questions = [
        str(question).strip().casefold()
        for question in results["Question"].tolist()
    ]

    expected = expected_question.casefold()

    if ranked_questions and ranked_questions[0] == expected:
        top1_correct += 1
    else:
        top_question = (
            results.iloc[0]["Question"] if not results.empty
            else "No result"
        )

        failures.append({
            "query": query,
            "expected": expected_question,
            "actual_top_result": top_question,
        })

    if expected in ranked_questions:
        rank = ranked_questions.index(expected) + 1
        reciprocal_ranks.append(1 / rank)
        recall_at_5_correct += 1
    else:
        reciprocal_ranks.append(0)

total = len(evaluation_data)

top1_accuracy = top1_correct / total
recall_at_5 = recall_at_5_correct / total
mrr = sum(reciprocal_ranks) / total

print("\n===== TF-IDF SEARCH EVALUATION =====")
print(f"Total queries: {total}")
print(f"Top-1 Accuracy: {top1_accuracy:.2%}")
print(f"Recall@5: {recall_at_5:.2%}")
print(f"MRR: {mrr:.4f}")

print(f"\nTop-1 correct: {top1_correct}/{total}")
print(f"Correct FAQ found in top 5: {recall_at_5_correct}/{total}")
print(f"Top-1 failures: {len(failures)}")

if failures:
    print("\n===== TOP-1 FAILURES =====")

    for number, failure in enumerate(failures, start=1):
        print(f"\n{number}. Query: {failure['query']}")
        print(f"   Expected: {failure['expected']}")
        print(f"   Actual:   {failure['actual_top_result']}")
else:
    print("\nNo Top-1 failures.")
