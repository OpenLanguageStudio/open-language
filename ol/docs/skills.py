"""The ``skills`` directive: a level page's skills, drawn from its front matter.

A level page lists its skills once, under ``skills:`` in its front matter. The
directive is written ``:::{skills} know`` or ``:::{skills} can`` with no
options and no body, under "What learners know" and "What learners can do". It
draws a bullet list of the text of every skill of that kind, in the order the
front matter gives them.
"""

from __future__ import annotations

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util import logging

from ol.authoring.situations import front_matter
from ol.authoring.skills import DIRECTIVE, KINDS, list_problem

logger = logging.getLogger(__name__)
STORE = "ol_skills"


def skills_on(env) -> dict[str, object]:
    """What each page's front matter holds under ``skills:``, by page name."""
    if not hasattr(env, STORE):
        setattr(env, STORE, {})
    return getattr(env, STORE)


def read_skills(app, docname, source):
    """Keep the ``skills:`` of a page that has any."""
    fm = front_matter(source[0])
    if "skills" in fm:
        skills_on(app.env)[docname] = fm["skills"]


def purge(app, env, docname):
    """Forget what a page recorded before it is read again or after it is removed."""
    skills_on(env).pop(docname, None)


def merge(app, env, docnames, other):
    """Take what the pages a parallel reader read recorded."""
    for docname in docnames:
        if docname in skills_on(other):
            skills_on(env)[docname] = skills_on(other)[docname]


class SkillsDirective(Directive):
    """Draw the page's skills of one kind as a bullet list."""

    required_arguments = 1
    final_argument_whitespace = True

    def run(self) -> list[nodes.Node]:
        """Draw the list, or warn and draw nothing.

        Returns:
            The bullet list, or nothing when the argument or the front matter is
            not sound.
        """
        env = self.state.document.settings.env
        where = (env.docname, self.lineno)
        kind = self.arguments[0].strip()
        if kind not in KINDS:
            logger.warning(
                "%s: '%s' is not a kind of skill: write 'know' or 'can'",
                DIRECTIVE,
                kind,
                location=where,
            )
            return []
        skills = skills_on(env).get(env.docname)
        if skills is None:
            logger.warning(
                "%s: the page's front matter has no 'skills:'",
                DIRECTIVE,
                location=where,
            )
            return []
        if problem := list_problem(skills):
            logger.warning("%s: %s", DIRECTIVE, problem, location=where)
            return []
        texts = [s["text"] for s in skills if s["kind"] == kind]
        items = nodes.bullet_list()
        for text in texts:
            items += nodes.list_item("", nodes.paragraph("", text))
        return [items] if texts else []


def setup(app):
    """Register the directive and the hooks that keep each page's skills.

    Returns:
        The extension's metadata.
    """
    app.add_directive(DIRECTIVE, SkillsDirective)
    app.connect("source-read", read_skills)
    app.connect("env-purge-doc", purge)
    app.connect("env-merge-info", merge)
    return {
        "version": "1.0",
        "env_version": 1,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
