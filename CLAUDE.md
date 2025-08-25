# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-LLM query testing project that provides a unified interface to test and compare responses from multiple Large Language Model providers (OpenAI, Anthropic, Perplexity, Google Gemini) and Google Web Search.

The project includes three main scripts:
- **query.py**: Original testing script for querying multiple LLMs
- **run.py**: Enhanced version with multiple query modes and AI-powered response analysis for AISEO insights
- **analyzer.py**: Response analysis module that uses GPT-4 to extract structured insights

## Key Commands

### Running Tests
```bash
# Basic multi-LLM testing
python3 query.py

# Interactive mode with AI analysis
python3 run.py

# Single query via command line
python3 run.py --query "Your question here"
python3 run.py -q "Your question here"

# Batch processing all questions
python3 run.py --batch
python3 run.py -b

# Select from question list
python3 run.py --select
python3 run.py -s

# Use custom questions file
python3 run.py --batch --file my_questions.txt
```

### Installing Dependencies
```bash
# Install all dependencies
pip3 install -r requirements.txt

# Or install manually (with minimum versions)
pip3 install "openai>=1.0.0" "anthropic>=0.64.0" "python-dotenv>=1.0.0" "requests>=2.31.0" "google-genai>=1.0.0"
```

## Architecture

### Core Components

1. **query.py** - Basic testing framework that:
   - Validates environment setup and dependencies
   - Checks API key configuration from `.env` file
   - Tests each configured LLM provider sequentially
   - Generates timestamped JSON result files
   - Provides detailed debugging output

2. **run.py** - Enhanced testing with multiple modes:
   - All features of query.py PLUS
   - Multiple query modes (interactive, command-line, batch, select)
   - Organized results in `results/` directory with descriptive filenames
   - Batch summaries for multi-query runs
   - AI-powered response analysis using GPT-4 (when enabled)
   - Extracts companies, authority signals, and key features
   - Provides AISEO optimization insights
   - Saves analysis to CSV for pattern tracking

3. **analyzer.py** - Response analysis module:
   - Uses OpenAI API to analyze LLM responses
   - Extracts structured insights for AISEO optimization
   - Handles JSON parsing and error recovery
   - Saves results to CSV for historical tracking
   - Analyzes only LLM responses (not Google Search results)

### Configuration

API keys are managed through a `.env` file with the following structure:
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic Claude API key  
- `PERPLEXITY_API_KEY` - Perplexity API key
- `GOOGLE_API_KEY` - Google Gemini API key
- `GOOGLE_SEARCH_API_KEY` - Google Custom Search API key
- `GOOGLE_SEARCH_CX` - Google Custom Search Engine ID

Model configurations:
- `OPENAI_MODEL` (default: gpt-4.1)
- `ANTHROPIC_MODEL` (default: claude-sonnet-4-20250514)
- `PERPLEXITY_MODEL` (default: llama-3.1-sonar-small-128k-online)
- `GOOGLE_MODEL` (default: gemini-2.5-flash)

Settings:
- `MAX_TOKENS` (default: 4000) - Maximum tokens for LLM responses
- `TEMPERATURE` (default: 0.7) - Sampling temperature
- `REQUEST_TIMEOUT` (default: 30) - Request timeout in seconds

Provider toggles:
- `ENABLE_OPENAI` (default: true)
- `ENABLE_ANTHROPIC` (default: true)
- `ENABLE_PERPLEXITY` (default: false)
- `ENABLE_GOOGLE` (default: true)

AI Analysis Settings (run.py only):
- `ANALYZE_RESPONSES` (default: true) - Enable AI-powered analysis
- `ANALYSIS_MODEL` (default: gpt-4.1) - Model for analysis (uses OpenAI API)
- `ANALYSIS_CSV_PATH` (default: analysis_results.csv) - CSV output path

### Testing Flow

The `FixedLLMTester` class orchestrates testing:
1. Validates provider configuration and library availability
2. Sends test prompts to each configured provider
3. Handles API-specific request formats and error handling
4. Collects and formats responses (full text for LLMs, top 10 results for web search)
5. Saves results to JSON files (timestamped in root for query.py, organized in results/ for run.py)

### Output Structure

**JSON Results**:
- query.py: `llm_test_results_YYYYMMDD_HHMMSS.json` (in root directory)
- run.py: `results/llm_results_[question_slug]_[timestamp].json`
- Batch summary: `results/batch_summary_[timestamp].json`

JSON contains:
- Query text and timestamp
- Provider name and model info
- Response text (full response up to MAX_TOKENS)
- For Google Search: array of results with title, link, snippet
- Error details if failed
- Analysis data (run.py with ANALYZE_RESPONSES=true)

**CSV Analysis** (`analysis_results.csv` - run.py only):
- Timestamp, query, and provider
- Companies/brands mentioned with reasons
- Authority signals and key features
- Sources cited and ranking factors
- Sentiment analysis
- AISEO optimization insights

### Key Features

1. **No Response Truncation**: Uses MAX_TOKENS environment variable (default 4000) instead of hardcoded limits
2. **Google Web Search**: Queries Google Custom Search API and returns top 10 results
3. **Version Detection**: Automatically detects and handles different library versions (OpenAI v0.x vs v1.x, google.genai vs google.generativeai)
4. **Environment Override**: Uses `load_dotenv(override=True)` to prioritize .env values
5. **Multiple Query Modes** (run.py): Interactive, command-line, batch, and select modes
6. **AI Response Analysis** (run.py): Analyzes LLM responses for AISEO insights
   - NOTE: Only analyzes LLM-generated responses, not Google Search results
   - Extracts companies, authority signals, and optimization insights
   - Saves to CSV for pattern tracking

### Questions File

The project includes a `questions.txt` file with standard financial advisor questions:
- One question per line format
- Used by `--batch` and `--select` modes in run.py
- Can be overridden with custom file using `--file` parameter