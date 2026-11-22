"""Regression cases for studio_gate.decide (includes Sol round 4's cases). Run: python3 test_studio_gate.py"""
from studio_gate import decide
FIRE = ["Add an accessible button to the header and leave the footer alone", "Build me a landing page for my SaaS", "Add a button to settings", "Make it look good",
        "Ship the pricing page", "animate the hero section with scroll effects", "make a 30 second promo video",
        "Can you redesign the dashboard?", "please polish the navbar and footer", "Let's add a 3D scene to the homepage"]
SKIP = ["Add pagination to the dashboard API endpoint", "Fix the API and leave the dashboard alone", "Review the attached video transcript for factual errors",
        "Do not redesign the homepage", "what does this function do", "fix the auth bug in login.py",
        "<task-notification>build website</task-notification>", "/impeccable polish the hero",
        'Explain this error: "Failed to build component Button"', "train a model on the video dataset"]
bad = [p for p in FIRE if not decide(p)] + [p for p in SKIP if decide(p)]
print(f"{len(FIRE)+len(SKIP)-len(bad)}/{len(FIRE)+len(SKIP)} cases correct")
for p in bad: print("WRONG:", repr(p), "->", decide(p))
import sys as _s; _s.exit(1 if bad else 0)
