#!/usr/bin/env python3
"""
This module converts the enrich_transcripts.py script 
to an OOP version for enriching YouTube transcripts with
various LLMs. 
"""
import sys
import os
import json
import argparse
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from google import genai
from google.genai import types

# Load environmental configurations from local workspace files
load_dotenv()

class LLMStrategy(ABC): # pylint: disable=too-few-public-methods
    """
    Abstract base class that implements the LLM Strategy. 
    """
    @abstractmethod
    def enrich(self, video_id: str, raw_text: str) -> dict:
        """Must accept a video identifier and raw transcript text,
        and return a dict containing at minimum 'video_id' and 'cleaned_text'."""

class GeminiStrategy(LLMStrategy): # pylint: disable=too-few-public-methods
    """
    Strategy that enriches transcripts using the Gemini LLM.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")
        self.client = genai.Client(api_key=self.api_key)
        self.response_schema = {
        "title": "Transcript Enrichment Schema",
        "description": "Stores cleaned YouTube transcript text with enriched metadata features.",
        "type": "object",
        "properties": {
            "video_id": {
                "type": "string"
            },
            "cleaned_text": {
                "type": "string"
            },
            "tech_terms": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "book_names": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": ["video_id", "cleaned_text"]
    }

    def enrich(self, video_id: str, raw_text: str) -> dict:
        """
        Enriches the provided raw text using the Gemini LLM.
        """
        prompt = f"""
        You are an elite data engineer. Clean this transcript text for video_id '{video_id}'.
        1. Strip all timestamps and duration codes.
        2. Extract technical architecture terms and books.
        """
        try:
            response = self.client.models.generate_content(
                model = 'gemini-2.5-flash',
                contents = raw_text,
                config = types.GenerateContentConfig(
                    system_instruction = prompt,
                    response_schema = self.response_schema,
                    response_mime_type = "application/json",
                    temperature = 0.1
                )
            )
        except Exception as e:
            raise ValueError(f"Failed processing video {video_id} during LLM generation: {str(e)}") from e

        return json.loads(response.text)

class TranscriptEnricher: # pylint: disable=too-few-public-methods
    """
    Invariant pipeline context that drives an injected LLMStrategy over a
    stream of JSON-encoded transcript records from stdin.
    """
    def __init__(self, strategy: LLMStrategy):
        self.strategy = strategy

    def run_stream(self):
        """
        Runs the data streaming loop. 
        """
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                payload = json.loads(line)
                video_id = payload['video_id']
                raw_text = payload['raw_text']
            except Exception as e:
                sys.stderr.write(f"ERROR parsing input line: {str(e)}\n")
                sys.stderr.flush()
                continue

            try:
                result = self.strategy.enrich(video_id, raw_text)
                sys.stdout.write(json.dumps(result) + "\n")
                sys.stdout.flush()
            except Exception as e:
                sys.stderr.write(f"ERROR processing token [{video_id}]: {str(e)}\n")
                sys.stderr.flush()

def main(argv=None):
    """
    Runtime entrypoint: parses CLI flags, selects an LLMStrategy, and
    drives it through TranscriptEnricher.
    """
    parser = argparse.ArgumentParser(description="Multi-Vendor Transcript Enrichment Node.")
    parser.add_argument(
        "--llm",
        choices=["gemini"], 
        default="gemini",
        help="Target LLM enrichment strategy (Defaults to gemini)."
    )
    args = parser.parse_args(argv)

    if args.llm == "gemini":
        selected_strategy = GeminiStrategy()

    engine = TranscriptEnricher(selected_strategy)
    engine.run_stream()

if __name__ == "__main__":
    main()