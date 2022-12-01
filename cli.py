import typer
from dotenv import load_dotenv

from xui import Xui, generate_password

load_dotenv()
app = typer.Typer(add_completion=False)


@app.command()
def setup_ssl(ctx: typer.Context):
    ctx.obj.setup_ssl()


@app.command()
def change_password(ctx: typer.Context):
    ctx.obj.change_password(new_password=generate_password())
    typer.echo(
        f"""##############
X-UI Login Info:
URL: {ctx.obj.host}
USER: {ctx.obj.user}
PASSWORD: {ctx.obj.password}
##############
    """
    )


@app.command()
def add_vmess(ctx: typer.Context, port: int, path: str):
    ctx.obj.add_vmess(port, path)


@app.command()
def add_vless_tls(ctx: typer.Context, port: int, path: str):
    ctx.obj.add_vless_tls(port, path)


@app.command()
def add_trojan(ctx: typer.Context, port: int):
    ctx.obj.add_trojan(port)


@app.callback()
def _main(
    ctx: typer.Context,
    ip: str = typer.Option(None, envvar="IP"),
    port: int = typer.Option(None, envvar="XPORT"),
    domain: str = typer.Option(None, envvar="DOMAIN"),
    remark: str = typer.Option("", envvar="REMARK"),
    user: str = typer.Option("admin", envvar="XUSER"),
    password: str = typer.Option("admin", envvar="XPASSWORD"),
    ssl_enabled: bool = typer.Option(False, envvar="SSL_ENABLED"),
    cert_path: str = typer.Option("/root/cert.crt", envvar="CERT_PATH"),
    private_path: str = typer.Option("/root/private.key", envvar="PRIVATE_PATH"),
):
    ctx.obj: Xui = Xui(
        ip=ip,
        port=port,
        domain=domain,
        remark=remark,
        user=user,
        password=password,
        ssl_enabled=ssl_enabled,
        cert_path=cert_path,
        private_path=private_path,
    )


if __name__ == "__main__":
    app()
