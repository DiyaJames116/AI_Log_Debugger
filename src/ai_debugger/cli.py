from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import typer

from ai_debugger import __version__
from ai_debugger.config import Settings
from ai_debugger.llm.ollama import OllamaProvider
from ai_debugger.pipeline import analyze as run_analysis
from ai_debugger.reporting.html import render as html_report
from ai_debugger.reporting.markdown import render as markdown_report

app = typer.Typer(help="Private, local-first AI-assisted log debugging.", no_args_is_help=True)


@app.command()
def analyze(
    path: Path = typer.Argument(..., exists=True),
    model: str | None = typer.Option(None),
    format: str = typer.Option("markdown", "--format", case_sensitive=False),
    output: Path | None = typer.Option(None),
    max_file_size: int = typer.Option(2 * 1024 * 1024 * 1024),
    max_lines: int | None = typer.Option(None),
    max_context: int = typer.Option(12000),
    verbose: bool = False,
    no_embeddings: bool = typer.Option(
        False, help="Reserved for future local semantic retrieval; lexical retrieval is used."
    ),
    no_verification: bool = False,
    offline: bool = typer.Option(
        False, help="Produce an evidence-only report without calling Ollama."
    ),
):
    """Analyze a log file or directory. Logs never leave this machine."""
    if format not in {"markdown", "json", "html"}:
        raise typer.BadParameter("format must be markdown, json, or html")
    settings = Settings(
        model=model or Settings().model,
        max_file_size=max_file_size,
        max_lines=max_lines,
        max_context=max_context,
    )
    provider = (
        None
        if offline
        else OllamaProvider(settings.model, settings.ollama_url, settings.ollama_timeout)
    )
    try:
        result = run_analysis(path, settings, provider, not no_verification)
    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        raise typer.Exit(typer.echo(f"Error: {exc}", err=True) or 2)
    if verbose:
        typer.echo("  ".join(f"{k.upper()} {v:,}" for k, v in result.metrics.items()), err=True)
    if format == "json":
        rendered = json.dumps(
            {
                "analysis": result.analysis.model_dump(mode="json"),
                "metrics": result.metrics,
                "timeline": [e.model_dump(mode="json") for e in result.timeline],
                "error_clusters": [
                    c.model_dump(mode="json", exclude={"events"}) for c in result.clusters
                ],
            },
            indent=2,
            default=str,
        )
    else:
        rendered = {"markdown": markdown_report, "html": html_report}[format](
            result.analysis, result.timeline, result.clusters
        )
    if output:
        output.write_text(rendered, encoding="utf-8")
        typer.echo(f"Wrote {output}")
    else:
        typer.echo(rendered)


@app.command()
def setup():
    """Check the local runtime needed for private AI analysis."""
    s = Settings()
    typer.echo(f"Python: {sys.version.split()[0]} (required: 3.11+)")
    typer.echo(
        f"Ollama: {'found at ' + shutil.which('ollama') if shutil.which('ollama') else 'not found'}"
    )
    try:
        typer.echo("Models: " + ", ".join(OllamaProvider(s.model, s.ollama_url).models()))
    except Exception:
        typer.echo("Models: unavailable (start Ollama, then run `ollama pull qwen3:8b`)")
    try:
        typer.echo(f"Free disk space: {shutil.disk_usage('.').free // (1024**3)} GiB")
    except OSError:
        pass


@app.command()
def models():
    """List models installed in the local Ollama runtime."""
    try:
        settings = Settings()
        for model in OllamaProvider(
            settings.model, settings.ollama_url, settings.ollama_timeout
        ).models():
            typer.echo(model)
    except RuntimeError as exc:
        raise typer.Exit(typer.echo(str(exc), err=True) or 1)


@app.command()
def config():
    s = Settings()
    typer.echo(
        f"model={s.model}\nollama_url={s.ollama_url}\nollama_timeout={s.ollama_timeout:g}s\nNo telemetry. No cloud analysis."
    )


@app.command()
def version():
    typer.echo(__version__)


if __name__ == "__main__":
    app()
