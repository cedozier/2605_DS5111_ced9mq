#!/usr/bin/env python3
"""
This module converts the enrich_transcripts.py script 
to an OOP version for enriching YouTube transcripts with
various LLMs. 
"""
import sys
import os
import json
import logging
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from google import genai
from google.genai import types

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
