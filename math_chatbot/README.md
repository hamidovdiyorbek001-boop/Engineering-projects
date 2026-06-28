# MathBot — AI Mathematics Tutor 🤖📐

A command-line mathematics tutoring chatbot powered by **OpenAI GPT** for
natural-language explanations and **SymPy** for exact symbolic computation.
Built as a portfolio project demonstrating Python software design, AI API
integration, and mathematical computing.

---

## ✨ Features

| Feature | Detail |
|---|---|
| **Arithmetic** | BODMAS/PEMDAS, fractions, percentages, large integers |
| **Algebra** | Polynomial equations, systems, factorisation, inequalities |
| **Geometry** | Area, perimeter, volume formulas; coordinate geometry |
| **Trigonometry** | sin/cos/tan, inverse functions, identities, unit circle |
| **Calculus** | Limits, derivatives, integrals (basic) |
| **Exact computation** | SymPy solves/simplifies before calling the LLM |
| **Step-by-step explanations** | GPT explains *how* to reach the answer |
| **Conversation history** | Context carried across multi-turn sessions |
| **Graceful error handling** | Invalid inputs caught; API errors surfaced cleanly |
| **Clean CLI** | ANSI colours, word-wrap, special commands |

---

## 📁 Project Structure

```
math_chatbot/
├── main.py           # CLI entry point and user interaction loop
├── chatbot.py        # Conversation engine + OpenAI API integration
├── math_solver.py    # SymPy-powered expression/equation solver
├── config.py         # All configuration and constants (env-backed)
├── requirements.txt  # Python dependencies
├── .env.example      # Template for environment variables
├── .gitignore        # Files excluded from version control
└── README.md         # This file
```

---

## 🛠️ Technologies Used

- **Python 3.11+** — language runtime
- **OpenAI Python SDK (`openai`)** — GPT-4o-mini for step-by-step explanations
- **SymPy** — computer algebra system for exact symbolic maths
- **python-dotenv** — loads secrets from `.env` without hardcoding

---

## ⚡ Quick Start

### 1 — Clone the repository

```bash
git clone https://github.com/<your-username>/math_chatbot.git
cd math_chatbot
```

### 2 — Create and activate a virtual environment

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Configure your API key

```bash
cp .env.example .env
# Open .env in your editor and paste your OpenAI API key
```

Your `.env` file should look like:

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
MAX_TOKENS=1024
TEMPERATURE=0.2
```

> Get your key at <https://platform.openai.com/api-keys>

### 5 — Run MathBot

```bash
python main.py
```

---

## 💬 Usage Examples

```
══════════════════════════════════════════════════════════════════════
              MathBot — AI Mathematics Tutor
                           v1.0.0
══════════════════════════════════════════════════════════════════════
  Type a math question or expression to get started.
  Special commands: /help  /reset  /history  /exit
──────────────────────────────────────────────────────────────────────

You > 2 + 5 * 3

MathBot >
  Great question about order of operations! The expression
  2 + 5 * 3 evaluates to **17**.

  Step 1 — Identify operator precedence (BODMAS/PEMDAS):
    Multiplication comes before addition.
  Step 2 — Multiply first:  5 × 3 = 15
  Step 3 — Then add:        2 + 15 = 17

──────────────────────────────────────────────────────────────────────

You > x^2 + 5x + 6 = 0

MathBot >
  This is a quadratic equation. SymPy found the solutions:
  x = -2  and  x = -3.

  Step 1 — Write in standard form:  x² + 5x + 6 = 0
  Step 2 — Find two numbers that multiply to 6 and add to 5: (2, 3)
  Step 3 — Factor:  (x + 2)(x + 3) = 0
  Step 4 — Zero-product property:  x = -2  or  x = -3  ✓

──────────────────────────────────────────────────────────────────────

You > sqrt(144)

MathBot >
  √144 = 12.

  Explanation: 144 = 12² because 12 × 12 = 144.
  Taking the principal (positive) square root gives 12.

──────────────────────────────────────────────────────────────────────

You > What is the derivative of sin(x^2)?

MathBot >
  Using the chain rule:

  Step 1 — Let u = x², so f(u) = sin(u).
  Step 2 — Outer derivative:  d/du[sin(u)] = cos(u)
  Step 3 — Inner derivative:  du/dx = 2x
  Step 4 — Multiply:  d/dx[sin(x²)] = cos(x²) · 2x = 2x·cos(x²)

──────────────────────────────────────────────────────────────────────

You > /history
──────────────────────────────────────────────────────────────────────
Session History
  [1] User: 2 + 5 * 3…
  [1] Assistant: Great question about order of operations!…
  [2] User: x^2 + 5x + 6 = 0…
  [2] Assistant: This is a quadratic equation…
──────────────────────────────────────────────────────────────────────

You > /exit
Goodbye! Keep learning! 👋
```

---

## 🔧 Special Commands

| Command | Action |
|---|---|
| `/help` | Show command list and example inputs |
| `/reset` | Clear conversation history |
| `/history` | Display the current session transcript |
| `/exit` | Quit MathBot |

---

## 🏗️ Architecture Overview

```
User Input
    │
    ▼
main.py  ──── special commands (/help, /reset, …)
    │
    ▼ normal input
chatbot.py  (MathChatbot.chat)
    │
    ├──► math_solver.py (SymPy)
    │         │  exact result
    │         ▼
    │    enriched message ("[COMPUTED RESULT]: …")
    │
    └──► OpenAI API  →  step-by-step explanation
              │
              ▼
         Reply displayed in CLI
```

---

## 🔑 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI secret key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model to use |
| `MAX_TOKENS` | `1024` | Max reply length |
| `TEMPERATURE` | `0.2` | Lower = more deterministic |

---

## 🧪 Running the Solver Standalone

```python
from math_solver import try_solve

r = try_solve("x^2 - 9 = 0")
print(r.result)   # x = -3,  x = 3

r = try_solve("sqrt(256)")
print(r.result)   # 16

r = try_solve("sin(pi/6)")
print(r.result)   # 1/2
```

---

## 📄 License

MIT — free for academic and personal use.

---

## 👤 Author

Built as a university portfolio project demonstrating:
- Clean Python project structure
- AI API integration (OpenAI)
- Symbolic computation (SymPy)
- Software design principles (separation of concerns, PEP 8)
