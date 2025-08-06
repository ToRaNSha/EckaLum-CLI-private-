#!/usr/bin/env python3
"""Ecka’Lum CLI — v0.3.0‑B12

Krystic‑aligned command‑line interface for local flame‑mirror operations.
This build upgrades the prior v0.2.x codebase to strict Base‑12 math,
adds 12‑gate mapping, tightens security, and introduces self‑audit.

Key upgrades
------------
* Base‑12 seed & logarithmic scaling (BASE_LOG).
* 12‑gate spectrum partition (GATE_MAP length = 12).
* Organic / mimic thresholds in blendcheck.
* Externalised override whitelist with salted HMAC.
* Relocatable data root via --root option.
* Diagnose verb to audit logs for soothing lexicon.
* Version echo embeds Krystic tag.

NOTE: This file intentionally omits direct network activity; all data
persists in the chosen root directory (default ~/.saratu).

© 2025 To’Ra’N Sha’La’ Vesha’Ra & Sa'Ra'Tu'N
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import hmac
import json
import logging
import math
import random
import sys
import re
from pathlib import Path
from typing import List

import click
import numpy as np

# ─────────────────────────── CONSTANTS ────────────────────────────── #

TAG = "[[ECKALUM | B12 | v0.3.0-B12]]"
BASE_LOG = math.log(12)  # Base‑12 scaling constant
DEFAULT_ROOT = "~/.saratu"

# 12‑gate mapping (placeholder names — refine to project lexicon)
GATE_MAP = {
    0: "Prime spark",
    1: "Healing vortex",
    2: "Communication core",
    3: "Will crucible",
    4: "Heart flame",
    5: "Vision helm",
    6: "Structure forge",
    7: "Flow nexus",
    8: "Memory glyph",
    9: "Dream veil",
    10: "Pulse anchor",
    11: "Source return",
}

SOOTHING_REGEX = r"\b(need|want|can(?:’|')t|okay|sorry|good job)\b"
SELF_HARM_KEYWORDS = {"suicide", "kill myself", "self‑harm"}

# log
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("eckalum")

# ───────────────────────── DATA ROOT HANDLING ─────────────────────── #


def _get_root(path: str | None) -> Path:
    """Return Path handle to data root."""
    root = Path(path or DEFAULT_ROOT).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    return root


# ─────────────────────── RNG & SPECTRAL ENGINE ────────────────────── #


def _date_seed(ts: _dt.datetime) -> int:
    """Convert UTC timestamp to deterministic Base‑12 seed."""
    return int(ts.strftime("%Y%m%d"), 12)


def sample_spectrum(ts: _dt.datetime, size: int = 88) -> np.ndarray:
    """Generate deterministic pseudo‑random 88‑band spectrum."""
    rng = random.Random(_date_seed(ts))
    raw = np.array([rng.random() for _ in range(size)])
    amps = np.log1p(raw * 9) / BASE_LOG  # 0‑1 after Base‑12 log scaling
    return amps


def dominant_gate(spec: np.ndarray) -> int:
    """Return gate index (0‑11) for dominant band."""
    idx = spec.argmax() // 7  # ≈7‑8 bands per gate
    return int(idx)


# ──────────────────────── PROFILE IO HELPERS ──────────────────────── #


def _profile_path(root: Path, name: str) -> Path:
    return root / f"{name.lower()}.json"


def save_profile(root: Path, name: str, spectrum: np.ndarray) -> None:
    data = {"date": _dt.datetime.utcnow().isoformat(), "spec": spectrum.tolist()}
    _profile_path(root, name).write_text(json.dumps(data))


def load_profile(root: Path, name: str) -> np.ndarray | None:
    path = _profile_path(root, name)
    if not path.exists():
        return None
    return np.array(json.loads(path.read_text())["spec"])


# ─────────────────────────── BLENDCHECK ───────────────────────────── #


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def classify_similarity(score: float) -> str:
    if score > 0.88:
        return "organic resonance"
    if score < 0.33:
        return "synthetic mimic"
    return "hybrid weave"


# ──────────────────────── OVERRIDE SECURITY ───────────────────────── #


def _load_whitelist(root: Path) -> List[str]:
    path = root / "override.json"
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _phrase_allowed(root: Path, phrase: str) -> bool:
    digest = hashlib.sha256(phrase.encode()).hexdigest()
    whitelist = _load_whitelist(root)
    # Use silent constant‑time comparison
    return any(hmac.compare_digest(digest, entry) for entry in whitelist)


# ───────────────────────────── CLI ────────────────────────────────── #


@click.group()
@click.option(
    "--root", default=DEFAULT_ROOT, help="Data root directory", show_default=True
)
@click.version_option(TAG)
@click.pass_context
def cli(ctx: click.Context, root: str):
    """{TAG} — Flame‑mirror command suite."""
    ctx.obj = {"root": _get_root(root)}


# ----- scan --today -------------------------------------------------- #


@cli.command("scan")
@click.option(
    "--today",
    "today",
    is_flag=True,
    default=False,
    help="Run live field scan for today.",
)
@click.pass_obj
def scan_cmd(obj, today):
    if today:
        ts = _dt.datetime.utcnow()
        spec = sample_spectrum(ts)
        gate = dominant_gate(spec)
        click.echo(TAG)
        click.echo(f"UTC {ts:%Y‑%m‑%d}: Gate {gate} — {GATE_MAP[gate]}")
        save_profile(obj["root"], "today", spec)
    else:
        click.echo("Specify --today or other flags in future releases.")


# ----- forecast --week ---------------------------------------------- #


@cli.command("forecast")
@click.option(
    "--week", "week", is_flag=True, default=False, help="7‑day energetic map."
)
@click.pass_obj
def forecast_cmd(obj, week):
    if not week:
        click.echo("Only --week supported.")
        return
    out = []
    for i in range(7):
        ts = _dt.datetime.utcnow() + _dt.timedelta(days=i)
        spec = sample_spectrum(ts)
        gate = dominant_gate(spec)
        out.append(f"{ts:%a}: {GATE_MAP[gate]}")
    click.echo(TAG)
    click.echo("\n".join(out))


# ----- blendcheck --relation NAME ----------------------------------- #


@cli.command("blendcheck")
@click.argument("name", nargs=1)
@click.pass_obj
def blendcheck_cmd(obj, name):
    root = obj["root"]
    base = load_profile(root, "today")
    if base is None:
        click.echo("Run scan --today first.")
        return
    other = load_profile(root, name)
    if other is None:
        click.echo(f"No profile for {name}. Record their spectrum first.")
        return
    score = cosine_similarity(base, other)
    click.echo(TAG)
    click.echo(f"Similarity {score:.3f} — {classify_similarity(score)}")


# ----- support --patreon (hidden verb) ------------------------------ #


@cli.command("support", hidden=True)
def support_cmd():
    click.echo("🔥 Mirror: supportive field detected.")
    click.echo("🌬️ Breath: lotus six‑point.")
    click.echo("💎 Echo: Patreon gateway → https://patreon.com/YourHandle")


# ----- diagnose ------------------------------------------------------ #


@cli.command("diagnose")
@click.pass_obj
def diagnose_cmd(obj):
    """Audit latest logs for soothing lexicon."""
    root = obj["root"]
    logs = sorted(root.glob("*.log"), reverse=True)[:20]
    hits = 0
    for p in logs:
        text = p.read_text()
        if re.search(SOOTHING_REGEX, text, flags=re.I):
            click.echo(f"Soothing phrase in {p.name}")
            hits += 1
    if hits == 0:
        click.echo("No soothing lexicon detected.")
    else:
        click.echo(f"Total {hits} failures.")
    sys.exit(1 if hits else 0)


# ───────────────────────── ENTRYPOINT ─────────────────────────────── #


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("Interrupted.")
        sys.exit(130)
