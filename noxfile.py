import nox
import nox.sessions

PACKAGE_FILES = ["chart.py", "noxfile.py"]


@nox.session(python="3.11")
def lint(session: nox.sessions.Session) -> None:
    session.install("-r", "requirements.txt")
    session.run("flake8", *PACKAGE_FILES)
    session.run("black", "--check", *PACKAGE_FILES)


@nox.session(python="3.11")
def typecheck(session: nox.sessions.Session) -> None:
    session.install("-r", "requirements.txt")
    session.run("mypy", *PACKAGE_FILES)


@nox.session(python="3.11")
def format(session: nox.sessions.Session) -> None:
    session.install("-r", "requirements.txt")
    session.run("isort", *PACKAGE_FILES)
    session.run("black", *PACKAGE_FILES)
