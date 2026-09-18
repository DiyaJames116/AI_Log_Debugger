# AI Log Debugger

AI Log Debugger turns large application logs into a grounded incident report using a model running entirely on your computer. **Your logs stay on your machine:** no telemetry, no cloud logging, no API keys, and no hosted AI API.

## Why?

An incident log is noisy, repetitive, and often too large to inspect manually. The pipeline streams it, extracts significant events, clusters duplicates, ranks likely incident signals, redacts sensitive values, and gives only compact evidence to a local Ollama model.

## Features

- Streaming `.log`, `.txt`, `.json`, and `.jsonl` ingestion, including recursive directories
- Timestamp/level/HTTP/request-ID extraction with graceful degradation
- Error clustering, chronological timeline, importance ranking, bounded context retrieval
- Configurable secret redaction before local model context is constructed
- Ollama provider abstraction, structured analysis, and a second verification pass
- Markdown, JSON, and standalone HTML reports; no Ollama needed for `--offline` evidence reports

## Architecture

```text
LOG FILES → streaming ingestion → parser → significant events → clustering/ranking
       → redaction → bounded context retrieval → local Ollama analysis → verifier → report
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
ollama pull qwen3:8b
ai-debug setup
```

## Ollama setup and models

Install Ollama from its official installer, start its local service, then pull a model. Set `AI_DEBUG_MODEL` or use `--model`. Suggested sizes: 3B–4B for small machines (~4–6 GB RAM), Qwen 8B for typical laptops (~8–12 GB RAM), and 14B+ for powerful systems (~16–24+ GB RAM). Exact memory varies by quantization and context.

## Usage

```bash
ai-debug analyze examples/sample_application.log --model qwen3:8b --format markdown --output report.md
ai-debug analyze ./logs --format html --output report.html
ai-debug analyze examples/sample_application.log --format json
ai-debug analyze examples/sample_application.log --offline --verbose
ai-debug models
ai-debug config
```

The first local-model request can take several minutes while a large model loads. The default timeout is 600 seconds; override it when needed with `AI_DEBUG_OLLAMA_TIMEOUT=900`. Use `--no-verification` to skip the second LLM pass while diagnosing performance.

Facts observed in logs, model hypotheses, and recommended actions are deliberately separate. A hypothesis is never treated as a confirmed cause.

## Security & privacy

The redactor removes bearer tokens, JWTs, passwords, AWS access keys, database URLs, private keys, and email addresses from model context. It is pattern based, so review reports before sharing. The model endpoint defaults to `127.0.0.1`; no internet connection is used after Ollama and a model have been installed.

## Performance

Input is streamed line-by-line and `--max-file-size`, `--max-lines`, and `--max-context` bound work and model context. The MVP keeps significant events in memory, so exceptionally error-dense multi-gigabyte logs should be constrained with `--max-lines`; disk-backed aggregation is a planned optimization.

## Evaluation

`python evaluations/evaluate.py` runs deterministic extraction benchmarks. It measures important-event recall and timeline presence. For LLM evaluation, pin a local model and assess root-cause category, evidence grounding, unsupported-claim rate, timeline ordering, and recommendation relevance against labeled incidents.

## Development

```bash
pip install -e '.[dev]'
python -m pytest
python evaluations/evaluate.py
```

## Roadmap

Local semantic embeddings, disk-backed aggregation, FastAPI local UI, richer format plugins, and optional repository context are planned. The core remains local-first.

## License

MIT.
