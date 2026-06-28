"""
main.py - Command-line interface for MathBot.

Run with:
    python main.py

Special commands (case-insensitive):
    /help    – Show available commands
    /reset   – Clear conversation history
    /history – Display the current session history
    /exit    – Quit MathBot
"""

from __future__ import annotations

import sys
import textwrap

import config
from chatbot import MathChatbot

# ── ANSI colour helpers ────────────────────────────────────────────────────────

BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
RESET  = "\033[0m"

W = config.TERMINAL_WIDTH


def _banner() -> str:
    """Return the startup banner string."""
    return (
        f"\n{CYAN}{'═' * W}{RESET}\n"
        f"{BOLD}{CYAN}{'MathBot — AI Mathematics Tutor':^{W}}{RESET}\n"
        f"{CYAN}{'v' + config.APP_VERSION:^{W}}{RESET}\n"
        f"{CYAN}{'═' * W}{RESET}\n"
        f"  Type a math question or expression to get started.\n"
        f"  Special commands: /help  /reset  /history  /exit\n"
        f"{CYAN}{'─' * W}{RESET}\n"
    )


def _help_text() -> str:
    return (
        f"\n{YELLOW}{'─' * W}{RESET}\n"
        f"{BOLD}Available commands{RESET}\n"
        f"  /help     – Show this message\n"
        f"  /reset    – Start a new conversation\n"
        f"  /history  – Display session history\n"
        f"  /exit     – Quit MathBot\n\n"
        f"{BOLD}Example inputs{RESET}\n"
        f"  2 + 5 * 3\n"
        f"  sqrt(144)\n"
        f"  x^2 + 5x + 6 = 0\n"
        f"  What is the derivative of sin(x)?\n"
        f"  Explain the Pythagorean theorem with an example.\n"
        f"  sin(pi/4)\n"
        f"{YELLOW}{'─' * W}{RESET}\n"
    )


def _wrap_reply(text: str) -> str:
    """Word-wrap the assistant reply for comfortable terminal reading."""
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if paragraph.strip() == "":
            lines.append("")
        else:
            wrapped = textwrap.fill(paragraph, width=W - 4, initial_indent="  ",
                                    subsequent_indent="  ")
            lines.append(wrapped)
    return "\n".join(lines)


# ── Main loop ──────────────────────────────────────────────────────────────────

def main() -> None:
    print(_banner())

    try:
        bot = MathChatbot()
    except EnvironmentError as exc:
        print(f"{RED}[Error] {exc}{RESET}")
        sys.exit(1)

    while True:
        # ── Prompt ────────────────────────────────────────────────────────────
        try:
            raw = input(f"{GREEN}You >{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{CYAN}Goodbye! Keep learning! 👋{RESET}\n")
            sys.exit(0)

        if not raw:
            continue

        command = raw.lower()

        # ── Special commands ──────────────────────────────────────────────────
        if command in ("/exit", "/quit", "exit", "quit"):
            print(f"\n{CYAN}Goodbye! Keep learning! 👋{RESET}\n")
            sys.exit(0)

        if command == "/help":
            print(_help_text())
            continue

        if command == "/reset":
            bot.reset()
            print(f"\n{YELLOW}  Conversation cleared. Starting fresh!{RESET}\n")
            continue

        if command == "/history":
            print(f"\n{YELLOW}{'─' * W}{RESET}")
            print(f"{BOLD}Session History{RESET}")
            print(bot.history_summary())
            print(f"{YELLOW}{'─' * W}{RESET}\n")
            continue

        # ── Normal question ───────────────────────────────────────────────────
        print(f"{CYAN}  Thinking…{RESET}", end="\r", flush=True)
        reply = bot.chat(raw)

        print(f"\n{BOLD}{CYAN}MathBot >{RESET}")
        print(_wrap_reply(reply))
        print(f"{CYAN}{'─' * W}{RESET}\n")


if __name__ == "__main__":
    main()
