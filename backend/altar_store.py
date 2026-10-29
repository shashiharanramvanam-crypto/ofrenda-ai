"""
Local Altar Store for Ofrenda AI
Persists altars, offerings, candles, and remembrance records in local JSON.
Ensures zero cloud storage, complete data sovereignty, and offline permanence.
"""

import os
import json
import uuid
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

DATA_DIR = Path(__file__).parent.parent / "data"
ALTARS_FILE = DATA_DIR / "altars.json"

DEFAULT_ALTARS: List[Dict[str, Any]] = [
    {
        "id": "ada-lovelace",
        "name": "Ada Lovelace",
        "title": "Enchantress of Numbers & Mother of Computing",
        "years": "1815 – 1852",
        "persona_key": "ada_lovelace",
        "summary": "First computer programmer who foresaw that the Analytical Engine could compose music and weave algorithmic tapestries.",
        "avatar": "🦋",
        "theme_color": "#9d4edd",
        "background_symbol": "analytical_engine",
        "candles": [
            {"id": "c1", "lit": True, "label": "Flame of Imagination"},
            {"id": "c2", "lit": True, "label": "The First Algorithm (Bernoulli Numbers)"},
            {"id": "c3", "lit": True, "label": "Poetical Science"}
        ],
        "offerings": [
            {"id": "off1", "tier": "top", "type": "portrait", "name": "Portrait with Jasmine Flowers", "note": "Painted in 1836, eyes bright with visions of the machine age."},
            {"id": "off2", "tier": "middle", "type": "symbol", "name": "Jacquard Loom Punched Cards", "note": "Weaving algebraic patterns just as the loom weaves flowers and leaves."},
            {"id": "off3", "tier": "middle", "type": "food", "name": "Darjeeling Tea & Scottish Shortbread", "note": "Her companion during late night mathematical correspondence with Babbage."},
            {"id": "off4", "tier": "bottom", "type": "element", "name": "Cempasúchil Trail & Copal Incense", "note": "Guiding her spirit back from 1852 into the modern digital world."}
        ],
        "memories": "Remembered for proving that computation is an art form, uniting science with human poetry.",
        "traits": "Brilliant, poetic, visionary, aristocratic yet rebellious, passionately curious.",
        "created_at": "2026-10-29T00:00:00Z"
    },
    {
        "id": "alan-turing",
        "name": "Alan Turing",
        "title": "Father of Computer Science & Morphogenetic Visionary",
        "years": "1912 – 1954",
        "persona_key": "alan_turing",
        "summary": "Cryptanalyst, mathematician, and philosopher who cracked the Enigma, conceptualized the Universal Turing Machine, and studied patterns in sunflowers.",
        "avatar": "🌻",
        "theme_color": "#e0a96d",
        "background_symbol": "sunflower_fibonacci",
        "candles": [
            {"id": "c1", "lit": True, "label": "The Universal Machine"},
            {"id": "c2", "lit": True, "label": "Bletchley Park Solitude"},
            {"id": "c3", "lit": True, "label": "Fibonacci Sunflowers"}
        ],
        "offerings": [
            {"id": "off1", "tier": "top", "type": "symbol", "name": "Paper Tape with Infinite Squares", "note": "The theoretical blueprint for every modern computer in existence."},
            {"id": "off2", "tier": "middle", "type": "nature", "name": "Golden Spiral Sunflower Heads", "note": "Studying nature's mathematical morphogenesis in his final quiet years."},
            {"id": "off3", "tier": "middle", "type": "food", "name": "Fresh Green Apples & Earl Grey", "note": "Placed with profound remorse and boundless gratitude."},
            {"id": "off4", "tier": "bottom", "type": "element", "name": "Bowl of Clear Water & Sea Salt", "note": "To purify the unhealed wounds of history and quench his journey."}
        ],
        "memories": "He saved tens of millions of lives and gave humanity the key to computation.",
        "traits": "Modest, deeply contemplative, gentle, eccentric, enduringly kind.",
        "created_at": "2026-10-29T00:00:00Z"
    },
    {
        "id": "dennis-ritchie",
        "name": "Dennis Ritchie (dmr)",
        "title": "Architect of C & The Soul of UNIX",
        "years": "1941 – 2011",
        "persona_key": "dennis_ritchie",
        "summary": "Quiet pioneer who designed C and co-created Unix at Bell Labs, creating the foundational substrate of the modern internet and operating systems.",
        "avatar": "⚡",
        "theme_color": "#48cae4",
        "background_symbol": "unix_terminal",
        "candles": [
            {"id": "c1", "lit": True, "label": "printf(\"Hello, World!\\n\");"},
            {"id": "c2", "lit": True, "label": "The Elegant Pointer *dmr"},
            {"id": "c3", "lit": True, "label": "Unix Philosophy (Do One Thing Well)"}
        ],
        "offerings": [
            {"id": "off1", "tier": "top", "type": "symbol", "name": "The K&R C Programming Language White Book", "note": "Crisp, concise, immortal prose."},
            {"id": "off2", "tier": "middle", "type": "food", "name": "Black Filter Coffee in a Bell Labs Ceramic Mug", "note": "Fuel for late night kernel compilations on the PDP-11."},
            {"id": "off3", "tier": "middle", "type": "tech", "name": "VT100 Amber Phosphor Terminal", "note": "Glowing with a single blinking cursor and /bin/sh prompt."},
            {"id": "off4", "tier": "bottom", "type": "element", "name": "Pan de Muerto dusted with Sugar & Marigolds", "note": "Honoring the quiet genius whose code runs in every pocket today."}
        ],
        "memories": "His code was unobtrusive, powerful, and built to stand the test of time.",
        "traits": "Humble, understated, wry humor, legendary craftsman, deeply generous.",
        "created_at": "2026-10-29T00:00:00Z"
    },
    {
        "id": "ancestor-memorial",
        "name": "Abuela Elena & The Ancestors",
        "title": "Beloved Family Ancestor",
        "years": "1932 – 2018",
        "persona_key": "ancestor",
        "summary": "A warm traditional family altar remembering beloved ancestors, their laughter, secret recipes, and unconditional love.",
        "avatar": "🕯️",
        "theme_color": "#ff758f",
        "background_symbol": "calavera_marigold",
        "candles": [
            {"id": "c1", "lit": True, "label": "Light for the Journey Home"},
            {"id": "c2", "lit": True, "label": "Warmth of Sunday Dinners"},
            {"id": "c3", "lit": True, "label": "Eternal Blessing"}
        ],
        "offerings": [
            {"id": "off1", "tier": "top", "type": "portrait", "name": "Vintage Framed Black-and-White Photo", "note": "Smiling in the courtyard surrounded by blooming bougainvillea."},
            {"id": "off2", "tier": "middle", "type": "food", "name": "Spiced Mexican Hot Chocolate & Fresh Pan Dulce", "note": "Made with cinnamon, Mexican chocolate tablets, and topped with froth."},
            {"id": "off3", "tier": "middle", "type": "memory", "name": "Hand-embroidered Floral Shawl & Rosary", "note": "Passed down through four generations with love."},
            {"id": "off4", "tier": "bottom", "type": "element", "name": "Clay Vessel of Well Water & Cross of Salt", "note": "Purifying their path and welcoming them back home for Día de los Muertos."}
        ],
        "memories": "Her kitchen smelled like cinnamon and roasted chilies, and nobody ever left her home hungry.",
        "traits": "Warm, loving, matriarchal, full of wisdom, rich in laughter and stories.",
        "created_at": "2026-10-29T00:00:00Z"
    }
]


class AltarStore:
    def __init__(self, data_file: Path = ALTARS_FILE):
        self.data_file = data_file
        self.ensure_storage()

    def ensure_storage(self):
        """Create data directory and initialize default altars if missing."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self.save_all(DEFAULT_ALTARS)

    def load_all(self) -> List[Dict[str, Any]]:
        """Load all altars from local disk."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_ALTARS

    def save_all(self, altars: List[Dict[str, Any]]):
        """Persist all altars to local disk."""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(altars, f, indent=2, ensure_ascii=False)

    def get_altar(self, altar_id: str) -> Optional[Dict[str, Any]]:
        """Find an altar by ID."""
        for a in self.load_all():
            if a["id"] == altar_id:
                return a
        return None

    def create_altar(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new personal or ancestor altar."""
        altars = self.load_all()
        new_id = data.get("id") or str(uuid.uuid4())[:8]
        new_altar = {
            "id": new_id,
            "name": data.get("name", "Beloved Spirit"),
            "title": data.get("title", "Honored Soul"),
            "years": data.get("years", "Forever Remembered"),
            "persona_key": data.get("persona_key", "ancestor"),
            "summary": data.get("summary", "A sacred altar of memory and light."),
            "avatar": data.get("avatar", "🕯️"),
            "theme_color": data.get("theme_color", "#ffaa00"),
            "background_symbol": data.get("background_symbol", "calavera_marigold"),
            "candles": data.get("candles", [
                {"id": "c1", "lit": True, "label": "Candle of Memory"},
                {"id": "c2", "lit": True, "label": "Candle of Peace"}
            ]),
            "offerings": data.get("offerings", [
                {"id": "off1", "tier": "top", "type": "symbol", "name": "Memorial Light", "note": "Honoring their journey."},
                {"id": "off2", "tier": "bottom", "type": "element", "name": "Pure Water & Cempasúchil", "note": "To guide them home."}
            ]),
            "memories": data.get("memories", "Treasured moments held in the heart."),
            "traits": data.get("traits", "Kind, remembered, loved."),
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        altars.append(new_altar)
        self.save_all(altars)
        return new_altar

    def update_altar(self, altar_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing altar fields."""
        altars = self.load_all()
        for i, a in enumerate(altars):
            if a["id"] == altar_id:
                altars[i].update(updates)
                self.save_all(altars)
                return altars[i]
        return None

    def toggle_candle(self, altar_id: str, candle_id: str) -> Optional[Dict[str, Any]]:
        """Toggle a candle flame between lit and unlit."""
        altar = self.get_altar(altar_id)
        if not altar:
            return None
        for c in altar.get("candles", []):
            if c["id"] == candle_id:
                c["lit"] = not c.get("lit", True)
                self.update_altar(altar_id, {"candles": altar["candles"]})
                return c
        return None

    def add_offering(self, altar_id: str, offering: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add an offering to an altar tier."""
        altar = self.get_altar(altar_id)
        if not altar:
            return None
        offering["id"] = offering.get("id") or str(uuid.uuid4())[:8]
        if "tier" not in offering:
            offering["tier"] = "middle"
        altar.setdefault("offerings", []).append(offering)
        self.update_altar(altar_id, {"offerings": altar["offerings"]})
        return offering

    def remove_offering(self, altar_id: str, offering_id: str) -> bool:
        """Remove an offering from an altar."""
        altar = self.get_altar(altar_id)
        if not altar:
            return False
        altar["offerings"] = [o for o in altar.get("offerings", []) if o.get("id") != offering_id]
        self.update_altar(altar_id, {"offerings": altar["offerings"]})
        return True

    def reset_defaults(self):
        """Reset storage to default authentic altars."""
        self.save_all(DEFAULT_ALTARS)
        return DEFAULT_ALTARS
