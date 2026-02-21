#!/usr/bin/env python3
"""Publish a Docusaurus blog post to Substack using its document JSON format."""

import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser
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


# ---------------------------------------------------------------------------
# HTML → Substack document JSON converter
# ---------------------------------------------------------------------------

class SubstackDocBuilder(HTMLParser):
    """Convert HTML to Substack's ProseMirror-like document JSON."""

    BLOCK_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "img", "ul", "ol", "li", "blockquote"}
    INLINE_TAGS = {"strong", "b", "em", "i", "a", "code"}

    def __init__(self):
        super().__init__()
        self.doc = {"type": "doc", "content": []}
        # Stack of (tag, attrs_dict, content_list) for open block/inline elements
        self._stack = []
        self._current_content = self.doc["content"]
        self._marks = []  # active inline marks

    # -- helpers --
    def _push(self, tag, attrs_dict, content_list):
        self._stack.append((tag, attrs_dict, content_list, self._current_content))
        self._current_content = content_list

    def _pop(self):
        if self._stack:
            tag, attrs_dict, content_list, parent = self._stack.pop()
            self._current_content = parent
            return tag, attrs_dict, content_list
        return None, None, None

    def _flush_text(self, text):
        """Add a text node with current marks to _current_content."""
        if not text:
            return
        node = {"type": "text", "text": text}
        if self._marks:
            node["marks"] = list(self._marks)
        self._current_content.append(node)

    # -- handler overrides --
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag in ("hr",):
            self._current_content.append({"type": "horizontalRule"})
            return

        if tag == "img":
            src = attrs_dict.get("src", "")
            alt = attrs_dict.get("alt", "")
            node = {
                "type": "image2",
                "attrs": {
                    "src": src,
                    "fullscreen": False,
                    "imageSize": "normal",
                    "height": None,
                    "width": None,
                    "resizeWidth": None,
                    "bytes": None,
                    "alt": alt,
                    "title": alt,
                    "type": None,
                    "href": None,
                    "belowTheFold": False,
                    "topImage": False,
                    "internalRedirect": None,
                    "isEditorRecist": False,
                },
            }
            self._current_content.append(node)
            return

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            content_list = []
            self._push(tag, {"level": level}, content_list)
            return

        if tag == "p":
            content_list = []
            self._push(tag, {}, content_list)
            return

        if tag == "blockquote":
            content_list = []
            self._push(tag, {}, content_list)
            return

        if tag in ("ul", "ol"):
            content_list = []
            self._push(tag, {}, content_list)
            return

        if tag == "li":
            content_list = []
            self._push(tag, {}, content_list)
            return

        # Inline marks
        if tag in ("strong", "b"):
            self._marks.append({"type": "bold"})
        elif tag in ("em", "i"):
            self._marks.append({"type": "italic"})
        elif tag == "a":
            href = attrs_dict.get("href", "")
            self._marks.append({"type": "link", "attrs": {"href": href}})
        elif tag == "code":
            self._marks.append({"type": "code"})

    def handle_endtag(self, tag):
        if tag in ("hr", "img", "br"):
            return

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            _, attrs_dict, content_list = self._pop()
            if content_list:
                node = {
                    "type": "heading",
                    "attrs": {"level": attrs_dict["level"]},
                    "content": content_list,
                }
                self._current_content.append(node)
            return

        if tag == "p":
            _, _, content_list = self._pop()
            if content_list:
                # Check if content is just an image (from markdown ![alt](src) inside <p>)
                if len(content_list) == 1 and content_list[0].get("type") == "image2":
                    self._current_content.append(content_list[0])
                else:
                    self._current_content.append({"type": "paragraph", "content": content_list})
            else:
                # Empty paragraph
                self._current_content.append({"type": "paragraph"})
            return

        if tag == "blockquote":
            _, _, content_list = self._pop()
            if content_list:
                self._current_content.append({"type": "blockquote", "content": content_list})
            return

        if tag in ("ul", "ol"):
            list_type = "bulletList" if tag == "ul" else "orderedList"
            _, _, content_list = self._pop()
            if content_list:
                self._current_content.append({"type": list_type, "content": content_list})
            return

        if tag == "li":
            _, _, content_list = self._pop()
            if content_list:
                # Wrap bare text nodes in a paragraph
                wrapped = []
                for item in content_list:
                    if item.get("type") == "text":
                        wrapped.append({"type": "paragraph", "content": [item]})
                    else:
                        wrapped.append(item)
                self._current_content.append({"type": "listItem", "content": wrapped})
            return

        # Inline marks - pop the matching mark
        if tag in ("strong", "b"):
            self._marks = [m for m in self._marks if m.get("type") != "bold"]
        elif tag in ("em", "i"):
            self._marks = [m for m in self._marks if m.get("type") != "italic"]
        elif tag == "a":
            self._marks = [m for m in self._marks if m.get("type") != "link"]
        elif tag == "code":
            self._marks = [m for m in self._marks if m.get("type") != "code"]

    def handle_data(self, data):
        if data.strip() or data == " ":
            self._flush_text(data)

    def get_document(self):
        return self.doc


def html_to_substack_doc(html_str):
    """Convert an HTML string to Substack's document JSON."""
    builder = SubstackDocBuilder()
    builder.feed(html_str)
    return builder.get_document()


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

def parse_blog_post(filepath):
    """Parse a Docusaurus markdown blog post into title, subtitle, and body doc."""
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
        body_md,
    )

    # Also convert local link-style image refs
    body_md = re.sub(
        r'\]\(/img/',
        f']({SITE_URL}/img/',
        body_md,
    )

    # Convert markdown to HTML
    body_html = markdown.markdown(
        body_md,
        extensions=["extra", "sane_lists"],
    )

    # Clean up --- rendered as <p>
    body_html = re.sub(r'<p>---</p>', '<hr>', body_html)

    # Convert HTML to Substack document JSON
    doc = html_to_substack_doc(body_html)

    return title, subtitle, doc


# ---------------------------------------------------------------------------
# Substack API
# ---------------------------------------------------------------------------

def get_publication_id():
    """Get the publication ID for the current subdomain."""
    r = requests.get(
        f"{BASE_URL}/api/v1/publication",
        cookies=get_cookies(),
        headers=HEADERS,
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["id"]


def create_draft(title, subtitle, body_doc):
    """Create a draft post on Substack with proper document JSON."""
    body_json = json.dumps(body_doc)

    r = requests.post(
        f"{BASE_URL}/api/v1/drafts/",
        cookies=get_cookies(),
        headers=HEADERS,
        json={
            "draft_title": title,
            "draft_subtitle": subtitle,
            "draft_body": body_json,
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
        url = f"{BASE_URL}/p/{slug}" if slug else BASE_URL
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

    title, subtitle, body_doc = parse_blog_post(args.file)
    body_json = json.dumps(body_doc)
    print(f"Title: {title}")
    print(f"Subtitle: {subtitle[:80]}...")
    print(f"Body JSON length: {len(body_json)} chars")
    print(f"Document nodes: {len(body_doc.get('content', []))}")

    draft_id = create_draft(title, subtitle, body_doc)

    if args.draft_only:
        print(f"Draft created (not published): {BASE_URL}/publish/post/{draft_id}")
    else:
        url = publish_draft(draft_id)
        print(f"Done! Post live at: {url}")


if __name__ == "__main__":
    main()
