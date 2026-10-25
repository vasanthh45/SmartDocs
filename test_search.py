from search_engine import search_banking_faqs


def check_top_result(question, expected_text):
    results = search_banking_faqs(question, number_of_results=5)

    assert not results.empty, f"No results for: {question}"

    top_question = results.iloc[0]["Question"]

    assert expected_text.lower() in top_question.lower(), (
        f"Question: {question}\n"
        f"Expected text: {expected_text}\n"
        f"Actual top result: {top_question}"
    )

    print(f"PASS: {question}")
    print(f"Top result: {top_question}\n")


if __name__ == "__main__":
    check_top_result(
        "What documents do I need to apply for a personal loan?",
        "personal loan"
    )

    check_top_result(
        "How can I reset my net banking password?",
        "reset my net banking password"
    )

    results = search_banking_faqs(
        "What should I do if I lose my debit card?",
        number_of_results=5
    )

    assert any(
        "block my debit card" in question.lower()
        for question in results["Question"].head(3)
    ), "Relevant debit-card blocking FAQ was not found in the top 3."

    print("PASS: Debit-card blocking FAQ found in the top 3.")
    print("Top result:", results.iloc[0]["Question"])
    print()

    print("All 3 search tests passed.")