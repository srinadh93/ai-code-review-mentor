import hashlib
import os
from typing import Any, Dict, List

import chromadb
import requests
import tree_sitter_python as tspython
from requests.exceptions import RequestException
from sentence_transformers import SentenceTransformer
from tree_sitter import Language, Parser


class RAGEngine:
    def __init__(self, ollama_url: str, model_name: str):
        self.ollama_url = ollama_url.rstrip('/')
        self.model_name = model_name
        self.embedding_model = SentenceTransformer(
            os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        )
        db_path = os.path.abspath(os.getenv('CHROMA_DB_PATH', './chroma_db'))
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = None
        self.parser = Parser()
        self.parser.set_language(Language(tspython.language()))

    @staticmethod
    def get_repo_hash(repo_path: str) -> str:
        """Generate a hash for the repo to check whether it has changed."""
        hash_md5 = hashlib.md5()
        for root, _, files in os.walk(repo_path):
            for file in sorted(files):
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'rb') as f:
                        for chunk in iter(lambda: f.read(4096), b''):
                            hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def extract_code_chunks(code: str) -> List[Dict[str, Any]]:
        parser = Parser()
        parser.set_language(Language(tspython.language()))
        tree = parser.parse(bytes(code, 'utf8'))
        chunks: List[Dict[str, Any]] = []

        def traverse(node):
            if node.type in ['function_definition', 'class_definition', 'decorated_definition']:
                start_line = node.start_point[0] + 1
                end_line = node.end_point[0] + 1
                chunk_text = code[node.start_byte:node.end_byte]
                chunks.append({
                    'text': chunk_text,
                    'start_line': start_line,
                    'end_line': end_line,
                })
            for child in node.children:
                traverse(child)

        traverse(tree.root_node)
        return chunks

    def parse_code(self, code: str) -> List[Dict[str, Any]]:
        """Parse code and extract meaningful function and class chunks."""
        return self.extract_code_chunks(code)

    def _get_or_create_collection(self, name: str):
        try:
            return self.client.get_collection(name=name)
        except Exception:
            return self.client.create_collection(name=name)

    def index_repo(self, repo_path: str):
        repo_path = os.path.abspath(repo_path)
        repo_hash = self.get_repo_hash(repo_path)
        collection_name = f'repo_{repo_hash}'
        self.collection = self._get_or_create_collection(collection_name)

        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []
        id_counter = 0

        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf8') as f:
                        code = f.read()
                    chunks = self.parse_code(code)
                    for chunk in chunks:
                        documents.append(chunk['text'])
                        metadatas.append({
                            'file': filepath,
                            'start_line': chunk['start_line'],
                            'end_line': chunk['end_line'],
                        })
                        ids.append(str(id_counter))
                        id_counter += 1

        if not documents:
            raise ValueError('No Python code was found to index.')

        embeddings = self.embedding_model.encode(documents, show_progress_bar=False)
        self.collection.add(
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids,
        )

    def query_repo(self, query: str, repo_path: str, top_k: int = 5) -> List[Dict[str, Any]]:
        repo_path = os.path.abspath(repo_path)
        if not self.collection:
            repo_hash = self.get_repo_hash(repo_path)
            collection_name = f'repo_{repo_hash}'
            try:
                self.collection = self.client.get_collection(name=collection_name)
            except Exception as exc:
                raise ValueError('Repo not indexed. Run index first.') from exc

        query_embedding = self.embedding_model.encode([query], show_progress_bar=False)[0]
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=['documents', 'metadatas'],
        )

        relevant_chunks: List[Dict[str, Any]] = []
        documents = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        for i, doc_text in enumerate(documents):
            metadata = metadatas[i]
            relevant_chunks.append({
                'file': metadata['file'],
                'start_line': metadata['start_line'],
                'end_line': metadata['end_line'],
                'text': doc_text,
            })

        return relevant_chunks

    @staticmethod
    def build_prompt(query: str, chunks: List[Dict[str, Any]]) -> str:
        prompt = (
            'You are an expert code review assistant. Your goal is to provide clear, educational explanations to junior developers. '
            'Analyze the following code snippets to answer the user\'s question.\n\n'
            f'User Question: {query}\n\nRelevant Code Snippets:\n'
        )
        for chunk in chunks:
            prompt += (
                f"File: {chunk['file']} Lines: {chunk['start_line']}-{chunk['end_line']}\n"
                f"{chunk['text']}\n\n"
            )
        prompt += 'Answer the user\'s question. Reference the specific file and line numbers where the relevant code can be found.'
        return prompt

    def generate_response(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        payload = {
            'model': self.model_name,
            'prompt': self.build_prompt(query, chunks),
            'stream': False,
        }
        try:
            response = requests.post(f'{self.ollama_url}/api/generate', json=payload, timeout=60)
            response.raise_for_status()
        except RequestException as exc:
            raise ConnectionError(f'Could not connect to Ollama at {self.ollama_url}') from exc

        data = response.json()
        if 'response' in data:
            return data['response']

        if 'results' in data and data['results']:
            first_result = data['results'][0]
            content = first_result.get('content')
            if isinstance(content, list):
                return ''.join(item.get('text', '') for item in content if isinstance(item, dict))
            if isinstance(content, str):
                return content
            if 'text' in first_result:
                return first_result['text']

        raise RuntimeError(f'Unexpected Ollama response format: {data}')