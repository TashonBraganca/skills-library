#!/usr/bin/env python3
"""Claude Code PreToolUse hook, matcher WebFetch.

Denies WebFetch for Reddit, X/Twitter, Nitter and YouTube hosts, and points
Claude to the `social-search` skill and its helper scripts. Everything else is allowed (no output).
"""
import json
import os
import sys
from urllib.parse import urlparse

BLOCKED_DOMAINS = [
    "reddit.com", "redd.it",
    "x.com", "twitter.com",
    "youtube.com", "youtube-nocookie.com", "youtu.be",
]
REDDIT_DOMAINS = {"reddit.com", "redd.it"}

REDDIT_MSG = (
    "WebFetch is blocked for Reddit. Use the `social-search` skill, or run the helper directly:\n"
    "python3 ~/.skills-library/skills/research/scripts/reddit.py search \"<words>\" -s <sub1>,<sub2> --since 6m\n"
    "python3 ~/.skills-library/skills/research/scripts/reddit.py thread <thread id or reddit URL>\n"
    "It reads the Arctic Shift archive API (title search, 6 to 8 seconds between calls, retries on 422 Timeout). "
    "For a known thread, use the thread mode with its id. An empty result means no archive match for that query, "
    "not that nobody posted; a failed call means nothing. Report coverage limits if they affect the answer."
)
OTHER_MSG = (
    "WebFetch is blocked for X, Twitter, Nitter and YouTube. Use the `social-search` skill, or run the helpers directly:\n"
    "X search: python3 ~/.skills-library/skills/research/scripts/social.py x search \"<words>\" --since 90d\n"
    "X post: python3 ~/.skills-library/skills/research/scripts/fetch.py <x.com status URL>\n"
    "YouTube: python3 ~/.skills-library/skills/research/scripts/youtube.py search \"<words>\" or transcript <id or URL>\n"
    "Any other page: python3 ~/.skills-library/skills/research/scripts/fetch.py <url>. "
    "Verify the output contains the requested post text, comments or transcript. If you only got metadata, a login "
    "wall or a challenge page, say which content you could not retrieve. X coverage is thin; say so in the report."
)


def host_of(url):
    if not isinstance(url, str):
        raise ValueError("URL must be a string")
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("URL must be absolute HTTP(S)")
    return parsed.hostname.lower().rstrip(".")


def blocked_domain(host):
    for d in BLOCKED_DOMAINS:
        if host == d or host.endswith("." + d):
            return d
    # nitter.net, nitter.example.org: a whole "nitter" label, not any label starting with it
    return "nitter" if "nitter" in host.split(".")[:-1] else None


def deny(message):
    json.dump({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                      "permissionDecision": "deny",
                                      "permissionDecisionReason": message}}, sys.stdout)


def main():
    if os.environ.get("SKILL_HOOKS_OFF") == "1":  # the skills-off arm of a paired test
        return 0
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("Expected a hook object")
        if data.get("tool_name") not in (None, "WebFetch"):
            return 0
        tool_input = data.get("tool_input")
        if not isinstance(tool_input, dict):
            raise ValueError("Expected a tool_input object")
        domain = blocked_domain(host_of(tool_input.get("url")))
    except ValueError:
        deny("WebFetch blocked because the hook could not read a valid HTTP(S) URL.")
        return 0
    if domain:
        deny(REDDIT_MSG if domain in REDDIT_DOMAINS else OTHER_MSG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
