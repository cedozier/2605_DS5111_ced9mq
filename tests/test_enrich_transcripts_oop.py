"""
Tests the TranscriptEnricher orchestrator using a dummy LLMStrategy.
"""
import sys
import io
import json
from bin.enrich_transcripts_oop import LLMStrategy, TranscriptEnricher

class MockLLMStrategy(LLMStrategy): # pylint: disable=too-few-public-methods
    """A fake strategy satisfying the LLMStrategy contract for isolated testing."""
    def enrich(self, video_id: str, raw_text: str) -> dict:
        return {
            "video_id": video_id,
            "cleaned_text": raw_text.upper(),
            "tech_terms": ["dummy_term"],
            "book_names": []
        }


def test_enricher_processes_single_line(capsys):
    """
    Verifies TranscriptEnricher reads a JSONL line from stdin, delegates to
    the injected strategy, and writes the resulting dict to stdout as JSON.
    """
    mock_input_row = {
        "video_id": "vid001",
        "raw_text": "hello world"
    }
    mock_stdin = io.StringIO(json.dumps(mock_input_row) + "\n")
    sys.stdin = mock_stdin

    engine = TranscriptEnricher(strategy=MockLLMStrategy())
    engine.run_stream()

    captured = capsys.readouterr()
    stdout_lines = captured.out.strip().split("\n")

    assert len(stdout_lines) == 1
    parsed_output = json.loads(stdout_lines[0])
    assert parsed_output["video_id"] == "vid001"
    assert parsed_output["cleaned_text"] == "HELLO WORLD"
