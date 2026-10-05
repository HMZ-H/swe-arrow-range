#!/usr/bin/env python3
"""Reward 1.0 only if every F2P test passes and nothing else regressed
against the recorded baseline."""
import json, shutil, subprocess, sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path("/workspace")
REPO = ROOT / "repo"
F2P = [l.strip() for l in (ROOT / "f2p.txt").read_text().splitlines() if l.strip()]
BASELINE = ROOT / "baseline.json"


def key_from_nodeid(nid):
    bits = nid.split("::")
    mod = bits[0][:-3] if bits[0].endswith(".py") else bits[0]
    return "::".join(mod.replace("/", ".").split(".") + bits[1:])


def key_from_xml(tc):
    cn = tc.get("classname") or ""
    return "::".join([p for p in cn.split(".") if p] + [tc.get("name") or ""])


def run_tests(xml):
    subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-o", "addopts=",
         f"--junitxml={xml}", "-q", "--tb=no", "tests/"],
        cwd=REPO, capture_output=True)
    if not Path(xml).exists():
        return {}
    out = {}
    for tc in ET.parse(xml).getroot().iter("testcase"):
        kids = {c.tag for c in tc}
        st = ("failed" if "failure" in kids else
              "error" if "error" in kids else
              "skipped" if "skipped" in kids else "passed")
        out[key_from_xml(tc)] = st
    return out


SOURCE_GLOB = "arrow/*.py"


def isolate():
    """Keep ONLY the agent's changes to library source. Everything else the
    agent left in the working tree is discarded before grading."""
    diff = subprocess.run(["git", "diff", "--", SOURCE_GLOB],
                          cwd=REPO, capture_output=True, text=True).stdout
    subprocess.run(["git", "checkout", "--", "."], cwd=REPO, capture_output=True)
    subprocess.run(["git", "clean", "-fdx", "--", "."], cwd=REPO, capture_output=True)
    if diff.strip():
        subprocess.run(["git", "apply", "-"], cwd=REPO, input=diff,
                       capture_output=True, text=True)


def main():
    if "--baseline" not in sys.argv:
        isolate()
    shutil.copy(ROOT / "hidden_test_arrow.py", REPO / "tests" / "test_arrow.py")
    res = run_tests("/tmp/r.xml")

    if "--baseline" in sys.argv:
        print(json.dumps(res, sort_keys=True, indent=0))
        return 0

    known = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
    f2p_keys = [key_from_nodeid(t) for t in F2P]
    f2p_pass = [k for k in f2p_keys if res.get(k) == "passed"]
    regressions = sorted(
        k for k, st in res.items()
        if st in ("failed", "error") and k not in f2p_keys and known.get(k) != st)

    ok = len(f2p_pass) == len(F2P) and not regressions
    print(json.dumps({
        "reward": 1.0 if ok else 0.0,
        "f2p_passed": len(f2p_pass),
        "f2p_total": len(F2P),
        "f2p_detail": {t: res.get(key_from_nodeid(t), "missing") for t in F2P},
        "collected": len(res),
        "regressions": regressions[:10],
    }, indent=2))
    return 0 if ok else 1


sys.exit(main())
