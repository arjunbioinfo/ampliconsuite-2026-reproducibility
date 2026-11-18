"""Reconstruct the v1.5.1 gene-probe benchmark from the archived workbooks."""
import csv
import hashlib
import subprocess
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "results/validation"
BASE = "https://pmc-oa-opendata.s3.amazonaws.com/PMC13736199.1/"
FISH = {"DM", "Native HSR", "Non-native HSR", "Unknown HSR", "Indeterminate"}
AC = {"ecDNA", "NoFCNA", "Linear", "Complex-non-cyclic", "BFB", "unknown"}


def get_inputs():
    for line in (DATA / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split()
        target = DATA / name
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise ValueError(f"Checksum mismatch in {target}")
            continue
        with TemporaryDirectory(dir=DATA) as temp:
            path = Path(temp) / name
            payload = subprocess.check_output(["curl", "-fLsS", "--retry", "3", BASE + name])
            path.write_bytes(payload)
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError(f"Checksum mismatch downloading {name}")
            path.replace(target)


def sheet(number, name):
    book = load_workbook(DATA / f"41592_2026_3264_MOESM{number}_ESM.xlsx", read_only=True, data_only=True)
    try:
        rows = iter(book[name].values)
        headers = next(rows)
        return [dict(zip(headers, row)) for row in rows]
    finally:
        book.close()


def score(fish, ac, include_unknown_hsr):
    if fish not in FISH or ac not in AC:
        raise ValueError(f"Unexpected labels: {fish!r}, {ac!r}")
    if fish == "Indeterminate":
        return "neutral_fish"
    if ac == "unknown":
        return "neutral_ac"
    if ac == "ecDNA":
        if fish == "Non-native HSR" or (include_unknown_hsr and fish == "Unknown HSR"):
            return "neutral_possible_integration"
        return "TP" if fish == "DM" else "FP"
    return "FN" if fish == "DM" else "TN"


def write_table(name, rows):
    with (OUT / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    get_inputs()
    records = sheet(4, "FISH_results")
    keys = {(r["Sample"], r["Gene"]) for r in records}
    if len(keys) != len(records) or len(keys) != 175 or len({s for s, g in keys}) != 72:
        raise ValueError("Unexpected validation cohort")
    audit = []
    for r in records:
        fish, ac = r["FISH finding"], r["AC Classification"]
        audit.append(dict(sample=r["Sample"], gene=r["Gene"], fish=fish, ac=ac,
                          methods_literal=score(fish, ac, False),
                          figure_consistent=score(fish, ac, True)))
    metrics = []
    for policy in ("methods_literal", "figure_consistent"):
        counts = Counter(r[policy] for r in audit)
        scored = sum(counts[k] for k in ("TP", "FP", "TN", "FN"))
        metrics.append(dict(policy=policy, **{k: counts[k] for k in ("TP", "FP", "TN", "FN")},
                            scored=scored, neutral=len(records)-scored,
                            precision=counts["TP"]/(counts["TP"]+counts["FP"]),
                            recall=counts["TP"]/(counts["TP"]+counts["FN"])))
    reproduced = metrics[-1]
    # Reference counts transcribed from Figure 1d. Figure 1e reports percentages.
    if tuple(reproduced[k] for k in ("TP", "FP", "TN", "FN")) != (53, 5, 81, 3):
        raise ValueError("Figure 1d mismatch")
    ref, = [r for r in sheet(11, "Figure1e") if r["AC Version"] == "1.5.1"]
    for metric in ("precision", "recall"):
        if round(100 * reproduced[metric], 1) != ref[metric.title()]:
            raise ValueError(f"Figure 1e mismatch: {metric}")
    OUT.mkdir(exist_ok=True, parents=True)
    write_table("probe_audit.tsv", audit)
    write_table("metrics.tsv", metrics)
    print(f"Verified Figure 1d/e for {len(records)} probes; outputs in {OUT}")


if __name__ == "__main__":
    main()
