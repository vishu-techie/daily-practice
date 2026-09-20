"""Generate one small daily practice file with the Claude API.

Picks a topic from a rotating curriculum, asks Claude for a problem +
solution + tests, and saves it to YYYY/MM/DD-slug.<ext>.
"""
import datetime
import os
import pathlib
import re

import anthropic

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")

# (language, topic) pairs. Edit freely: this is your curriculum.
CURRICULUM = [
    ("Python", "string manipulation"),
    ("SQL", "joins and aggregations"),
    ("Pandas", "cleaning messy data"),
    ("Python", "lists, dicts and sets"),
    ("SQL", "window functions"),
    ("Pandas", "groupby and pivot tables"),
    ("Python", "recursion and dynamic programming"),
    ("SQL", "CTEs and subqueries"),
    ("Pandas", "merging and reshaping datasets"),
    ("Python", "sorting and searching"),
    ("Python", "file handling and CSV parsing"),
    ("SQL", "date and time queries"),
]

EXT = {"Python": "py", "Pandas": "py", "SQL": "sql"}


def pick_topic(today: datetime.date):
    idx = today.toordinal() % len(CURRICULUM)
    return CURRICULUM[idx]


def existing_slugs(root: pathlib.Path):
    slugs = []
    for p in root.glob("20*/*/*"):
        if p.is_file():
            slugs.append(p.stem.split("-", 1)[-1])
    return slugs[-60:]


def build_prompt(language, topic, done):
    return f"""Create one small daily practice exercise.

Language: {language}
Topic: {topic}
Already covered (do not repeat): {", ".join(done) or "nothing yet"}

Requirements:
- Beginner-to-intermediate difficulty, solvable in about 15 minutes.
- Start the file with a comment block containing the problem statement.
- Then a clear, commented solution.
- End with a few tests/asserts (Python) or sample data + expected output in comments (SQL).
- 30 to 60 lines total. Original, not copied from a known site.

Reply in exactly this format and nothing else:
SLUG: short-kebab-case-name
---
<the full file contents, no markdown code fences>
"""


def main():
    today = datetime.date.today()
    root = pathlib.Path(__file__).resolve().parent.parent
    language, topic = pick_topic(today)

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": build_prompt(language, topic, existing_slugs(root))}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()

    header, _, body = text.partition("---")
    m = re.search(r"SLUG:\s*([a-z0-9-]+)", header)
    if not m or not body.strip():
        raise SystemExit(f"Unexpected model output:\n{text[:500]}")
    slug = m.group(1)[:50]

    # Strip stray markdown fences if the model added them anyway.
    body = re.sub(r"^```\w*\n|\n```\s*$", "", body.strip())

    out_dir = root / f"{today:%Y}" / f"{today:%m}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{today:%d}-{slug}.{EXT[language]}"
    out_file.write_text(body + "\n", encoding="utf-8")

    pathlib.Path("/tmp/commit_msg.txt").write_text(
        f"Add {language} practice: {topic} ({slug})\n", encoding="utf-8"
    )
    print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
