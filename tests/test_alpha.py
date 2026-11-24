import tempfile
import unittest
from pathlib import Path
from s_alpha.universal import execute
from s_alpha.create import create
from s_alpha.learn import score

class AlphaTests(unittest.TestCase):
    def test_integration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'out'
            db = Path(tmp)/'learn.sqlite3'
            result = execute(dict(version=1, operation='create_text', id='1', name='a.txt', content='hello'), root, db)
            self.assertEqual(result['status'], 'created')
            self.assertEqual((root/'a.txt').read_text(), 'hello')
            self.assertEqual(score(db), 1)
    def test_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                create(tmp, '../escape', 'x')
    def test_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            create(tmp, 'a', 'first')
            with self.assertRaises(FileExistsError):
                create(tmp, 'a', 'second')
    def test_unknown(self):
        with self.assertRaises(ValueError):
            execute({'version': 1, 'operation': 'shell'}, None, None)
