import hashlib
import tempfile
import unittest
from pathlib import Path
from html.parser import HTMLParser
from s_alpha.fusion_website import build_website

class Reader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags=[]
        self.data=[]
    def handle_starttag(self,tag,attrs):
        self.tags.append(tag)
        if any(k.startswith("on") or k in ("src","href") for k,v in attrs):
            raise AssertionError("unexpected active attribute")
    def handle_data(self,data):
        self.data.append(data)

class WebsiteTests(unittest.TestCase):
    def test_independent_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=build_website({"title":"Demo","heading":"Welcome","paragraphs":["Offline content"]},tmp)
            data=(Path(tmp)/"index.html").read_bytes()
            parser=Reader()
            parser.feed(data.decode())
            self.assertEqual(parser.tags.count("h1"),1)
            self.assertIn("Welcome",parser.data)
            self.assertIn("Offline content",parser.data)
            self.assertEqual(hashlib.sha256(data).hexdigest(),result["artifact"]["sha256"])
    def test_injection_is_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload='<script>alert(1)</script><img src=x onerror=alert(1)>'
            build_website({"title":"Demo","heading":payload,"paragraphs":[payload]},tmp)
            parser=Reader()
            parser.feed((Path(tmp)/"index.html").read_text(encoding="utf-8"))
            self.assertNotIn("script",parser.tags)
            self.assertNotIn("img",parser.tags)
            self.assertIn(payload,parser.data)
    def test_invalid_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                build_website({"title":"Demo","heading":"Hi","paragraphs":[]},tmp)
            self.assertFalse((Path(tmp)/"index.html").exists())
            spec={"title":"Demo","heading":"Hi","paragraphs":["Text"]}
            build_website(spec,tmp)
            with self.assertRaises(FileExistsError):
                build_website(spec,tmp)
