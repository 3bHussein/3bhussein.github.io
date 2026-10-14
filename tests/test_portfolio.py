from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
class PortfolioParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections=set(); self.anchors=[]; self.styles=[]; self.project_cards=0; self.images=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="section" and a.get("id"): self.sections.add(a["id"])
        if tag=="a" and a.get("href","").startswith("#"): self.anchors.append(a["href"][1:])
        if tag=="link" and a.get("rel")=="stylesheet": self.styles.append(a.get("href"))
        if tag=="article" and "pro-project" in a.get("class","").split(): self.project_cards+=1
        if tag=="img": self.images.append(a)

class PortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/"index.html").read_text(encoding="utf-8")
        cls.css=(ROOT/"css/professional.css").read_text(encoding="utf-8")
        cls.page=PortfolioParser();cls.page.feed(cls.html)
    def test_original_sections_preserved(self):
        self.assertTrue({"about","experience","education","skills","languages","certificates"}.issubset(self.page.sections))
    def test_projects_present(self):
        self.assertIn("projects",self.page.sections)
        self.assertEqual(self.page.project_cards,3)
    def test_navigation_targets(self):
        self.assertFalse(set(self.page.anchors)-self.page.sections-{"page-top"})
    def test_theme_linked(self):
        self.assertIn("css/professional.css",self.page.styles)
    def test_mobile_and_accessibility(self):
        self.assertIn("@media(max-width:991.98px)",self.css)
        self.assertIn("prefers-reduced-motion",self.css)
        self.assertTrue(all(img.get("alt") is not None for img in self.page.images))
    def test_no_global_blank_target(self):
        self.assertNotIn('<base target="_blank">',self.html)

if __name__=="__main__": unittest.main()
