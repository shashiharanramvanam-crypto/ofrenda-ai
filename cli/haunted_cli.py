"""
Haunted Terminal / NecroCLI & Séance Companion
A possessed terminal interface for Ofrenda AI.
Whispers poetic remembrances from Gemma 2 locally in your shell.
"""

import sys
import time
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from gemma_engine import GemmaEngine
from altar_store import AltarStore

# ANSI Color codes
AMBER = "\033[38;5;214m"
GOLD = "\033[38;5;220m"
PURPLE = "\033[38;5;135m"
CYAN = "\033[38;5;51m"
GREEN = "\033[38;5;48m"
RED = "\033[38;5;196m"
GRAY = "\033[38;5;244m"
BOLD = "\033[1m"
RESET = "\033[0m"

SKULL_ASCII = f"""
{GOLD}
       .---.
      /     \\
     | () () |       {AMBER}OFRENDA AI : GHOST IN THE MACHINE{GOLD}
      \\  _  /        {PURPLE}A Local Séance & Terminal Altar{GOLD}
       `---`         {GRAY}Powered by Gemma 2B Open Weights{RESET}
"""

def typewriter(text: str, delay: float = 0.015, color: str = AMBER):
    sys.stdout.write(color)
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(RESET + "\n")

def main():
    os.system("") # Enable ANSI on Windows console
    print(SKULL_ASCII)

    engine = GemmaEngine()
    store = AltarStore()

    status = engine.get_status()
    print(f"{GRAY}[Status: Model: {status['model']} | Connected: {status['connected']} | Mode: Offline/Private]{RESET}\n")

    current_altar = store.get_altar("ada-lovelace")

    print(f"{AMBER}Current Spirit Altar:{RESET} {BOLD}{current_altar['name']}{RESET} ({current_altar['title']})")
    print(f"{GRAY}Type 'help' for commands, or speak your mind to commune across the veil.{RESET}\n")

    while True:
        try:
            prompt_str = f"{PURPLE}🕯️  [{current_altar['name']}]{RESET} > "
            user_input = input(prompt_str).strip()

            if not user_input:
                continue

            cmd_lower = user_input.lower()

            if cmd_lower in ["exit", "quit", "q"]:
                typewriter("The candle flames flicker low as the veil gently closes. Go in peace...", 0.02, GRAY)
                break

            elif cmd_lower == "help":
                print(f"""
{BOLD}Available Terminal Commands:{RESET}
  {GOLD}list{RESET}               - List all spirit altars
  {GOLD}select <id>{RESET}        - Commune with a specific altar (e.g. 'select alan-turing')
  {GOLD}candles{RESET}            - View and light/extinguish candles
  {GOLD}offerings{RESET}          - View sacred offerings placed on the altar
  {GOLD}haunt <command>{RESET}    - Possessed terminal: let the spirit critique a terminal command
  {GOLD}status{RESET}             - Display local Gemma engine & air-gap verification
  {GOLD}clear{RESET}              - Clear the terminal screen
  {GOLD}<any message>{RESET}      - Speak directly with the spirit
""")
            elif cmd_lower == "list":
                print(f"\n{BOLD}Sacred Altars in Local Memory:{RESET}")
                for a in store.load_all():
                    print(f"  {AMBER}✦ {a['id']:<18}{RESET} {a['name']:<24} {GRAY}({a['title']}){RESET}")
                print()

            elif cmd_lower.startswith("select "):
                target_id = user_input.split(" ", 1)[1].strip()
                altar = store.get_altar(target_id)
                if altar:
                    current_altar = altar
                    print(f"\n{GOLD}The cempasúchil petals stir... You are now before the altar of {BOLD}{altar['name']}{RESET} ({altar['years']}).\n")
                else:
                    print(f"{RED}Altar '{target_id}' not found. Type 'list' to see available altars.{RESET}")

            elif cmd_lower == "candles":
                print(f"\n{BOLD}Candles for {current_altar['name']}:{RESET}")
                for c in current_altar.get("candles", []):
                    icon = f"{GOLD}🔥 LIT{RESET}" if c.get("lit") else f"{GRAY}💨 EXTINGUISHED{RESET}"
                    print(f"  {icon} - {c.get('label')}")
                print()

            elif cmd_lower == "offerings":
                print(f"\n{BOLD}Offerings on {current_altar['name']}'s Altar:{RESET}")
                for o in current_altar.get("offerings", []):
                    print(f"  {PURPLE}[{o.get('tier', 'mid').upper()}]{RESET} {BOLD}{o.get('name')}{RESET}: {o.get('note')}")
                print()

            elif cmd_lower.startswith("haunt "):
                sh_cmd = user_input.split(" ", 1)[1].strip()
                typewriter(f"\n[The spirit observes you typing `{sh_cmd}` into the shell...]", 0.015, GRAY)
                query = f"I just ran the terminal command `{sh_cmd}` on my computer. In your distinctive voice and era, share a brief, poetic, or witty commentary on what this action means in the grand tapestry of human thought and computing."
                resp = engine.generate_remembrance(
                    spirit_name=current_altar['name'],
                    spirit_title=current_altar['title'],
                    spirit_traits=current_altar.get('traits', ''),
                    spirit_memories=current_altar.get('memories', ''),
                    user_message=query,
                    persona_key=current_altar.get('persona_key')
                )
                typewriter(f"\n\"{resp['text']}\"\n", 0.015, AMBER)

            elif cmd_lower == "status":
                s = engine.get_status()
                print(f"\n{BOLD}Engine Verification:{RESET}")
                print(f"  Host:         {s['host']}")
                print(f"  Model:        {s['model']}")
                print(f"  Connected:    {s['connected']}")
                print(f"  Privacy:      {GREEN}{s['privacy_mode']}{RESET}\n")

            elif cmd_lower == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                print(SKULL_ASCII)

            else:
                # Commune across the veil
                typewriter("\n[The amber flame flickers as your words reach across the veil...]", 0.015, GRAY)
                resp = engine.generate_remembrance(
                    spirit_name=current_altar['name'],
                    spirit_title=current_altar['title'],
                    spirit_traits=current_altar.get('traits', ''),
                    spirit_memories=current_altar.get('memories', ''),
                    user_message=user_input,
                    persona_key=current_altar.get('persona_key')
                )
                print(f"\n{AMBER}{BOLD}{current_altar['name']}:{RESET}")
                typewriter(f"{resp['text']}\n", 0.015, AMBER)
                print(f"{GRAY}[Inference latency: {resp['latency_seconds']}s | Engine: {resp['model']}]{RESET}\n")

        except (KeyboardInterrupt, EOFError):
            print(f"\n{GRAY}Closing the veil... Farewell.{RESET}")
            break

if __name__ == "__main__":
    main()
