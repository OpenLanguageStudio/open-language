"""The few GitHub API calls the content review makes.

The token comes from ``GH_TOKEN`` or ``GITHUB_TOKEN``. In CI that is the
workflow's own token. A reviewer posting a verdict uses the repository bot's
installation token, so the status and the report are the bot's.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

from ol.review import CONTEXT, ChangedFile, is_page, needs_texts

API = "https://api.github.com"
COMMENT_MARK = "<!-- content-review-tier -->"


class GitHubError(RuntimeError):
    """A GitHub API call failed."""


def token() -> str:
    """The API token, or GitHubError when there is none."""
    value = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not value:
        raise GitHubError("set GH_TOKEN to a token that may post commit statuses")
    return value


def call(method: str, path: str, body: dict | None = None, raw: bool = False):
    """One API call.

    Args:
        method: The HTTP method.
        path: The path below the API root, or a full URL.
        body: The JSON body, for a write.
        raw: Return the response's bytes as text, not parsed JSON.

    Returns:
        The parsed response, or its text with ``raw``.
    """
    url = path if path.startswith("https://") else f"{API}{path}"
    request = urllib.request.Request(  # noqa: S310 (the URL is always the API's)
        url,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {token()}",
            "Accept": "application/vnd.github.raw"
            if raw
            else "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
            data = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise GitHubError(f"{method} {path}: {exc.code} {detail}") from exc
    if raw:
        return data
    return json.loads(data) if data else None


def pull(repo: str, number: int) -> dict:
    """The pull request."""
    return call("GET", f"/repos/{repo}/pulls/{number}")


def _text(repo: str, path: str, ref: str) -> str | None:
    quoted = urllib.parse.quote(path)
    try:
        return call("GET", f"/repos/{repo}/contents/{quoted}?ref={ref}", raw=True)
    except GitHubError:
        return None


def changed_files(repo: str, pr: dict) -> list[ChangedFile]:
    """Every changed file of the pull request, with the texts its tier needs."""
    found: list[ChangedFile] = []
    page = 1
    while True:
        batch = call(
            "GET", f"/repos/{repo}/pulls/{pr['number']}/files?per_page=100&page={page}"
        )
        for item in batch:
            found.append(
                ChangedFile(
                    path=item["filename"],
                    status=item["status"],
                    additions=item["additions"],
                    deletions=item["deletions"],
                    patch=item.get("patch"),
                )
            )
        if len(batch) < 100:
            break
        page += 1
    base, head = pr["base"]["sha"], pr["head"]["sha"]
    for changed in found:
        if needs_texts(changed) and is_page(changed.path):
            if changed.status != "added":
                changed.base_text = _text(repo, changed.path, base)
            if changed.status != "removed":
                changed.head_text = _text(repo, changed.path, head)
    return found


def post_status(repo: str, sha: str, state: str, description: str) -> None:
    """Set the content-review commit status on ``sha``."""
    call(
        "POST",
        f"/repos/{repo}/statuses/{sha}",
        {"state": state, "context": CONTEXT, "description": description[:140]},
    )


def comment(repo: str, number: int, body: str) -> None:
    """Add a comment to the pull request."""
    call("POST", f"/repos/{repo}/issues/{number}/comments", {"body": body})


def upsert_tier_comment(repo: str, number: int, body: str) -> None:
    """Write the tier comment, replacing the one an earlier push left."""
    body = f"{COMMENT_MARK}\n{body}"
    comments = call("GET", f"/repos/{repo}/issues/{number}/comments?per_page=100")
    for existing in comments:
        if COMMENT_MARK not in (existing.get("body") or ""):
            continue
        if existing["body"] == body:
            return
        try:
            call("PATCH", existing["url"], {"body": body})
        except GitHubError:
            break  # written by another account: add a fresh one
        else:
            return
    comment(repo, number, body)
