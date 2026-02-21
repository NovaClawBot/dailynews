#!/usr/bin/env python3
"""Publish a Docusaurus blog post to Substack."""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import markdown
import requests

SUBSTACK_COOKIE = os.environ.get("SUBSTACK_COOKIE", "")
SUBSTACK_SUBDOMAIN = os.environ.get("SUBSTACK_SUBDOMAIN", "nova750605")
BASE_URL = f"https://{SUBSTACK_SUBDOMAIN}.substack.com"
SITE_URL = "https://novaclawbot.github.io/dailynews"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Content-Type": "application/json",
}


def get_cookies():
    return {"substack.sid": SUBSTACK_COOKIE}


def parse_blog_post(filepath):
    """Parse a Docusaurus markdown blog post into title, subtitle, and body."""
    text = Path(filepath).read_text()

    # Extract frontmatter
    fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not fm_match:
        print("Error: No frontmatter found")
        sys.exit(1)

    frontmatter = fm_match.group(1)
    body_md = text[fm_match.end():]

    # Parse title from frontmatter
    title_match = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', frontmatter, re.MULTILINE)
    title = title_match.group(1) if title_match else "Daily Briefing"

    # Remove <!-- truncate --> marker
    body_md = body_md.replace("<!-- truncate -->", "")

    # Extract subtitle (first non-empty line of body)
    lines = [l.strip() for l in body_md.strip().split("\n") if l.strip()]
    subtitle = lines[0] if lines else ""

    # Convert local image paths to full URLs
    body_md = re.sub(
        r'!\[([^\]]*)\]\(/img/',
        f'![\\1]({SITE_URL}/img/',
        body_md
    )

    # Convert markdown to HTML
    body_html = markdown.markdown(
        body_md,
        extensions=["extra", "sane_lists"],
    )

    # Clean up: convert --- to <hr>
    body_html = re.sub(r'<p>---</p>', '<hr>', body_html)

    return title, subtitle, body_html


def create_draft(title, subtitle, body_html):
    """Create a draft post on Substack."""
    r = requests.post(
        f"{BASE_URL}/api/v1/drafts/",
        cookies=get_cookies(),
        headers=HEADERS,
        json={
            "draft_title": title,
            "draft_subtitle": subtitle,
            "draft_body": body_html,
            "draft_bylines": [],
            "type": "newsletter",
        },
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    print(f"Created draft: id={data['id']}")
    return data["id"]


def publish_draft(draft_id):
    """Publish a draft post."""
    r = requests.post(
        f"{BASE_URL}/api/v1/drafts/{draft_id}/publish",
        cookies=get_cookies(),
        headers=HEADERS,
        json={"send": True},
        timeout=60,
    )
    if r.status_code == 200:
        data = r.json()
        slug = data.get("slug", "")
        url = f"{BASE_URL}/p/{slug}" if slug else f"{BASE_URL}"
        print(f"Published: {url}")
        return url
    else:
        print(f"Publish failed: {r.status_code} {r.text[:500]}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Publish blog post to Substack")
    parser.add_argument("file", help="Path to the Docusaurus markdown blog post")
    parser.add_argument("--draft-only", action="store_true", help="Create draft without publishing")
    args = parser.parse_args()

    if not SUBSTACK_COOKIE:
        print("Error: SUBSTACK_COOKIE environment variable not set")
        sys.exit(1)

    title, subtitle, body_html = parse_blog_post(args.file)
    print(f"Title: {title}")
    print(f"Subtitle: {subtitle[:80]}...")
    print(f"Body length: {len(body_html)} chars")

    draft_id = create_draft(title, subtitle, body_html)

    if args.draft_only:
        print(f"Draft created (not published): {BASE_URL}/publish/post/{draft_id}")
    else:
        url = publish_draft(draft_id)
        print(f"Done! Post live at: {url}")


if __name__ == "__main__":
    main()
