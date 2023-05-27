from pathlib import Path
from os import environ

import nox
from yaml import safe_load


def load_dependencies():
    environment = safe_load(Path("environment.dev.yml").read_text())
    conda = [
        pkg for pkg in environment.get("dependencies") if not pkg.startswith("python")
    ]
    requirements = conda.pop(-1).get("pip")
    return conda, requirements


def install_environment(session):
    conda, requirements = load_dependencies()
    session.conda_install(*conda)
    session.install(*requirements)


@nox.session(venv_backend="conda", python=environ.get("PYTHON_VERSION", "3.11"))
def test(session):
    install_environment(session)
    session.run("python", "--version")
    session.run("python", "-c", "import jupysql_plugin")
    session.run("jlpm", "install")
    session.install("-e", ".")

    session.run("jlpm", "test")

    with session.chdir("ui-tests"):
        session.run("jlpm", "install")
        session.run("jlpm", "playwright", "install")
        session.run("jlpm", "test")
