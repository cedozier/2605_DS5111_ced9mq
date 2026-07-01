# 2605_DS5111_ced9mq
GitHub respository for DS 5111 work (Summer 2026)

## Project Core Objective

This repository implements a three-stage data pipeline that ingests YouTube video IDs and produces cleaned, enriched transcript data suitable for downstream analysis. The pipeline stages are:

1. **`bin/clean_ids.py`** — Validates raw YouTube video IDs against the standard 11-character modified Base64 format, filtering out malformed entries.
2. **`bin/extract_transcripts.py`** — Fetches raw transcript text for each valid video ID using the YouTube Transcript API, routed through Webshare residential proxy credentials to avoid cloud-provider IP throttling/blocking.
3. **`bin/enrich_transcripts.py`** — Sends raw transcript text to the Google Gemini API (`gemini-2.5-flash`) to strip timestamps, clean the text, and extract structured metadata (technical terms, book references).

Data flows as newline-delimited JSON (JSON Lines) between stages via stdin/stdout piping, and pipeline execution is logged to `pipeline/logs/pipeline_audit.log` for auditing and debugging.

## New VM Set up

Pre-Set up Requirements: 
* User has launched an established AWS EC2 instance
* User has created and set up an SSH key to enable login to GitHub with credentials

VM Set up Steps:  
1. Clone the GitHub repository to the VM with `git clone git@github.com:cedozier/2605_DS5111_ced9mq.git`  
2. cd into the GitHub repository `2605_DS5111_ced9mq` from the root  
3. cd into `scripts`  
4. Run `bash init.sh` to make sure the VM is update-to-date and has the required programs/tools installed (make/python/tree)
5. Run `bash init_git_creds.sh` to configure GitHub credentials (when run it will echo email/username -- email and user need to be changed for different individual)  
6. cd back to the root of the repository  
7. Run `make update` to execute the `makefile` that creates the virtual environment for Python and loads the required packages (calls the `requirements.txt` file present in the repo)  
8. Test success by running `. env/bin/activate` to confirm the new virtual environment can be activated (this activates it) and `pip list` to ensure required packages are present  

## Environment Configuration

The pipeline reads credentials and configuration from a `.env` file at the repository root (loaded via `python-dotenv`). This file is git-ignored and must be created manually on each new VM — it is **not** included in version control.

| Variable | Required? | Used By | Purpose | Failure Behavior if Missing |
|---|---|---|---|---|
| `GEMINI_API_KEY` | **Required** | `bin/enrich_transcripts.py` | Authenticates requests to the Google Gemini API for transcript enrichment | Script logs a critical error and exits immediately (`sys.exit(1)`) before processing any input |
| `WEBSHARE_USER` | Recommended | `bin/extract_transcripts.py` | Username for Webshare residential proxy, used to route transcript-fetch requests and avoid YouTube blocking cloud datacenter IPs | If absent (with `WEBSHARE_PASSWORD`), falls back to direct local IP routing — transcript fetches are likely to fail or be rate-limited from an EC2 IP |
| `WEBSHARE_PASSWORD` | Recommended | `bin/extract_transcripts.py` | Password paired with `WEBSHARE_USER` for proxy authentication | Same fallback behavior as `WEBSHARE_USER` above |

**To set up `.env` on a new VM:**
```bash
touch .env
```
Then add the following lines, replacing placeholder values with real credentials:
```
WEBSHARE_USER=your-webshare-username-here
WEBSHARE_PASSWORD=your-webshare-password-here
GEMINI_API_KEY=your-gemini-api-key-here
```

## Verification Steps

After completing VM setup and configuring `.env`, verify the environment is correctly configured before running the pipeline:

```bash
# Confirm the virtual environment builds and dependencies install cleanly
make update

# Run the linter across all source directories (bin/, lib/, tests/)
make lint

# Run the full automated test suite
make test

# Run both lint and test together (fails fast on lint errors before testing)
make check
```

All four commands should complete with exit code `0` and no unsuppressed errors. If `make lint` or `make test` fails, do not proceed to running the pipeline (`make run`) until the failure is resolved — failing tests or lint errors indicate the environment is not correctly configured for production use.

To verify the live pipeline end-to-end (requires valid `.env` credentials):
```bash
make run
```


