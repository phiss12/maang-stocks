import os

from dotenv import load_dotenv
from invoke import Context, task

load_dotenv()

@task
def prod_server(c: Context):
    c.run(
        f"uvicorn backend.src.main:app --host {os.getenv('API_HOST')} --port 5000 --reload"
    )


@task
def release(c: Context):
    c.run("cz bump")
    c.run("git push --follow-tags")