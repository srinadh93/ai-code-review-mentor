#!/usr/bin/env python3
import click
import os
from rag_engine import RAGEngine

@click.group()
@click.option('--ollama-url', default=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'), help='Ollama base URL')
@click.option('--model', default=os.getenv('LLM_MODEL', 'codellama:7b'), help='LLM model name')
@click.pass_context
def cli(ctx, ollama_url, model):
    ctx.ensure_object(dict)
    ctx.obj['engine'] = RAGEngine(ollama_url, model)

@cli.command()
@click.argument('repo_path', type=click.Path(exists=True))
@click.pass_context
def index(ctx, repo_path):
    """Index a repository for querying."""
    engine = ctx.obj['engine']
    try:
        engine.index_repo(repo_path)
        click.echo("Repository indexed successfully.")
    except Exception as e:
        click.echo(f"Error indexing repo: {e}", err=True)

@cli.command()
@click.argument('question')
@click.option('--repo', 'repo_path', type=click.Path(exists=True), required=True, help='Path to the indexed repository')
@click.option('--top-k', default=5, help='Number of top chunks to retrieve')
@click.pass_context
def query(ctx, question, repo_path, top_k):
    """Query the indexed repository."""
    engine = ctx.obj['engine']
    try:
        chunks = engine.query_repo(question, repo_path, top_k)
        if not chunks:
            click.echo("No relevant code found.")
            return
        response = engine.generate_response(question, chunks)
        click.echo(response)
    except Exception as e:
        click.echo(f"Error querying: {e}", err=True)

if __name__ == '__main__':
    cli()