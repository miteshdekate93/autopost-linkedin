"""
Post Scheduler
Reads post files from the posts/ directory and publishes the next scheduled one.

Post files are markdown with YAML frontmatter:

    ---
    scheduled: 2024-01-15
    published: false
    ---

    Your LinkedIn post content here.
"""

import glob
import sys
from datetime import date
from pathlib import Path

import yaml

from linkedin_client import LinkedInClient


POSTS_DIR = Path(__file__).parent.parent / "posts"


def parse_post(filepath: str) -> dict:
    """Parse a markdown post file with YAML frontmatter."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid post format in {filepath} — missing frontmatter")

    frontmatter = yaml.safe_load(parts[1])
    body = parts[2].strip()

    return {
        "scheduled": frontmatter.get("scheduled"),
        "published": frontmatter.get("published", False),
        "content": body,
        "filepath": filepath,
    }


def mark_as_published(filepath: str) -> None:
    """Update the post file to mark it as published."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("published: false", "published: true", 1)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Marked {Path(filepath).name} as published")


def find_next_post() -> dict | None:
    """Find the oldest unpublished post scheduled for today or earlier."""
    today = date.today()
    pending = []

    for filepath in glob.glob(str(POSTS_DIR / "*.md")):
        # Skip the README inside posts/
        if "README" in filepath:
            continue
        try:
            post = parse_post(filepath)
            scheduled = post["scheduled"]
            if isinstance(scheduled, str):
                from datetime import datetime
                scheduled = datetime.strptime(scheduled, "%Y-%m-%d").date()
            if not post["published"] and scheduled <= today:
                post["scheduled"] = scheduled
                pending.append(post)
        except Exception as e:
            print(f"⚠ Skipping {filepath}: {e}")

    if not pending:
        return None

    return sorted(pending, key=lambda p: p["scheduled"])[0]


def main() -> None:
    post = find_next_post()

    if not post:
        print("No posts scheduled for today or earlier. Nothing to publish.")
        sys.exit(0)

    print(f"Publishing post scheduled for {post['scheduled']}...")
    print(f"Content preview: {post['content'][:100]}...")

    client = LinkedInClient()
    result = client.publish_post(post["content"])

    post_id = result.get("id", "unknown")
    print(f"✓ Published successfully! LinkedIn Post ID: {post_id}")

    mark_as_published(post["filepath"])


if __name__ == "__main__":
    main()
