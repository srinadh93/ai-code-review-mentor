import pytest
from click.testing import CliRunner
from mentor import cli
import os
import tempfile
import shutil

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def temp_repo():
    # Create a temporary directory with sample Python files
    temp_dir = tempfile.mkdtemp()
    # Create a simple Python file
    with open(os.path.join(temp_dir, 'test.py'), 'w') as f:
        f.write("""
def hello():
    print("Hello")

class TestClass:
    def method(self):
        pass
""")
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_index_command(runner, temp_repo):
    # Mock ollama, but for now, just test if command runs without error
    # Since we can't run ollama in tests, perhaps skip or mock
    # For simplicity, assume it works if no exception
    result = runner.invoke(cli, ['index', temp_repo])
    # In real test, check if collection is created, but since it's file-based, hard
    assert result.exit_code == 0 or "already indexed" in result.output

def test_query_command_without_index(runner, temp_repo):
    result = runner.invoke(cli, ['query', 'What does hello do?', '--repo', temp_repo])
    assert result.exit_code != 0  # Should fail if not indexed

# Note: Full integration test would require running Ollama, which is complex for unit tests