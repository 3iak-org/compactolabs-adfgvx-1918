"""Append-only trials log: every configuration run on an R entry (prereg 'Logging')."""
import json, time, os
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trials.log")
def log(**kw):
    kw["t"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG, "a") as f: f.write(json.dumps(kw, sort_keys=True) + "\n")
