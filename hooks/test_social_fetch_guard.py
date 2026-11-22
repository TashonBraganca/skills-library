"""Regression cases for social_fetch_guard. Run: python3 test_social_fetch_guard.py"""
import json, os, subprocess, sys
GUARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "social_fetch_guard.py")
CASES = [("https://www.reddit.com/r/x/", "deny"), ("https://old.reddit.com/r/x", "deny"), ("https://redd.it/abc", "deny"),
         ("https://x.com/a/status/1", "deny"), ("https://mobile.twitter.com/a", "deny"), ("https://youtu.be/abc", "deny"),
         ("https://m.youtube.com/watch?v=1", "deny"), ("https://www.youtube-nocookie.com/embed/1", "deny"),
         ("https://nitter.net/a", "deny"), ("https://nitter.example.org/a", "deny"), ("https://[", "deny"),
         ("https://github.com/a/b", "allow"), ("https://arxiv.org/abs/1", "allow"), ("https://notreddit.com/", "allow"),
         ("https://fix.x.com.evil.org/", "allow"), ("https://nitterbugs.example.org/", "allow")]
bad = 0
for url, want in CASES:
    out = subprocess.run([sys.executable, GUARD], input=json.dumps(
        {"tool_name": "WebFetch", "tool_input": {"url": url}}), capture_output=True, text=True).stdout
    got = "deny" if '"deny"' in out else "allow"
    if got != want: bad += 1; print("WRONG", url, got)
print(f"{len(CASES)-bad}/{len(CASES)} cases correct")
import sys as _s; _s.exit(1 if bad else 0)
