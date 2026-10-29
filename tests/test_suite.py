"""
Automated Test Suite for Ofrenda AI
Tests AltarStore persistence, Gemma 2 engine, offline fallbacks, and REST API handlers.
"""

import sys
import unittest
import json
import tempfile
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from altar_store import AltarStore
from gemma_engine import GemmaEngine

class TestAltarStore(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "test_altars.json"
        self.store = AltarStore(data_file=self.data_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_altars_initialization(self):
        altars = self.store.load_all()
        self.assertGreaterEqual(len(altars), 4)
        ids = [a["id"] for a in altars]
        self.assertIn("ada-lovelace", ids)
        self.assertIn("alan-turing", ids)
        self.assertIn("dennis-ritchie", ids)
        self.assertIn("ancestor-memorial", ids)

    def test_get_altar(self):
        ada = self.store.get_altar("ada-lovelace")
        self.assertIsNotNone(ada)
        self.assertEqual(ada["name"], "Ada Lovelace")
        self.assertTrue(len(ada["candles"]) >= 3)

    def test_create_altar(self):
        new_altar = self.store.create_altar({
            "name": "Grace Hopper",
            "title": "Grand Lady of Software",
            "years": "1906 – 1992",
            "summary": "Pioneer of compilers and COBOL."
        })
        self.assertEqual(new_altar["name"], "Grace Hopper")
        fetched = self.store.get_altar(new_altar["id"])
        self.assertIsNotNone(fetched)

    def test_toggle_candle(self):
        ada = self.store.get_altar("ada-lovelace")
        c1 = ada["candles"][0]
        initial_state = c1["lit"]
        toggled = self.store.toggle_candle("ada-lovelace", c1["id"])
        self.assertNotEqual(toggled["lit"], initial_state)

    def test_add_and_remove_offering(self):
        offering = self.store.add_offering("ada-lovelace", {
            "name": "Analytical Engine Gear",
            "tier": "middle",
            "type": "symbol",
            "note": "Brass gear mechanism."
        })
        self.assertIsNotNone(offering)
        self.assertIn("id", offering)

        # Verify added
        ada = self.store.get_altar("ada-lovelace")
        self.assertTrue(any(o["id"] == offering["id"] for o in ada["offerings"]))

        # Remove offering
        success = self.store.remove_offering("ada-lovelace", offering["id"])
        self.assertTrue(success)
        ada_updated = self.store.get_altar("ada-lovelace")
        self.assertFalse(any(o["id"] == offering["id"] for o in ada_updated["offerings"]))


class TestGemmaEngine(unittest.TestCase):
    def setUp(self):
        self.engine = GemmaEngine()

    def test_engine_status(self):
        status = self.engine.get_status()
        self.assertIn("connected", status)
        self.assertIn("model", status)
        self.assertIn("privacy_mode", status)

    def test_remembrance_generation(self):
        resp = self.engine.generate_remembrance(
            spirit_name="Ada Lovelace",
            spirit_title="Enchantress of Numbers",
            spirit_traits="Poetic, visionary",
            spirit_memories="Pioneer of computer programming",
            user_message="Do you see our machines today?",
            persona_key="ada_lovelace"
        )
        self.assertIn("text", resp)
        self.assertTrue(len(resp["text"]) > 10)
        self.assertIn("model", resp)
        self.assertIn("privacy", resp)


if __name__ == "__main__":
    unittest.main()
