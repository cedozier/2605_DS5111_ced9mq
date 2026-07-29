# File location: bin/load_snowflake.py
"""
Module that connects to Snowflake and loads enriched transcript data
into database.
"""
import sys
import os
import json
import logging
import snowflake.connector
from dotenv import load_dotenv  # <-- Added to support standard .env loading

# Establish clean centralized diagnostic logging metrics output footprint
logging.basicConfig(
    filename='pipeline/logs/pipeline_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """
    Executes the following sequence:
    1. Connects to Snowflake.
    2. Performs semi-structured polymorphic schema verification.
    3. Executes safe parameterized insertion into the database. 
    4. Closes the Snowflake connection.
    """
    # Initialize the environment variables from the local .env file
    load_dotenv()  # <-- Added to ensure os.getenv() does not return None

    logging.info("Pipeline Step 3 (Snowflake Loader Node) initialized.")

    # -------------------------------------------------------------------------
    # Environment Handshake & Connection Isolation Engine
    # Securely retrieve database context variables from the shell environment.
    # If key credentials (USER/PASSWORD) are missing, log a critical alert and crash out.
    # Open your connection context engine using the native connector framework.
    # -------------------------------------------------------------------------
    sf_user = os.getenv('SF_USER')
    sf_password = os.getenv('SF_PASSWORD')

    if not sf_user or not sf_password:
        logging.critical("Missing critical Snowflake runtime credential bindings. Ingestion aborted.")
        sys.exit(1)

    try:
        # Pass the pre-extracted user/password variables along with remaining context configs
        ctx = snowflake.connector.connect(
            user=sf_user,
            password=sf_password,
            account=os.getenv('SF_ACCOUNT'),
            warehouse=os.getenv('SF_WAREHOUSE'),
            database=os.getenv('SF_DATABASE'),
            schema=os.getenv('SF_SCHEMA'),
            role=os.getenv('SF_ROLE')
        )
        cs = ctx.cursor()
    except Exception as e:
        logging.critical(f"Snowflake Authorization Context Handshake Failed: {str(e)}")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # Semi-Structured Polymorphic Schema Verification (DDL)
    # Execute a DDL statement to guarantee the target landing table exists.
    # The table configuration MUST feature an active 'VARIANT' type data column
    # to hold the raw unstructured polymorphic incoming document strings efficiently,
    # alongside a default transactional generation record ingestion timestamp.
    # -------------------------------------------------------------------------
    try:
        cs.execute("""
            CREATE TABLE IF NOT EXISTS RAW_TRANSCRIPTS (
                json_payload VARIANT, 
                inserted_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
        """)
        cs.execute("TRUNCATE TABLE RAW_TRANSCRIPTS") # prevents duplicating when rerunning pipeline
    except Exception as e:
        logging.error(f"Failed to execute target structural validation DDL: {str(e)}")
        cs.close()
        ctx.close()
        sys.exit(1)

    # -------------------------------------------------------------------------
    # Safe Streaming Consumer Insertion Invariant
    # Process inputs infinitely line-by-line via sys.stdin streaming.
    # For every line:
    #   1. Clean trailing whitespace. Skip blank lines.
    #   2. Run structural sanity checks by deserializing the string to a dict.
    #   3. Build a parameterized injection-proof insertion template query.
    #   4. Convert the dict back into a serialized string literal and pass it
    #      safely inside a positional execution parameter tuple using PARSE_JSON(%s).
    # -------------------------------------------------------------------------
    for line in sys.stdin:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue

        try:
            # Safely validate structural correctness before invoking remote storage
            json_data = json.loads(cleaned_line)

            # Execute safe parameterized insertion. json.dumps() handles turning the
            # validated python dictionary cleanly back into a serialized string payload.

            query = "INSERT INTO RAW_TRANSCRIPTS (json_payload) SELECT PARSE_JSON(%s)"
            cs.execute(query, (json.dumps(json_data), ))

            # Left intact from your original template design:
            logging.info(f"Loaded entry token item target: [{json_data.get('video_id', 'UNKNOWN')}] safely to warehouse.")
        except Exception as e:
            logging.error(f"Skipping corrupt pipeline payload stream element: {str(e)}")

    # -------------------------------------------------------------------------
    # Defensive Resource Reclamation Lifecycle
    # Ensure that resource cursors and connection pools are definitively closed
    # out down to the operating system runtime container layout.
    # -------------------------------------------------------------------------
    cs.close()
    ctx.close()
    logging.info("Pipeline Step 3 finished execution cycles cleanly.")

if __name__ == '__main__':
    main()
