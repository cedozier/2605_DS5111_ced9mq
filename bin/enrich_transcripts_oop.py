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

class LLMStrategy(ABC):
    """
    Abstract base class that implements the LLM Strategy. 
    """
    @abstractmethod
    def enrich(self, video_id: str, raw_text: str) -> dict:
        """Must accept a video identifier and raw transcript text,
        and return a dict containing at minimum 'video_id' and 'cleaned_text'."""
        pass
