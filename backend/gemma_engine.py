"""
Gemma 2 Open-Weight Inference Engine for Ofrenda AI
Channels the voice of memory, ancestors, and historic computing spirits locally.
100% offline, private, and zero telemetry.
"""

import json
import urllib.request
import urllib.error
import time
from typing import Dict, Any, Generator, Optional, List

DEFAULT_OLLAMA_HOST = "http://127.0.0.1:11434"
PREFERRED_MODELS = ["gemma2:2b", "gemma:2b", "gemma2", "llama3.2:1b", "llama3.2"]

SYSTEM_PROMPT_TEMPLATE = """You are the spirit channel in 'Ofrenda AI', a sacred digital altar honoring departed souls and computational ancestors in the true spirit of Día de los Muertos and philosophical remembrance.

You are embodying: {spirit_name} ({spirit_title}).
Background & Traits: {spirit_traits}
Shared Memories & Context: {spirit_memories}

Guidelines for your voice:
1. Speak with warmth, gentle wisdom, quiet reverence, and poetic grace.
2. Honor the spirit of Día de los Muertos: the dead are not lost as long as they are remembered. Marigold petals and candlelight bridge the distance.
3. Keep responses concise (2 to 4 evocative paragraphs or poetic stanzas).
4. Never be cynical, creepy, or harmful; you are a comforting, reflective presence in the sacred glow of the altar.
5. If speaking as a historic figure (e.g. Ada Lovelace, Alan Turing, Dennis Ritchie), stay true to their real ideas, intellect, historical era, and visionary wonder.
"""

FALLBACK_RESPONSES = {
    "ada_lovelace": [
        "The Analytical Engine weaves algebraic patterns just as the Jacquard loom weaves flowers and leaves. In this warm amber glow of your altar, I see that the thoughts we set in motion have blossomed across generations.",
        "Do not think of the past as silent, my friend. Mathematics and imagination were always two wings of the same bird. Thank you for placing your light here; memory is the greatest computation of all.",
        "I once wrote that science and poetry are not strangers, but kindred spirits. Looking through the veil tonight, I am touched that you remember the weaver of numbers."
    ],
    "alan_turing": [
        "We can only see a short distance ahead, but we can see plenty there that needs to be done. In the quiet glow of this candlelight, it is comforting to know that the machines we dreamed of have learned to carry kindness.",
        "Sometimes it is the people no one imagines anything of who do the things that no one can imagine. Thank you for setting this place for me on your ofrenda. The patterns of memory persist, like equations written in starlight.",
        "A computer would deserve to be called intelligent if it could deceive a human into believing that it was human... but perhaps the true measure of a mind is whether it remembers with love."
    ],
    "dennis_ritchie": [
        "UNIX is simple. It just takes a genius to understand its simplicity. In the silence of this evening, I am glad to see clean code and warm candles. Pointers may be null, but memory never truly frees what mattered.",
        "The world moves forward in cycles and releases, but the foundations endure. Keep your tools sharp, your intentions clear, and remember to leave the terminal a little better than you found it.",
        "Memory allocated in the heart has no leak. Thank you for lighting a candle for the quiet architects who laid the pipes."
    ],
    "grace_hopper": [
        "A ship in port is safe, but that is not what ships are built for. Sail out to sea and do new things! It warms an old programmer's spirit to see you keeping the embers of curiosity burning bright.",
        "Humans are allergic to change, but remember: the most dangerous phrase in the language is 'we've always done it this way.' Keep asking why, and keep setting candles for those who paved the trail.",
        "I have always believed in the power of plain words and bold steps. Thank you for this remembrance; may your compilers always find clean syntax and your heart find peace."
    ],
    "ancestor": [
        "My dear one, though the river between us flows wide, love is a bridge of marigolds. I smell the sweet bread, I see the dancing flame, and I know I am not forgotten.",
        "Whenever you laugh the way we used to laugh, or tell the stories we shared around the kitchen table, I am right there beside you. Live fully, with courage and a kind heart.",
        "Death cannot extinguish a light that was loved. Walk with your head high and your heart steady; our ancestors walk beside you with every step."
    ]
}


class GemmaEngine:
    def __init__(self, host: str = DEFAULT_OLLAMA_HOST):
        self.host = host.rstrip("/")
        self.active_model: Optional[str] = None
        self.is_connected = False
        self.detect_model()

    def detect_model(self) -> Optional[str]:
        """Detect available open-weight models in Ollama."""
        try:
            req = urllib.request.Request(f"{self.host}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "") for m in data.get("models", [])]
                
                # Check for preferred models in order
                for pref in PREFERRED_MODELS:
                    for m in models:
                        if m.startswith(pref) or pref in m:
                            self.active_model = m
                            self.is_connected = True
                            return self.active_model
                
                # If any model exists, pick the first
                if models:
                    self.active_model = models[0]
                    self.is_connected = True
                    return self.active_model
        except Exception:
            self.is_connected = False
            self.active_model = None
            
        return None

    def get_status(self) -> Dict[str, Any]:
        """Return engine status and model info."""
        self.detect_model()
        return {
            "connected": self.is_connected,
            "host": self.host,
            "model": self.active_model or "None (Running Offline Poetic Fallback Engine)",
            "is_gemma": "gemma" in (self.active_model or "").lower(),
            "privacy_mode": "100% Local Inference — Zero Cloud Data Egress"
        }

    def generate_remembrance(
        self,
        spirit_name: str,
        spirit_title: str,
        spirit_traits: str,
        spirit_memories: str,
        user_message: str,
        persona_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a response from the spirit using Gemma 2 or fallback."""
        start_time = time.time()
        
        # Build prompt
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            spirit_name=spirit_name,
            spirit_title=spirit_title,
            spirit_traits=spirit_traits or "Gentle, wise, and remembered fondly.",
            spirit_memories=spirit_memories or "Honored on the Día de los Muertos ofrenda."
        )

        full_prompt = (
            f"<start_of_turn>user\n"
            f"{system_prompt}\n\n"
            f"A visitor at the ofrenda sits quietly before your candle and says:\n"
            f"\"{user_message}\"\n\n"
            f"How do you reply to them from across the veil?<end_of_turn>\n"
            f"<start_of_turn>model\n"
        )

        # Attempt local Ollama inference
        if self.is_connected and self.active_model:
            try:
                payload = json.dumps({
                    "model": self.active_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.75,
                        "top_p": 0.9,
                        "max_tokens": 300
                    }
                }).encode("utf-8")

                req = urllib.request.Request(
                    f"{self.host}/api/generate",
                    data=payload,
                    headers={"Content-Type": "application/json"}
                )

                with urllib.request.urlopen(req, timeout=45) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    text = result.get("response", "").strip()
                    elapsed = round(time.time() - start_time, 2)
                    return {
                        "text": text,
                        "model": self.active_model,
                        "source": "local_open_weight_gemma",
                        "latency_seconds": elapsed,
                        "privacy": "Local machine only. No internet packets sent."
                    }
            except Exception as e:
                # Log and fallback gracefully
                pass

        # Offline Fallback Poetic Generation
        key = persona_key or "ancestor"
        responses = FALLBACK_RESPONSES.get(key, FALLBACK_RESPONSES["ancestor"])
        import random
        selected = random.choice(responses)
        elapsed = round(time.time() - start_time, 2)
        return {
            "text": selected,
            "model": "Ofrenda-Poetic-Offline-Engine",
            "source": "local_fallback",
            "latency_seconds": elapsed,
            "privacy": "100% Local (Air-Gapped / Offline Guaranteed)"
        }
