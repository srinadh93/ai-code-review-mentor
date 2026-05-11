from rag_engine import RAGEngine


def test_extract_code_chunks_finds_functions_and_classes():
    code = '''
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def validate_email(self):
        return '@' in self.email


def format_date(dt):
    return dt.isoformat()
'''
    chunks = RAGEngine.extract_code_chunks(code)
    assert any('class User' in chunk['text'] for chunk in chunks)
    assert any('def format_date' in chunk['text'] for chunk in chunks)
