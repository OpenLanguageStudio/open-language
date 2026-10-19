"""The ``ol`` command: coursebook build, content checks and authoring helpers."""

import json
import subprocess
import sys
from pathlib import Path

import typer

from ol.blocks import BlockCollection, BlockFormatError, Refusal

app = typer.Typer(help="Open Language authoring tools")

BASELINE_FILE = ".ol-validate-baseline"


@app.command()
def docs(
    live: bool = typer.Option(False, "--live", help="Auto-rebuild with live server."),
):
    """Build the documentation."""
    if live:
        subprocess.run(
            [
                "sphinx-autobuild",
                "docs",
                "docs/_build/html",
                "--open-browser",
                "--port",
                "5000",
                "--watch",
                ".",
            ],
            check=True,
        )
    else:
        subprocess.run(
            ["sphinx-build", "-E", "-b", "html", "docs", "docs/_build/html"], check=True
        )


@app.command()
def outline(
    level: str = typer.Option("", help="Filter by CEFR level(s), e.g. 'a2 b1'."),
    category: str = typer.Option(
        "", help="Filter by category(ies), e.g. 'grammar concepts'."
    ),
    hide_sections: bool = typer.Option(
        False,
        "--hide-sections",
        help="Show article titles only; hide section headings.",
    ),
    max_heading_level: int | None = typer.Option(
        None, help="Deepest heading level to include (1=H1, 2=H1+H2, …)."
    ),
    json: bool = typer.Option(False, "--json", help="Output as JSON."),
):
    """Print the heading structure of all CEFR-level docs."""
    sys.path.insert(0, str(Path.cwd() / "docs"))
    from outline import main as outline_main

    argv = []
    if level:
        argv += ["--level", *level.split()]
    if category:
        argv += ["--category", *category.split()]
    if hide_sections:
        argv.append("--hide-sections")
    if max_heading_level is not None:
        argv += ["--max-heading-level", str(max_heading_level)]
    if json:
        argv.append("--json")

    outline_main(argv)


def main() -> None:
    app()


@app.command()
def context(
    as_json: bool = typer.Option(
        False, "--json", help="Output as JSON (for agent consumption)."
    ),
):
    """Resolve working context (level, section) from the current git branch."""
    from ol.context import get_current_branch, parse_branch

    branch = get_current_branch()
    if branch is None:
        if as_json:
            print(json.dumps({"error": "could not determine current branch"}))
        else:
            typer.echo("Error: could not determine current branch.", err=True)
        raise typer.Exit(1)

    ctx = parse_branch(branch)

    if as_json:
        print(json.dumps(ctx))
        return

    typer.echo(f"Branch:      {ctx['branch']}")
    if ctx["level"] is None:
        typer.echo("Level:       (not a content branch)")
        typer.echo("Section:     -")
        typer.echo("Sub-section: -")
        typer.echo()
        typer.echo(
            "Note: This branch does not follow the content/{level}-{section} convention."
        )
    else:
        typer.echo(f"Level:       {ctx['level']}")
        typer.echo(f"Section:     {ctx['section']}")
        typer.echo(f"Sub-section: {ctx['sub_section'] or '-'}")


def _article_files(docs_root: Path) -> list[Path]:
    """Every Markdown file under the CEFR level directories (docs/<level>/...)."""
    files: list[Path] = []
    for level_dir in sorted(p for p in docs_root.iterdir() if p.is_dir()):
        if (
            len(level_dir.name) == 2
            and level_dir.name[0] in "abc"
            and level_dir.name[1] in "12"
        ):
            files.extend(sorted(level_dir.rglob("*.md")))
    return files


def _read_baseline(path: Path) -> set[str]:
    if not path.exists():
        return set()
    lines = path.read_text(encoding="utf-8").splitlines()
    return {
        ln.strip() for ln in lines if ln.strip() and not ln.lstrip().startswith("#")
    }


def cross_page_refusals(workspace: Path) -> dict[str, list[Refusal]]:
    """The refusals that need every page, by file relative to the workspace.

    Every page under docs/ is read, whichever files are being checked, so a
    duplicate is matched with the block that writes its track wherever it is.
    While a block on any page cannot be read there is nothing to match against,
    and that page's own report fails the run instead.
    """
    found: dict[str, list[Refusal]] = {}
    try:
        collection = BlockCollection.from_docs(workspace / "docs")
    except BlockFormatError:
        return found
    for refusal in collection.refusals():
        if refusal.code in Refusal.CROSS_PAGE:
            found.setdefault(f"docs/{refusal.block.page}.md", []).append(refusal)
    return found


def file_report(path: Path, workspace: Path, cross_page: dict[str, list[Refusal]]):
    """Validate one file and add the refusals across pages that fall on it."""
    from ol.authoring.validate import validate_file

    rep = validate_file(path, workspace)
    rel = path.resolve().relative_to(workspace.resolve()).as_posix()
    for refusal in cross_page.get(rel, []):
        rep.error(
            f"audio-examples (line {refusal.block.line}): {refusal.code}: "
            f"{refusal.detail}"
        )
    return rep


def _run_validate(
    files: list[Path], workspace: Path, baseline_path: Path, verbose: bool
) -> tuple[list[str], list[str], int]:
    """Validate files. Returns (new failures, baseline entries now passing, checked)."""
    from ol.authoring.validate import report_status

    baseline = _read_baseline(baseline_path)
    cross_page = cross_page_refusals(workspace)
    new_failures: list[str] = []
    now_passing: list[str] = []
    for path in files:
        rel = path.resolve().relative_to(workspace.resolve()).as_posix()
        rep = file_report(path, workspace, cross_page)
        status = report_status(rep)
        if status == "FAIL" and rel not in baseline:
            new_failures.append(rel)
            typer.echo(f"[FAIL] {rel}")
            for lvl, msg in rep.items:
                if lvl == "ERROR" or verbose:
                    typer.echo(f"    {lvl}: {msg}")
        elif status != "FAIL" and rel in baseline:
            now_passing.append(rel)
        elif verbose:
            typer.echo(
                f"[{status}] {rel}" + ("  (baseline)" if rel in baseline else "")
            )
    return new_failures, now_passing, len(files)


@app.command()
def validate(
    files: list[Path] = typer.Argument(
        None, help="Files to check. Default: every article under docs/<level>/."
    ),
    workspace: Path = typer.Option(Path("."), help="Language workspace root."),
    baseline: Path = typer.Option(
        None, help=f"Known-failure list. Default: <workspace>/{BASELINE_FILE}."
    ),
    write_baseline: bool = typer.Option(
        False, "--write-baseline", help="Record every current failure as the baseline."
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show every file."),
):
    """Check articles and indexes against the authoring templates.

    Files listed in the baseline may fail without failing the run; any other
    failure does. A baseline entry that now passes is reported so it can be
    removed, and the baseline only ever shrinks.
    """
    from ol.authoring.validate import report_status

    baseline_path = baseline or workspace / BASELINE_FILE
    targets = list(files) if files else _article_files(workspace / "docs")

    if write_baseline:
        failing = []
        cross_page = cross_page_refusals(workspace)
        for path in targets:
            if report_status(file_report(path, workspace, cross_page)) == "FAIL":
                failing.append(
                    path.resolve().relative_to(workspace.resolve()).as_posix()
                )
        header = (
            "# Articles that failed `ol validate` when this baseline was written.\n"
            "# Remove a line once its article passes. Never add lines by hand.\n"
        )
        baseline_path.write_text(
            header + "".join(f"{f}\n" for f in sorted(failing)), encoding="utf-8"
        )
        typer.echo(
            f"Baseline written: {len(failing)} failing file(s) -> {baseline_path}"
        )
        return

    new_failures, now_passing, checked = _run_validate(
        targets, workspace, baseline_path, verbose
    )
    for rel in now_passing:
        typer.echo(f"PASSING, remove from baseline: {rel}")
    if new_failures:
        typer.echo(
            f"\n{len(new_failures)} file(s) fail outside the baseline ({checked} checked)."
        )
        raise typer.Exit(1)
    typer.echo(f"OK: {checked} file(s) checked, no failures outside the baseline.")


@app.command()
def templates(
    name: str = typer.Argument(None, help="Template to print. Omit to list them."),
):
    """List the authoring templates, or print one."""
    from ol.authoring.validate import TEMPLATES_DIR

    if name is None:
        for path in sorted(TEMPLATES_DIR.iterdir()):
            typer.echo(path.name)
        return
    path = TEMPLATES_DIR / name
    if not path.exists():
        typer.echo(f"No template named {name}.", err=True)
        raise typer.Exit(1)
    typer.echo(path.read_text(encoding="utf-8"), nl=False)


@app.command()
def check(
    workspace: Path = typer.Option(Path("."), help="Language workspace root."),
    skip_build: bool = typer.Option(False, "--skip-build", help="Skip the docs build."),
):
    """Run every content check: validate, then a strict docs build.

    This is the same gate CI runs. Both steps run even when the first one
    fails, so one pass reports everything.
    """
    failed: list[str] = []

    typer.echo("== ol validate")
    new_failures, now_passing, checked = _run_validate(
        _article_files(workspace / "docs"), workspace, workspace / BASELINE_FILE, False
    )
    for rel in now_passing:
        typer.echo(f"PASSING, remove from baseline: {rel}")
    if new_failures:
        failed.append("validate")
    else:
        typer.echo(f"OK: {checked} file(s), no failures outside the baseline.")

    if not skip_build:
        typer.echo("\n== sphinx-build -W")
        cmd = [
            sys.executable,
            "-m",
            "sphinx",
            "-W",
            "--keep-going",
            "-E",
            "-q",
            "-b",
            "html",
            "docs",
            "docs/_build/html",
        ]
        if subprocess.run(cmd, cwd=workspace).returncode:
            failed.append("docs build")

    if failed:
        typer.echo(f"\nFAILED: {', '.join(failed)}")
        raise typer.Exit(1)
    typer.echo("\nAll checks passed.")
