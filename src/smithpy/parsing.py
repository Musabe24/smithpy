"""Utility parsing helpers for Smith chart components."""
from __future__ import annotations

import re


PREFIXES = {
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "f": 1e-15,
    "m": 1e-3,
    "": 1.0,
}


def parse_lc_value(text: str) -> float:
    """Parse a value like ``"10 nH"`` or ``"50 uF"``.

    Parameters
    ----------
    text:
        Value string with optional SI prefix and unit (H or F).

    Returns
    -------
    float
        Numeric value in base SI units.
    """
    if not text:
        raise ValueError("empty value")
    text = text.strip()
    m = re.match(r"([0-9.]+)\s*([pnufm]?)[HhFf]", text)
    if not m:
        raise ValueError("invalid format")
    num = float(m.group(1))
    prefix = m.group(2).lower()
    return num * PREFIXES[prefix]


def parse_length(value: str, mode: str) -> tuple[float, str]:
    """Return length in degrees and a display string.

    Parameters
    ----------
    value:
        Input length value expressed either in degrees or wavelength
        fractions depending on ``mode``.
    mode:
        Either ``"deg"`` for degrees or ``"lambda"`` for a fraction of
        a wavelength.
    """
    value = value.strip().replace("°", "").replace("\u03bb", "")
    if mode == "deg":
        deg = float(value)
        return deg, f"{deg}\u00b0"
    frac = float(value)
    deg = frac * 360.0
    return deg, f"{frac} \u03bb"


def parse_ohm_value(text: str) -> float:
    """Parse a resistor value in ohms."""
    if not text:
        raise ValueError("empty value")
    text = text.strip().lower()
    m = re.match(r"([0-9.]+)", text)
    if not m:
        raise ValueError("invalid format")
    return float(m.group(1))


def parse_complex_impedance(text: str) -> complex:
    """Parse a complex impedance string like ``"50+30j"``."""
    if not text:
        raise ValueError("empty load impedance")
    t = text.replace(" ", "")
    try:
        return complex(t)
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError("invalid complex impedance") from exc
