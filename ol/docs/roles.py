from docutils import nodes
from docutils.parsers.rst import roles


def make_colored_role(color, latex_command):
    # Signature and mutable defaults are fixed by the docutils role API.
    def role(name, rawtext, text, lineno, inliner, options={}, content=[]):  # noqa: B006
        if inliner.document.settings.env.app.builder.format == "latex":
            node = nodes.raw("", rf"\{latex_command}{{{text}}}", format="latex")
        else:
            # Namespaced, plus the bare role name for backwards compatibility.
            # Role names like `mo`, `te` and `article` are short enough to
            # collide with a theme or a utility class in a shared namespace.
            node = nodes.inline(
                text, text, classes=["ol-mark", f"ol-mark--{color}", color]
            )
        return [node], []

    return role


def setup(app):

    # Load roles from conf.py
    app.add_config_value("custom_roles", [], "env")

    def register_custom_roles(app):
        for class_name in app.config.custom_roles:
            roles.register_local_role(
                class_name, make_colored_role(class_name, f"{class_name}def")
            )

    app.connect("builder-inited", register_custom_roles)

    # app.add_css_file("custom.css")  # optional: for HTML
    # roles.register_local_role('noun', make_colored_role('noun', 'noundef'))
    # roles.register_local_role('verb', make_colored_role('verb', 'verbdef'))

    # app.add_config_value('latex_elements', {}, 'env')
    app.add_config_value("custom_roles_loaded", True, "env")
