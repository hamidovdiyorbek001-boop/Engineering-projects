"""
chatbot.py - Conversation engine for MathBot.

Manages the dialogue history, calls the math solver for precise computation,
and forwards questions (enriched with computed results) to the OpenAI API.
"""

from __future__ import annotations

import textwrap
from typing import Optional

from openai import OpenAI, OpenAIError

import config
from math_solver import try_solve, SolverResult


# ── Type alias ─────────────────────────────────────────────────────────────────

Message = dict[str, str]   # {"role": "...", "content": "..."}


class MathChatbot:
    """
    Orchestrates a mathematics tutoring session.

    Attributes
    ----------
    _client       : OpenAI API client
    _history      : List of conversation messages (system excluded from storage)
    _system_msg   : Fixed system prompt injected at the start of every request
    """

    def __init__(self) -> None:
        if not config.OPENAI_API_KEY:
            raise EnvironmentError(
                "OPENAI_API_KEY is not set. "
                "Create a .env file with your key (see README.md)."
            )

        self._client: OpenAI = OpenAI(api_key=config.OPENAI_API_KEY)
        self._history: list[Message] = []
        self._system_msg: Message = {
            "role": "system",
            "content": config.SYSTEM_PROMPT,
        }

    # ── Public interface ───────────────────────────────────────────────────────

    def chat(self, user_input: str) -> str:
        """
        Process one user turn and return the assistant's reply.

        Steps
        -----
        1. Run the local math solver on the raw input.
        2. If a result was computed, prepend it to the user message so the LLM
           can explain the verified answer.
        3. Append the (possibly enriched) message to history.
        4. Call the OpenAI API with the full conversation.
        5. Append the assistant reply to history and return it.
        """
        user_input = user_input.strip()
        solver_result: Optional[SolverResult] = try_solve(user_input)

        if solver_result and solver_result.success:
            enriched = (
                f"{user_input}\n\n"
                f"[COMPUTED RESULT by Python/SymPy]: {solver_result.result}"
            )
            user_msg: Message = {"role": "user", "content": enriched}
        else:
            user_msg = {"role": "user", "content": user_input}

        self._history.append(user_msg)
        self._trim_history()

        try:
            response = self._client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[self._system_msg] + self._history,
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE,
            )
            reply: str = response.choices[0].message.content.strip()
        except OpenAIError as exc:
            reply = f"[API Error] {exc}"

        self._history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self) -> None:
        """Clear conversation history (start a new session)."""
        self._history.clear()

    def history_summary(self) -> str:
        """Return a compact, numbered summary of conversation turns."""
        if not self._history:
            return "  (empty)"
        lines: list[str] = []
        turn = 1
        i = 0
        while i < len(self._history):
            msg = self._history[i]
            role = msg["role"].capitalize()
            # Truncate long messages for display
            snippet = textwrap.shorten(msg["content"], width=60, placeholder="…")
            lines.append(f"  [{turn}] {role}: {snippet}")
            if msg["role"] == "assistant":
                turn += 1
            i += 1
        return "\n".join(lines)

    # ── Private helpers ────────────────────────────────────────────────────────

    def _trim_history(self) -> None:
        """
        Keep the history within MAX_HISTORY_TURNS complete turns.
        One 'turn' = one user message + one assistant message (2 entries).
        """
        max_entries = config.MAX_HISTORY_TURNS * 2
        if len(self._history) > max_entries:
            self._history = self._history[-max_entries:]
