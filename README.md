# AI Code Review Mentor

A command-line tool that uses Retrieval-Augmented Generation (RAG) and Abstract Syntax Tree (AST) parsing to analyze code repositories and provide intelligent answers to questions about the codebase.

## Features

- **AST-Based Code Chunking**: Uses tree-sitter to parse Python code into meaningful chunks (functions, classes) for better context.
- **RAG Pipeline**: Embeds code chunks using sentence transformers and stores them in ChromaDB for efficient retrieval.
- **Local LLM Integration**: Uses Ollama to run local LLMs like CodeLlama for generating responses.
- **Containerized**: Fully containerized with Docker for easy deployment and reproducibility.

## Architecture

The application consists of two main components:

1. **mentor.py**: The CLI interface with commands to index repositories and query them.
2. **rag_engine.py**: The core RAG engine handling AST parsing, embedding, vector storage, and LLM interaction.

### Workflow

1. **Indexing**: Parse Python files in the repository, extract code chunks, generate embeddings, and store in ChromaDB.
2. **Querying**: Embed the user's question, retrieve relevant code chunks, and generate a response using the LLM.

## Prerequisites

- Docker and Docker Compose
- Ollama running locally with a code-specialized model (e.g., codellama:7b)

## Setup

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd ai-code-review-mentor
   ```

2. Install Ollama and pull the model:
   ```bash
   # Install Ollama from https://ollama.ai/
   ollama pull codellama:7b
   ```

3. Copy the environment file:
   ```bash
   cp .env.example .env
   # Edit .env if necessary (default should work for most setups)
   ```

4. Build and run the container:
   ```bash
   docker-compose up --build
   ```

## Usage

### Index a Repository

```bash
docker-compose exec mentor python mentor.py index /app/sample_repo
```

### Query the Repository

```bash
docker-compose exec mentor python mentor.py query "What are the bugs in the user model?" --repo /app/sample_repo
```

### Example Queries

- "Explain the process_order function"
- "What validation is done on user emails?"
- "Identify potential bugs in the codebase"

## Configuration

Environment variables in `.env`:

- `OLLAMA_BASE_URL`: URL for Ollama API (default: http://host.docker.internal:11434 for Mac/Windows)
- `LLM_MODEL`: Model to use (default: codellama:7b)

## Development

### Running Tests

```bash
docker-compose exec mentor pytest tests/
```

### Adding New Languages

To support languages other than Python, add the corresponding tree-sitter grammar and update the parser in `rag_engine.py`.

## Limitations

- Currently supports only Python code
- Requires significant RAM for larger models
- Indexing is done per repository hash; changes require re-indexing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

## License

MIT License