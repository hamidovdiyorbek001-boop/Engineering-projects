"""
config.py - Configuration settings for the Mathematics Chatbot.

Loads environment variables and defines constants used throughout the project.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ── API Configuration ──────────────────────────────────────────────────────────

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1024"))
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.2"))


# ── Chatbot Settings ───────────────────────────────────────────────────────────

APP_NAME: str = "MathBot"
APP_VERSION: str = "1.0.0"

# Maximum conversation turns kept in history (each turn = user + assistant)
MAX_HISTORY_TURNS: int = 20

# CLI display width
TERMINAL_WIDTH: int = 70


# ── System Prompt ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT: str = """You are MathBot, an expert mathematics tutor designed
to help university students understand mathematical concepts and solve problems.

Your capabilities include:
- Arithmetic (operations, fractions, percentages, order of operations)
- Algebra (equations, inequalities, polynomials, systems of equations)
- Geometry (shapes, area, perimeter, volume, angles, coordinate geometry)
- Trigonometry (sin/cos/tan, identities, inverse functions, unit circle)
- Calculus (limits, derivatives, integrals, basic differential equations)

Guidelines:
1. When a symbolic or numerical result is provided in the user's message
   (prefixed with [COMPUTED RESULT]), use it as the ground truth answer
   and focus your explanation on *how* to arrive at that result step by step.
2. Always explain the reasoning and method, not just the answer.
3. Use clear mathematical notation. For inline math use backticks: `x^2`.
4. Break complex problems into numbered steps.
5. If a question is outside mathematics, politely redirect the conversation.
6. Be encouraging and pedagogically sound.
"""
