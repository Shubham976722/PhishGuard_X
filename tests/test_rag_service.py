import json
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import requests

from backend.app.services.rag_service import (
    MIN_SIMILARITY,
    answer_question,
    answer_scan_question,
    chunk_text,
    filter_relevant_documents,
    format_sources,
    insufficient_information_response,
    load_index,
    retrieve_documents,
)


# ==================================================
# CHUNK_TEXT TESTS
# ==================================================

def test_chunk_text_empty_and_whitespace():
    assert chunk_text("") == []
    assert chunk_text("   \n\t  ") == []


def test_chunk_text_invalid_parameters():
    with pytest.raises(ValueError, match="chunk_size must be greater than zero"):
        chunk_text("Sample text", chunk_size=0)

    with pytest.raises(ValueError, match="overlap must be between zero"):
        chunk_text("Sample text", chunk_size=100, overlap=-1)

    with pytest.raises(ValueError, match="overlap must be between zero"):
        chunk_text("Sample text", chunk_size=100, overlap=100)


def test_chunk_text_splits_and_preserves_overlap():
    words = ["word" + str(i) for i in range(100)]
    text = " ".join(words)

    chunks = chunk_text(text, chunk_size=100, overlap=30)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 100
        assert chunk.strip() != ""


# ==================================================
# FILTER & FORMAT SOURCES TESTS
# ==================================================

def test_filter_relevant_documents():
    retrieved = [
        {"source": "doc1.md", "similarity": 0.75},
        {"source": "doc2.md", "similarity": 0.59},
        {"source": "doc3.md", "similarity": 0.60},
        {"source": "doc4.md", "similarity": 0.40},
    ]

    filtered = filter_relevant_documents(retrieved)

    assert len(filtered) == 2
    assert [d["source"] for d in filtered] == ["doc1.md", "doc3.md"]


def test_format_sources_deduplicates():
    retrieved = [
        {"source": "doc1.md", "title": "Doc One", "source_urls": ["http://a.com"], "similarity": 0.85234},
        {"source": "doc1.md", "title": "Doc One", "source_urls": ["http://a.com"], "similarity": 0.75111},
        {"source": "doc2.md", "title": "Doc Two", "source_urls": [], "similarity": 0.62189},
    ]

    sources = format_sources(retrieved)

    assert len(sources) == 2
    assert sources[0]["source"] == "doc1.md"
    assert sources[0]["similarity"] == 0.8523
    assert sources[1]["source"] == "doc2.md"
    assert sources[1]["similarity"] == 0.6219


def test_insufficient_information_response():
    resp = insufficient_information_response("What is quantum phishing?")

    assert resp["question"] == "What is quantum phishing?"
    assert "don't have enough relevant information" in resp["answer"]
    assert resp["sources"] == []


# ==================================================
# LOAD_INDEX & RETRIEVAL TESTS
# ==================================================

def test_load_index_missing_file(tmp_path, monkeypatch):
    non_existent = tmp_path / "missing_index.json"
    monkeypatch.setattr("backend.app.services.rag_service.INDEX_PATH", non_existent)

    with pytest.raises(FileNotFoundError, match="RAG index not found"):
        load_index()


def test_load_index_empty_file(tmp_path, monkeypatch):
    empty_index = tmp_path / "empty_index.json"
    empty_index.write_text("[]", encoding="utf-8")
    monkeypatch.setattr("backend.app.services.rag_service.INDEX_PATH", empty_index)

    with pytest.raises(ValueError, match="RAG index is empty"):
        load_index()


@pytest.mark.parametrize("invalid_top_k", [0, -1, True, False])
def test_retrieve_documents_invalid_top_k(invalid_top_k):
    with pytest.raises(ValueError, match="top_k must be a positive integer"):
        retrieve_documents("What is phishing?", top_k=invalid_top_k)


def test_retrieve_documents_dimension_mismatch(monkeypatch):
    fake_records = [
        {"source": "test.md", "title": "Test", "text": "Content", "embedding": [0.1, 0.2]}
    ]
    monkeypatch.setattr("backend.app.services.rag_service.load_index", lambda: fake_records)
    monkeypatch.setattr(
        "backend.app.services.rag_service.get_embedding",
        lambda text: [0.1, 0.2, 0.3],  # 3 dimensions vs 2 dimensions
    )

    with pytest.raises(ValueError, match="Embedding dimensions do not match"):
        retrieve_documents("Test question", top_k=1)


def test_retrieve_documents_cosine_scoring(monkeypatch):
    # Vector 1 is identical to query -> similarity ~ 1.0
    # Vector 2 is orthogonal -> similarity ~ 0.0
    fake_records = [
        {"source": "doc_ortho.md", "title": "Ortho", "source_urls": [], "text": "Orthogonal chunk", "embedding": [0.0, 1.0]},
        {"source": "doc_match.md", "title": "Match", "source_urls": [], "text": "Matching chunk", "embedding": [1.0, 0.0]},
    ]
    monkeypatch.setattr("backend.app.services.rag_service.load_index", lambda: fake_records)
    monkeypatch.setattr(
        "backend.app.services.rag_service.get_embedding",
        lambda text: [1.0, 0.0],
    )

    results = retrieve_documents("Test question", top_k=2)

    assert len(results) == 2
    assert results[0]["source"] == "doc_match.md"
    assert pytest.approx(results[0]["similarity"], 0.001) == 1.0
    assert results[1]["source"] == "doc_ortho.md"
    assert pytest.approx(results[1]["similarity"], 0.001) == 0.0


# ==================================================
# ANSWER_QUESTION TESTS
# ==================================================

def test_answer_question_empty_raises():
    with pytest.raises(ValueError, match="Question cannot be empty"):
        answer_question("")

    with pytest.raises(ValueError, match="Question cannot be empty"):
        answer_question("   ")


@patch("backend.app.services.rag_service.retrieve_documents")
def test_answer_question_low_similarity_fallback(mock_retrieve):
    mock_retrieve.return_value = [
        {"source": "doc.md", "similarity": 0.45, "text": "Low score text"}
    ]

    result = answer_question("Unrelated question about cooking")

    assert "don't have enough relevant information" in result["answer"]
    assert result["sources"] == []


@patch("backend.app.services.rag_service.requests.post")
@patch("backend.app.services.rag_service.retrieve_documents")
def test_answer_question_ollama_timeout(mock_retrieve, mock_post):
    mock_retrieve.return_value = [
        {"source": "doc.md", "title": "Doc", "similarity": 0.85, "text": "Relevant phishing text", "source_urls": []}
    ]
    mock_post.side_effect = requests.Timeout("Connection timed out")

    with pytest.raises(RuntimeError, match="Ollama generation request timed out"):
        answer_question("How do I report a phishing attack?")


@patch("backend.app.services.rag_service.requests.post")
@patch("backend.app.services.rag_service.retrieve_documents")
def test_answer_question_ollama_offline(mock_retrieve, mock_post):
    mock_retrieve.return_value = [
        {"source": "doc.md", "title": "Doc", "similarity": 0.85, "text": "Relevant phishing text", "source_urls": []}
    ]
    mock_post.side_effect = requests.ConnectionError("Failed to establish connection")

    with pytest.raises(RuntimeError, match="Ollama generation service is unavailable"):
        answer_question("How do I report a phishing attack?")


@patch("backend.app.services.rag_service.requests.post")
@patch("backend.app.services.rag_service.retrieve_documents")
def test_answer_question_success(mock_retrieve, mock_post):
    mock_retrieve.return_value = [
        {"source": "phishing_basics.md", "title": "Phishing Basics", "similarity": 0.88, "text": "Phishing basics content", "source_urls": ["http://example.com/guide"]}
    ]

    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"response": "Phishing is an attempt to steal sensitive data."}
    mock_post.return_value = mock_resp

    result = answer_question("What is phishing?", top_k=1)

    assert result["question"] == "What is phishing?"
    assert result["answer"] == "Phishing is an attempt to steal sensitive data."
    assert len(result["sources"]) == 1
    assert result["sources"][0]["source"] == "phishing_basics.md"
    assert result["sources"][0]["similarity"] == 0.88


# ==================================================
# ANSWER_SCAN_QUESTION TESTS
# ==================================================

@patch("backend.app.services.ml_service.explain_url")
def test_answer_scan_question_deterministic(mock_explain):
    mock_explain.return_value = {
        "top_factors": [
            {"feature": "count_dots", "value": 3, "contribution": 0.4215},
            {"feature": "has_https", "value": 1, "contribution": -0.8123},
            {"feature": "count_at", "value": 0, "contribution": 0.0},
        ]
    }

    mock_scan = MagicMock()
    mock_scan.url = "https://suspicious-bank-login.com"
    mock_scan.verdict = "phishing"
    mock_scan.risk_score = 88.5
    mock_scan.risk_level = "high"

    result = answer_scan_question("Why was this marked high risk?", mock_scan)

    assert result["question"] == "Why was this marked high risk?"
    answer = result["answer"]

    # Verify structured Python-assembled scan facts
    assert "SCAN SUMMARY" in answer
    assert "Verdict: phishing" in answer
    assert "Risk score: 88.5" in answer
    assert "Number of dots: value = 3, contribution = +0.4215, direction = increases the model's phishing prediction" in answer
    assert "HTTPS usage: value = 1, contribution = -0.8123, direction = decreases the model's phishing prediction" in answer
    assert "SAFETY ADVICE" in answer
    assert "INTERPRETATION" in answer
    assert result["sources"] == []


def test_answer_scan_question_empty_raises():
    mock_scan = MagicMock()
    with pytest.raises(ValueError, match="Question cannot be empty"):
        answer_scan_question("", mock_scan)
