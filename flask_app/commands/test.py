from flask import current_app


@current_app.cli.command("test1")
def test1():
    print("test1")
    pass
