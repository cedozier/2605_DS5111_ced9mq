"""
Tests the extract_transcripts.py script.
"""
import sys
import io
import json
from youtube_transcript_api import YouTubeTranscriptApi

# Import the executable main entry point loop from your pipeline package directory
from bin.extract_transcripts import main

class MockTranscriptContainer: # pylint: disable=too-few-public-methods
    """
    Mimics the 2026 .to_raw_data() array output return schema
    """
    def to_raw_data(self):
        """
        Return canned transcript segment data, mimicking the real API's shape.
        """
        return [
            {"start": 10.5, "text": "Automated container tracking loop text entry."}
        ]

def test_extract_transcripts_main_pipeline_stream(monkeypatch, capsys):
    """
    Verifies that the main() entrypoint loop correctly processes video IDs via stdin
    and outputs structured JSON Lines objects via stdout without hitting the internet.
    Serves as starting test.
    """
    # 1. Mock the external third-party API fetch dependency
    def stubbed_fetch_route(self, video_id):  # pylint: disable=unused-argument
        return MockTranscriptContainer()
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", stubbed_fetch_route)

    # 2. Mock Standard Input (sys.stdin) to feed a fake video ID into your script
    mock_input_stream = io.StringIO("fake_video_999\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    # 3. Trigger your script's main entry point execution loop directly
    main()

    # 4. Intercept the standard console terminal print buffers using capsys
    captured_output = capsys.readouterr()

    # Clean up trailing whitespace and isolate rows
    stdout_lines = captured_output.out.strip().split("\n")

    # 5. Execute structural validations against the emitted JSON Lines payload contract
    assert len(stdout_lines) == 1, "The pipeline loop should emit exactly one row per valid input ID."

    parsed_json_line = json.loads(stdout_lines[0])

    assert parsed_json_line["video_id"] == "fake_video_999"
    assert "Automated container tracking" in parsed_json_line["raw_text"]

def test_extract_transcripts_main_multiple_ids(monkeypatch, capsys):
    """
    Verifies that the main() loop correctly processes multiple video IDs
    and emits one JSON line per valid input ID.
    """
    def stubbed_fetch_route(self, video_id):  # pylint: disable=unused-argument
        return MockTranscriptContainer()
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", stubbed_fetch_route)

    # Feed two video IDs via stdin
    mock_input_stream = io.StringIO("fake_video_001\nfake_video_002\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    # Trigger script's main entry point
    main()

    captured_output = capsys.readouterr()
    stdout_lines = captured_output.out.strip().split("\n")

    assert len(stdout_lines) == 2, "Pipeline should emit one row per valid input ID."

    first = json.loads(stdout_lines[0])
    second = json.loads(stdout_lines[1])

    assert first["video_id"] == "fake_video_001"
    assert second["video_id"] == "fake_video_002"

def test_extract_transcripts_main_handles_fetch_error(monkeypatch, capsys):
    """
    Verifies that the main() loop catches exceptions gracefully and emits
    nothing to stdout when a video ID fails to fetch.
    """
    # Mock fetch to raise an exception (simulates invalid/blocked video ID)
    def stubbed_fetch_error(self, video_id):
        raise Exception("Video unavailable or invalid ID") # pylint: disable=broad-exception-raised
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", stubbed_fetch_error)

    # Feed a fake bad video ID via stdin
    mock_input_stream = io.StringIO("bad_video_id_000\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    # Trigger script's main entry point
    main()

    captured_output = capsys.readouterr()

    # Nothing should be emitted to stdout on failure (exception should be caught)
    assert captured_output.out.strip() == "", "Failed IDs should produce no stdout output."
