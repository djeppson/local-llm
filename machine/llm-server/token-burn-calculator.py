#!/usr/bin/env python3
"""Token burn & cost-per-million-tokens (CPT) calculator.

Usage:
    python3 token-burn-calculator.py                  # 600 M tok/mo (default)
    python3 token-burn-calculator.py 400,600,800      # one $/mo column per burn
    python3 token-burn-calculator.py 800 --input 0.9 --cache 0.9

Arguments / options:
    burn      household burn in millions of tokens per month; comma-separated for
              multiple columns (default: 600). Household = 2 users, ~2x per-person
              (~100-200 now -> 200-400 planned).
    --input F fraction of tokens that are input, agent skew (default 0.90)
    --cache F fraction of input tokens hitting the prompt prefix cache (default 0.85)

    Defaults calibrated 2026-11-20 from `opencode stats` ground truth:
      --input  0.90  recorded IF (input/(input+output)) is 88-95% across windows
                     on the HF/cloud-billed population; 97% (old default,
                     context-composition estimate) overstated input share and
                     understated cost. 0.90 is a ballpark midpoint — the billable
                     fraction falls to ~0.84-0.86 if reasoning tokens are billed
                     at the output rate (unconfirmed).
                     Range seen: 0.84 (HF 30d, reasoning billed) - 0.95 (life).
      --cache  0.85  validated: 83% (30d) / 85% (90d) / 88% (HF-only) / 70%
                     (lifetime, dragged by older pre-cache sessions). Recent
                     and HF-specific cluster around 85%; no change.

CPT math:
    no-cache  = in*IF + out*(1-IF)
    effective = in*IF*(1-HIT) + cache_rate*IF*HIT + out*(1-IF)
    $/mo      = CPT * burn

Local rows expose the 3-yr TCO components (capex, AppleCare+, electricity,
resale); gross $/mo is pre-resale, net $/mo is the
resale-credited range, and CPT uses the net midpoint over burn.
Edit the CLOUD / LOCAL / REFERENCE blocks below to reprice models.
"""

import argparse

# (name, input $/M, cache-read $/M or None, output $/M)
# List prices: DeepInfra/HF Inference, Nov 2026. Cache-read
# rates are set to match the effective CPTs (DeepSeek: 10% of
# input list price; Qwen-Coder-480B / GLM-5.2: flat $0.10/M). Edit here if
# you have different published DeepInfra cache prices.
CLOUD = [
    ("DeepSeek V4.1 Flash",              0.140, 0.014, 0.42),
    ("DeepSeek V4 Flash",                0.090, 0.009, 0.18),
    ("Qwen3-Coder-480B",                 0.300, 0.100, 1.00),
    ("GLM-5.2",                          0.560, 0.100, 1.80),
    ("Qwen3.8-27B",                      0.150, None,  1.88),
    ("Qwen3.6-27B (current local model)", 0.320, None,  3.20),
    ("Mistral Small 3.2 24B",            0.075, None,  0.20),
]
ROUTE = "HF -> DeepInfra"

# Local machines — 3-yr TCO components.
# Each row: (name, capex, applecare_3yr, electricity_3yr, resale_lo, resale_hi)
#   capex           : Apple list price. Ultra verified 2026-09-22 ($5,499);
#                    Max MBP corrected from the stale $3,300 to $3,799 — the 36 GB
#                    base ($2,499) is too small, 64 GB/1 TB is the real floor.
#                    2026-11-27: added M5 Max STUDIO 128 GB — the Studio Max ladder
#                    is 48 GB ($3,099) -> 128 GB ($5,399 / 1 TB, configurator check
#                    2026-11-07); no 64 GB Studio rung exists.
#   applecare_3yr   : AppleCare+ over the 3-yr window. Ultra = $185.
#                    Max rows ASSUME the same Mac Studio tier — adjust if you have it.
#   electricity_3yr : 3-yr electricity at ~8 h/day duty. Ultra = 9 W idle /
#                    385 W max ≈ $420. Max rows = ESTIMATED ~70% of Ultra
#                    from the lower TDP — adjust if you have actuals.
#   resale_lo/_hi   : absolute $ resale credit at 36 mo. Ultra ~40–45.5% of
#                    capex. Max rows = 40–50% of capex (M2 Ultra retained 58–70% at
#                    35 mo; M1 Ultra 41–53% at 50 mo; sell peer-to-peer —
#                    Apple Trade In pays 35–55% of market).
#   gross $/mo = (capex + applecare + electricity) / 36      — no resale credit.
#   net   $/mo = (capex + applecare + electricity - resale) / 36 — shown as range.
#   CPT (per burn) uses the net midpoint, consistent with the prior flat value.
LOCAL = [
    ("M5 Ultra 96 GB (local)", 5499, 185, 420, 2200, 2500),
    ("M5 Max Studio 128 GB (local)", 5399, 185, 300, 2160, 2700),
    ("M5 Max 64 GB (local)",   3799, 185, 300, 1520, 1900),
]

# (name, mode, values)
# mode "split": values = (cached CPT, no-cache CPT) — closed Bedrock rows,
#   CPTs from the D-cloud session math (10-turn ~380k in/out, 2 users), not
#   the --input/--cache model.
# mode "range": values = (low CPT, high CPT)
REFERENCE = [
    ("Bedrock Sonnet 5.5 (closed)",        "split", (0.70, 2.40)),
    ("Bedrock Nova Pro / 2 Lite (closed)", "range", (0.40, 0.85)),
]


def cpt(v):
    return f"${v:,.3f}"


def dollars(v):
    return f"${v:,.0f}"


def burn_label(b):
    return f"{b:g}M"


def tab(headers, rows, right_cols):
    widths = [max(len(h), *(len(r[i]) for r in rows)) for i, h in enumerate(headers)]

    def fmt(cells):
        return "  ".join(
            cells[i].rjust(widths[i]) if i in right_cols else cells[i].ljust(widths[i])
            for i in range(len(headers))
        )

    print(fmt(headers))
    print("  ".join("-" * w for w in widths))
    for cells in rows:
        print(fmt(cells))


def main():
    ap = argparse.ArgumentParser(
        description="Token burn & cost-per-million-tokens calculator (see file docstring)."
    )
    ap.add_argument(
        "burn",
        nargs="?",
        default="600",
        help="household burn in M tok/mo; comma-separated for multiple columns (default 600)",
    )
    ap.add_argument(
        "--input",
        dest="input_frac",
        type=float,
        default=0.90,
        help="fraction of tokens that are input, agent skew (default 0.90, calibrated 2026-11-20)",
    )
    ap.add_argument(
        "--cache",
        dest="cache_hit",
        type=float,
        default=0.85,
        help="fraction of input tokens hitting the prompt prefix cache (default 0.85, validated 2026-11-20)",
    )
    args = ap.parse_args()

    if not 0.0 <= args.input_frac <= 1.0:
        ap.error("--input must be in [0, 1]")
    if not 0.0 <= args.cache_hit <= 1.0:
        ap.error("--cache must be in [0, 1]")
    burns = []
    for part in args.burn.split(","):
        b = float(part.strip())
        if b <= 0:
            ap.error("burn must be positive (M tok/mo)")
        burns.append(b)

    ifrac, hit = args.input_frac, args.cache_hit
    out_frac = 1.0 - ifrac
    blabels = [burn_label(b) for b in burns]

    print("Token burn & cost-per-million-tokens")
    print(f"household burn: {' / '.join(blabels)} M tok/mo")
    print(
        f"factors: input/output {ifrac*100:g} / {out_frac*100:g}  "
        f"· cache hit {hit*100:g}% of input"
    )
    print()

    # Cloud
    print(f"Cloud ({ROUTE}, list prices Nov 2026)")
    headers = ["model", "list in/out", "no-cache CPT", "effective CPT", *blabels]
    rows = []
    for name, in_r, cache_r, out_r in CLOUD:
        no_cache = in_r * ifrac + out_r * out_frac
        eff = no_cache
        if cache_r is not None:
            eff = in_r * ifrac * (1.0 - hit) + cache_r * ifrac * hit + out_r * out_frac
        rows.append(
            [name, f"${in_r:,.3f} / ${out_r:,.3f}", cpt(no_cache), cpt(eff)]
            + [dollars(eff * b) for b in burns]
        )
    tab(headers, rows, right_cols=set(range(1, len(headers))))
    print()

    # Local
    print("Local (3-yr TCO amortized, FLAT not token-gated)")
    print("  gross $/mo = pre-resale TCO / 36   ·   net $/mo = (TCO - resale) / 36")
    print("  $/mo-at-burn is flat (same regardless of burn) — CPT scales as 1/burn")
    print("  gross CPT answers 'what did this token cost me' (capex-justified)")
    print("  net   CPT answers 'net 3-yr TCO incl. resale recovery'")
    headers = [
        "machine", "capex", "gross $/mo", "net $/mo",
        *[f"${lbl}/mo" for lbl in blabels],
        *["gross " + lbl for lbl in blabels],
        *["net " + lbl for lbl in blabels],
    ]
    rows = []
    for name, capex, ac, elec, rlo, rhi in LOCAL:
        gross_total = capex + ac + elec
        gross_mo = gross_total / 36.0
        net_mo_lo = (gross_total - rhi) / 36.0  # high resale -> low net (best)
        net_mo_hi = (gross_total - rlo) / 36.0  # low resale  -> high net (worst)
        net_mid = (net_mo_lo + net_mo_hi) / 2.0
        rows.append(
            [name, dollars(capex), dollars(gross_mo),
             f"{dollars(net_mo_lo)}-{dollars(net_mo_hi)}"]
            + [dollars(net_mid) for _ in burns]   # flat — same at every burn
            + [cpt(gross_mo / b) for b in burns]  # scales as 1/burn
            + [cpt(net_mid / b) for b in burns]   # scales as 1/burn
        )
    tab(headers, rows, right_cols=set(range(1, len(headers))))
    print()

    # Reference
    print("Reference (closed; CPTs from D-cloud session math, not the --input/--cache model)")
    headers = ["model", "CPT", *blabels]
    rows = []
    for name, mode, (a, z) in REFERENCE:
        if mode == "split":
            col = f"{cpt(a)} / {cpt(z)}"
            cols = [f"{dollars(a * b)} / {dollars(z * b)}" for b in burns]
        else:
            col = f"{cpt(a)} - {cpt(z)}"
            cols = [f"${a * b:,.0f} / ${z * b:,.0f}" for b in burns]
        rows.append([name, col, *cols])
    tab(headers, rows, right_cols=set(range(1, len(headers))))
    print()
    print(
        "Note: figures are computed exactly from the list prices and factors above; "
        "the source figures are rounded, so dollar values may differ slightly."
    )


if __name__ == "__main__":
    main()
