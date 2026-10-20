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
        self.assertEqual(self.page.project_cards,4)
    def test_navigation_targets(self):
        self.assertFalse(set(self.page.anchors)-self.page.sections-{"page-top"})
    def test_theme_linked(self):
        self.assertIn("css/professional.css",self.page.styles)
    def test_mobile_and_accessibility(self):
        self.assertIn("@media(max-width:991.98px)",self.css)
        self.assertIn("prefers-reduced-motion",self.css)
        self.assertTrue(all(img.get("alt") is not None for img in self.page.images))
    def test_social_metadata(self):
        self.assertIn('rel="canonical" href="https://3bhussein.github.io/"', self.html)
        self.assertIn('name="theme-color"', self.html)
        self.assertIn('https://3bhussein.github.io/assets/img/profile.jfif', self.html)
    def test_v2_design(self):
        self.assertIn('href="css/portfolio-v2.css"', self.html)
        self.assertIn('class="hero-kicker"', self.html)
        self.assertIn('class="hero-actions"', self.html)
        v2=(ROOT/"css/portfolio-v2.css").read_text(encoding="utf-8")
        self.assertIn("#about",v2)
        self.assertIn("@media(max-width:620px)",v2)
    def test_v3_rebuilt_layout(self):
        self.assertIn('class="v3-header"',self.html)
        self.assertIn('class="v3-hero-grid"',self.html)
        self.assertNotIn('id="sideNav"',self.html)
        self.assertIn('href="css/portfolio-v3.css"',self.html)
        self.assertIn('src="js/portfolio-v3.js"',self.html)
        css=(ROOT/"css/portfolio-v3.css").read_text(encoding="utf-8")
        self.assertIn("@media(max-width:620px)",css)
    def test_autel_concept(self):
        self.assertIn('autel-code-tracker.html',self.html)
        concept=(ROOT/'autel-code-tracker.html').read_text()
        self.assertIn('CONCEPT CASE STUDY',concept)
        self.assertIn('synthetic',concept)
        self.assertTrue((ROOT/'assets/img/autel-tracker-demo.webp').is_file())
        self.assertNotIn('workers.dev',concept)
        self.assertNotIn('supabase.co',concept)
    def test_no_global_blank_target(self):
        self.assertNotIn('<base target="_blank">',self.html)

if __name__=="__main__": unittest.main()

