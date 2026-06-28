"""
math_solver.py - Symbolic and numerical mathematics engine.

Uses SymPy to detect, parse, and evaluate mathematical expressions and
equations entered by the user before they are sent to the LLM.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)


# ── Transformations used when parsing user input ───────────────────────────────

PARSE_TRANSFORMATIONS = (
    standard_transformations
    + (implicit_multiplication_application, convert_xor)
)

# Common single-letter variable names to treat as symbols
_COMMON_SYMBOLS = "x y z a b c n t"


@dataclass
class SolverResult:
    """Holds the outcome of a math-solver attempt."""

    success: bool
    original: str          # The original user input
    result: str            # Human-readable result string
    latex: Optional[str] = None    # LaTeX representation (if available)
    error: Optional[str] = None    # Error message on failure


# ── Public helpers ─────────────────────────────────────────────────────────────

def try_solve(user_input: str) -> Optional[SolverResult]:
    """
    Attempt to detect and solve a mathematical expression or equation.

    Returns a SolverResult on success, or None if the input does not look
    like something SymPy should handle (so the LLM handles it directly).
    """
    text = user_input.strip()

    # ── 1. Equation (contains '=') ─────────────────────────────────────────
    if "=" in text and _looks_like_equation(text):
        return _solve_equation(text)

    # ── 2. Pure expression / formula ──────────────────────────────────────
    if _looks_like_expression(text):
        return _evaluate_expression(text)

    return None  # Let the LLM handle it


# ── Internal helpers ───────────────────────────────────────────────────────────

def _looks_like_equation(text: str) -> bool:
    """Return True if the text resembles a mathematical equation."""
    # Must have exactly one '=' not preceded by '!' '<' '>'
    eq_positions = [i for i, c in enumerate(text) if c == "="]
    if len(eq_positions) != 1:
        return False
    idx = eq_positions[0]
    if idx > 0 and text[idx - 1] in "!<>":
        return False
    # Both sides should contain digits or letters
    lhs, rhs = text[:idx].strip(), text[idx + 1:].strip()
    return bool(re.search(r"[\d\w]", lhs)) and bool(re.search(r"[\d\w]", rhs))


def _looks_like_expression(text: str) -> bool:
    """Return True if text looks like a mathematical expression."""
    math_pattern = re.compile(
        r"(?:"
        r"\d"                          # contains a digit
        r"|sqrt\s*\("                  # sqrt(
        r"|log\s*\("                   # log(
        r"|sin\s*\(|cos\s*\(|tan\s*\(" # trig
        r"|exp\s*\("                   # exp(
        r"|pi\b|e\b"                   # constants
        r"|[\+\-\*\/\^\(\)]"           # operators / brackets
        r")",
        re.IGNORECASE,
    )
    return bool(math_pattern.search(text))


def _local_namespace() -> dict:
    """Build a SymPy-enriched namespace for parse_expr."""
    symbols = sp.symbols(_COMMON_SYMBOLS)
    ns = {s.name: s for s in symbols}
    ns.update(
        {
            "sqrt": sp.sqrt,
            "log": sp.log,
            "ln": sp.ln,
            "exp": sp.exp,
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "asin": sp.asin,
            "acos": sp.acos,
            "atan": sp.atan,
            "pi": sp.pi,
            "e": sp.E,
            "oo": sp.oo,
            "abs": sp.Abs,
            "factorial": sp.factorial,
            "diff": sp.diff,
            "integrate": sp.integrate,
            "limit": sp.limit,
        }
    )
    return ns


def _evaluate_expression(text: str) -> SolverResult:
    """Parse and simplify / evaluate a mathematical expression."""
    # Normalise: replace ^ with ** handled by convert_xor transformation
    normalised = text.strip()

    try:
        expr = parse_expr(
            normalised,
            local_dict=_local_namespace(),
            transformations=PARSE_TRANSFORMATIONS,
        )
    except Exception as exc:
        return SolverResult(
            success=False,
            original=text,
            result="",
            error=f"Could not parse expression: {exc}",
        )

    try:
        simplified = sp.simplify(expr)

        # If the expression is purely numerical, also give a decimal value
        if simplified.is_number:
            numeric = float(simplified.evalf(15))
            # Show integer form when exact
            if numeric == int(numeric):
                result_str = str(int(numeric))
            else:
                result_str = f"{simplified} ≈ {numeric:.6g}"
        else:
            result_str = str(simplified)

        return SolverResult(
            success=True,
            original=text,
            result=result_str,
            latex=sp.latex(simplified),
        )

    except Exception as exc:
        return SolverResult(
            success=False,
            original=text,
            result="",
            error=f"Could not evaluate expression: {exc}",
        )


def _solve_equation(text: str) -> SolverResult:
    """Solve an equation (supports polynomial and simple transcendental forms)."""
    eq_idx = text.index("=")
    lhs_str = text[:eq_idx].strip()
    rhs_str = text[eq_idx + 1:].strip()
    ns = _local_namespace()

    try:
        lhs = parse_expr(lhs_str, local_dict=ns, transformations=PARSE_TRANSFORMATIONS)
        rhs = parse_expr(rhs_str, local_dict=ns, transformations=PARSE_TRANSFORMATIONS)
    except Exception as exc:
        return SolverResult(
            success=False,
            original=text,
            result="",
            error=f"Could not parse equation sides: {exc}",
        )

    # Determine the free symbols to solve for
    free = lhs.free_symbols | rhs.free_symbols
    if not free:
        # Both sides are constants – check equality
        diff = sp.simplify(lhs - rhs)
        truth = "True (identity)" if diff == 0 else "False (no solution)"
        return SolverResult(success=True, original=text, result=truth)

    # Prefer 'x', otherwise pick alphabetically first
    solve_for = (
        sp.Symbol("x") if sp.Symbol("x") in free else sorted(free, key=str)[0]
    )

    try:
        solutions = sp.solve(lhs - rhs, solve_for)
    except NotImplementedError:
        return SolverResult(
            success=False,
            original=text,
            result="",
            error="SymPy could not solve this equation analytically.",
        )

    if not solutions:
        result_str = "No real solutions found."
    elif len(solutions) == 1:
        sol = solutions[0]
        numeric = _numeric_str(sol)
        result_str = f"{solve_for} = {sol}{numeric}"
    else:
        parts = []
        for sol in solutions:
            numeric = _numeric_str(sol)
            parts.append(f"{solve_for} = {sol}{numeric}")
        result_str = ",  ".join(parts)

    latex = ", ".join(sp.latex(s) for s in solutions)
    return SolverResult(success=True, original=text, result=result_str, latex=latex)


def _numeric_str(expr: sp.Expr) -> str:
    """Return a decimal approximation string if the expression is not an integer."""
    try:
        val = complex(expr.evalf())
        if val.imag == 0:
            real = val.real
            if real == round(real):
                return ""          # already exact integer
            return f" ≈ {real:.6g}"
        return f" ≈ {val.real:.4g} + {val.imag:.4g}i"
    except Exception:
        return ""
