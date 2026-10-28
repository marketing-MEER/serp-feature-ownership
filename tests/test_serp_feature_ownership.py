import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

from serp_feature_ownership import cli, core

EXAMPLES = Path(__file__).parent.parent / "examples"

YOU = """Keyword,Position,Search Volume,URL,SERP Features by Keyword,Position Type
what is a crm,4,6600,https://me.com/what,"Featured snippet, People also ask, Video carousel, Related searches",Organic
crm pricing,2,1300,https://me.com/pricing,"People also ask, Image pack",People also ask
free crm,40,8100,https://me.com/free,"Featured snippet, AI Overviews",Organic
"""
RIVAL = """Keyword,Volume,Current position,Current URL,SERP features,Owned features
what is a crm,6600,1,https://www.rival.io/what,"Featured snippet, People also ask, Videos",Featured snippet
free crm,8100,1,https://www.rival.io/free,"Featured snippet, AI Overview","Featured snippet, AI Overview"
"""


class CoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        (d / "you.csv").write_text(YOU, encoding="utf-8")
        (d / "rival.csv").write_text(RIVAL, encoding="utf-8")
        self.pairs, self.sites, self.n = core.analyze(d / "you.csv", [d / "rival.csv"])
        self.s = self.pairs.set_index(["keyword", "feature"])["status"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_feature_names_are_normalised(self):
        self.assertEqual(core.split_features("Video carousel; image pack | PAA, organic"),
                         ["Images", "People also ask", "Videos"])
        self.assertEqual(self.sites, ["me.com", "rival.io"])
        self.assertEqual(self.n, 3)

    def test_statuses(self):
        self.assertEqual(self.s[("what is a crm", "Featured snippet")], "steal")     # rival holds it, you rank 4
        self.assertEqual(self.s[("what is a crm", "People also ask")], "open")       # nobody holds it, you rank 4
        self.assertEqual(self.s[("crm pricing", "People also ask")], "defend")       # your Position Type
        self.assertEqual(self.s[("free crm", "AI Overview")], "out of reach")        # you rank 40
        self.assertEqual(self.s[("what is a crm", "Related searches")], "not ownable")

    def test_landscape_and_ownership(self):
        land = core.landscape(self.pairs, self.n).set_index("feature")
        self.assertEqual(land.at["Featured snippet", "keywords"], 2)
        self.assertEqual(land.at["Videos", "benchmark_presence_2024_pct"], 76)
        own = core.ownership(self.pairs, self.sites).set_index("feature")
        self.assertEqual(own.at["Featured snippet", "rival.io"], 2)
        self.assertEqual(own.at["People also ask", "me.com"], 1)

    def test_steal_sorted_first(self):
        self.assertEqual(self.pairs.iloc[0]["status"], "steal")


class CliTest(unittest.TestCase):
    def test_example_writes_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "serp"
            args = [str(EXAMPLES / f) for f in ["brightcrm_serp.csv", "pipelinehq_serp.csv", "salesdeck_serp.csv"]]
            res = CliRunner().invoke(cli.main, args + ["-o", str(out)])
            self.assertEqual(res.exit_code, 0, res.output)
            self.assertIn("SERP feature ownership", out.with_suffix(".html").read_text(encoding="utf-8"))
            self.assertTrue(out.with_suffix(".xlsx").exists())


if __name__ == "__main__":
    unittest.main()
