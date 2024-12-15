import os

from dotenv import load_dotenv
from invoke import Context, task

load_dotenv()

@task
def prod_server(c: Context):
    c.run(
        f"uvicorn backend.src.main:app --host {os.getenv('API_HOST', '0.0.0.0')} --port {os.getenv('API_PORT', 8000)} --reload"
    )


@task
def release(c: Context):
    c.run("cz bump")
    c.run("git push --follow-tags")
