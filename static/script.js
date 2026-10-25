"use strict";

// =========================
// 1. Get HTML elements
// =========================

const searchForm = document.getElementById("search-form");
const questionInput = document.getElementById("question");
const searchButton = document.getElementById("search-button");
const buttonLabel = document.getElementById("button-label");

const resultsSection = document.getElementById("results-section");
const resultsContainer = document.getElementById("results");
const messageContainer = document.getElementById("message");

const messageSymbol = document.getElementById("message-symbol");
const messageTitle = document.getElementById("message-title");
const messageDescription = document.getElementById("message-description");
const resultCount = document.getElementById("result-count");

let currentSearch = 0;


// =========================
// 2. Show status messages
// =========================

function showMessage(title, description, type = "info") {
    messageTitle.textContent = title;
    messageDescription.textContent = description;

    messageContainer.classList.remove("error", "loading");
    messageSymbol.textContent = "✦";

    if (type === "error") {
        messageContainer.classList.add("error");
        messageSymbol.textContent = "!";
    }

    if (type === "loading") {
        messageContainer.classList.add("loading");
        messageSymbol.textContent = "↻";
    }

    // Explicitly reveal the message.
    messageContainer.hidden = false;
}


function hideMessage() {
    messageContainer.hidden = true;
    messageContainer.classList.remove("error", "loading");
}


// =========================
// 3. Scroll to results
// =========================

function scrollToResults(target = resultsSection) {
    if (!target) {
        return;
    }

    // Wait until the browser has applied the latest layout.
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            const targetPosition =
                target.getBoundingClientRect().top + window.scrollY - 20;

            window.scrollTo({
                top: Math.max(0, targetPosition),
                behavior: "smooth"
            });
        });
    });
}


// =========================
// 4. Display search results
// =========================

function displayResults(results) {
    resultsContainer.replaceChildren();

    results.forEach((result, index) => {
        const card = document.createElement("article");
        card.className = "result-card";

        // Category and ranking
        const topLine = document.createElement("div");
        topLine.className = "result-topline";

        const category = document.createElement("span");
        category.className = "category-label";
        category.textContent = result.Section || "Banking FAQ";

        const rank = document.createElement("span");
        rank.className = "rank-label";
        rank.textContent = index === 0
            ? "BEST MATCH"
            : `MATCH ${String(index + 1).padStart(2, "0")}`;

        topLine.append(category, rank);

        // FAQ question
        const question = document.createElement("h3");
        question.textContent = result.Question || "Untitled question";

        // FAQ answer
        const answer = document.createElement("p");
        answer.className = "answer";
        answer.textContent = result.Answer || "No answer available.";

        // Similarity score
        const bottomLine = document.createElement("div");
        bottomLine.className = "result-bottom";

        const scoreLabel = document.createElement("span");
        scoreLabel.textContent = "TF-IDF similarity";

        const score = document.createElement("span");
        score.className = "score-value";

        const similarity = Number(result.Similarity_Score);

        score.textContent = Number.isFinite(similarity)
            ? similarity.toFixed(3)
            : "N/A";

        bottomLine.append(scoreLabel, score);

        // Assemble the result card
        card.append(topLine, question, answer, bottomLine);
        resultsContainer.appendChild(card);
    });
}


// =========================
// 5. Handle form submission
// =========================

searchForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const question = questionInput.value.trim();

    if (!question) {
        showMessage(
            "Enter a question",
            "Type a banking question before clicking Search.",
            "error"
        );

        questionInput.focus();
        scrollToResults();
        return;
    }

    // Identify this search so older responses cannot replace newer results.
    const searchId = ++currentSearch;

    // Update the interface immediately.
    searchButton.disabled = true;
    buttonLabel.textContent = "Searching...";

    resultsContainer.replaceChildren();
    resultCount.textContent = "Searching...";

    showMessage(
        "Searching the knowledge base",
        "Finding the closest FAQ matches...",
        "loading"
    );

    // Move the results section into view while the search is running.
    scrollToResults(resultsSection);

    try {
        const queryParameters = new URLSearchParams({
            question: question,
            limit: "5"
        });

        const response = await fetch(
            `/search?${queryParameters.toString()}`,
            {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                },
                cache: "no-store"
            }
        );

        if (!response.ok) {
            throw new Error(`Search request failed (${response.status}).`);
        }

        const data = await response.json();

        // Ignore responses from an older search.
        if (searchId !== currentSearch) {
            return;
        }

        if (!Array.isArray(data.results)) {
            throw new Error("The server returned an unexpected response.");
        }

        if (data.results.length === 0) {
            resultCount.textContent = "No results";

            showMessage(
                "No matching FAQs found",
                "Try asking your question using different words."
            );

            scrollToResults(resultsSection);
            return;
        }

        // Render results before hiding the loading message.
        displayResults(data.results);

        hideMessage();

        const totalResults = Number.isFinite(Number(data.total_results))
            ? Number(data.total_results)
            : data.results.length;

        resultCount.textContent =
            `${totalResults} ${totalResults === 1 ? "result" : "results"}`;

        // Wait for the cards to render, then scroll directly to the first one.
        setTimeout(() => {
            if (searchId !== currentSearch) {
                return;
            }

            const firstResult = resultsContainer.querySelector(".result-card");

            if (firstResult) {
                scrollToResults(firstResult);
            }
        }, 100);

    } catch (error) {
        if (searchId !== currentSearch) {
            return;
        }

        console.error("SmartDocs search error:", error);

        resultCount.textContent = "Search unavailable";

        showMessage(
            "We couldn't complete your search",
            "Check that the SmartDocs server is running, then try again.",
            "error"
        );

        scrollToResults(resultsSection);

    } finally {
        // Only the latest search should control the button.
        if (searchId === currentSearch) {
            searchButton.disabled = false;
            buttonLabel.textContent = "Search";
        }
    }
});