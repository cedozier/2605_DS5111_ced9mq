#!/usr/bin/env python3
"""
This module uses the Gemini LLM to clean and enrich the 
text of raw YouTube transcripts. 
"""
import sys
import os
import json
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environmental configurations from local workspace files
load_dotenv()

# Audit logging framework tracking pipeline telemetry
logging.basicConfig(
    filename='pipeline/logs/pipeline_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """
    Runs Step 2B (Gemini Enrichment) to clean raw YouTube transcript text 
    and add helpful metadata features (technical terms and books). 
    """
    logging.info("Pipeline Step 2B (Gemini Enrichment) started.")

    # -------------------------------------------------------------------------
    # Step 2B-1: API Environment Validation and Client Initialization
    # Extract the necessary credential key token from the local environment.
    # If the token is missing, log a critical failure and terminate the system.
    # Otherwise, instantiate the official Google GenAI Client utility.
    # -------------------------------------------------------------------------
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.critical("GEMINI_API_KEY environment variable is not configured.")
        sys.exit(1)
    client = genai.Client(api_key=api_key)

    # -------------------------------------------------------------------------
    # Step 2B-2: Structured Output Response Schema Definition
    # To prevent the LLM from returning unpredictable formats that would crash
    # downstream applications, define a strict "Data Contract" using a JSON
    # Schema layout.
    #
    # Enforce a response type of "OBJECT" that guarantees the presence of:
    #   - video_id: (STRING, Required)
    #   - cleaned_text: (STRING, Required)
    #   - tech_terms: (ARRAY of STRINGS)
    #   - book_names: (ARRAY of STRINGS)
    # -------------------------------------------------------------------------
    response_schema = {
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

    # Stream processing framework reading line-by-line text inputs from stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        # ---------------------------------------------------------------------
        # Step 2B-3: Inbound String Stream Deserialization
        # Safely wrap your stream ingestion inside an isolated try-except block.
        # Parse the raw line string object into a key-value dictionary and
        # extract the target 'video_id' and 'raw_text' properties.
        # Log any malformed line tracks and continue processing the stream.
        # ---------------------------------------------------------------------
        try:
            # EXTRACT PAYLOAD DETAILS HERE
            payload = json.loads(line)
            video_id = payload['video_id']
            raw_text = payload['raw_text']
        except Exception as e:
            logging.error(f"Failed to parse incoming JSON payload row: {str(e)}")
            continue

        logging.info(f"Orchestrating Gemini enrichment for video: {video_id}")

        prompt = f"""
        You are an elite data engineer. Clean this transcript text for video_id '{video_id}'.
        1. Strip all timestamps and duration codes.
        2. Extract technical architecture terms and books.
        """

        # ---------------------------------------------------------------------
        # Step 2B-4: Structured Model Invocation and Instant Stream Flushing
        # Call the 'gemini-2.5-flash' model via the unified SDK interface.
        # Inject the constructed prompt along with the raw text sequence payload.
        # Map the configuration block to use the structured JSON mime-type
        # and enforce your defined response schema parameters.
        # Write the resulting text explicitly to sys.stdout and flush immediately.
        # ---------------------------------------------------------------------
        try:
            response = client.models.generate_content(
                model = 'gemini-2.5-flash',
                contents = raw_text,
                config = types.GenerateContentConfig(
                    system_instruction = prompt,
                    response_schema = response_schema,
                    response_mime_type = "application/json",
                    temperature = 0.1
                )
            )
            result = json.loads(response.text)
            sys.stdout.write(json.dumps(result) + "\n")
            sys.stdout.flush()
        except Exception as e:
            logging.error(f"Failed processing video {video_id} during LLM generation: {str(e)}")

    logging.info("Pipeline Step 2B finished.")

if __name__ == '__main__':
    main()
