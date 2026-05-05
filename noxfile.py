import nox


@nox.session(venv_backend="uv")
def python(session):
    session.env["MATURIN_PEP517_ARGS"] = "--profile=dev"
    session.install(".[dev]")
    session.run("pytest")
