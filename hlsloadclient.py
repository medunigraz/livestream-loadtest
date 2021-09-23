import sys
import click
import streamlink
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from pebble import ProcessPool, ThreadPool
from functools import partial


@click.command()
@click.option("--event", help="URL to event viewer dispatcher.")
@click.option("--viewers", default=1, help="The number of parallel viewers to start.")
@click.option("--username", help="The username for viewer creation.")
@click.option("--password", help="The password for viewer creation.")
def main(event, viewers, username, password):
    if username and password:
        auth = HTTPBasicAuth(username, password)
    else:
        auth = None
    with ProcessPool(max_workers=viewers) as pp:
        return [
            p.result()
            for p in pp.map(
                partial(viewer, auth=auth), [event] * viewers, chunksize=1
            ).result()
        ]


def viewer(event, auth=None):
    try:
        resp = requests.post(event, auth=auth)
        resp.raise_for_status()
    except requests.HTTPError as e:
        print(e)
        return
    urls = resp.json().get("streams").values()

    with ThreadPool(max_workers=len(urls)) as tp:
        return [t.result() for t in tp.map(consume, urls, chunk_size=1).result()]


def consume(url):
    print(f"Consuming {url}")
    stream = streamlink.streams(url).get("best")
    start = datetime.now()
    size = 0
    with stream.open() as fd:
        while chunk := fd.read(4194304):
            size = size + len(chunk)
            print(".", end="")
            sys.stdout.flush()
    return datetime.now() - start, size


if __name__ == "__main__":
    main()
