import pytest
import time
from unittest.mock import patch
from app.nlp.transformer_sentiment import analyze_sentiment_transformer
from tests.evaluation.test_retrieval_quality import mock_retrieval_service

@pytest.mark.evaluation
def test_component_latency(mock_retrieval_service):
    """
    Reproduces Table IX: Pipeline Component Latency Breakdown.
    Measures the latency of each component.
    """
    # Number of iterations to get a stable average
    iterations = 50
    test_query = "I am very angry about my order delay!"
    
    # 1. Sentiment Analysis Latency
    sentiment_latencies = []
    for _ in range(iterations):
        start = time.perf_counter()
        _ = analyze_sentiment_transformer(test_query)
        end = time.perf_counter()
        sentiment_latencies.append((end - start) * 1000) # Convert to ms
        
    avg_sentiment_latency = sum(sentiment_latencies) / len(sentiment_latencies)
    
    # 2. Vector Retrieval Latency
    retrieval_latencies = []
    for _ in range(iterations):
        start = time.perf_counter()
        _ = mock_retrieval_service.retrieve(client_id="test", query=test_query, top_k=5)
        end = time.perf_counter()
        retrieval_latencies.append((end - start) * 1000)
        
    avg_retrieval_latency = sum(retrieval_latencies) / len(retrieval_latencies)
    
    print("\n--- Table IX Reproduction: Component Latency Breakdown ---")
    print(f"{'Component':<25} | {'Latency (ms)':<15}")
    print("-" * 45)
    print(f"{'Sentiment Analysis':<25} | {avg_sentiment_latency:.2f} ms")
    print(f"{'Vector Retrieval':<25} | {avg_retrieval_latency:.2f} ms")
    
    # In a real environment, we'd also measure Intent Classification and LLM Generation.
    
    # Assertions based on paper claims (e.g. End-to-end latency < 200ms)
    total_pipeline_simulated = avg_sentiment_latency + avg_retrieval_latency + 50.0 # simulated LLM overhead
    assert total_pipeline_simulated < 200.0, f"Total pipeline latency ({total_pipeline_simulated:.2f}ms) exceeds the 200ms real-time threshold."
