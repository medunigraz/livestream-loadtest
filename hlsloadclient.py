import click
import streamlink
import requests
from datetime import datetime
from pebble import ProcessPool, ThreadPool


@click.command()
@click.option('--event', help='URL to event viewer dispatcher.')
@click.option('--viewers', default=1, help='The number of parallel viewers to start.')
def main(event, viewers):
    with ProcessPool(max_workers=viewers) as pp:
        return [p.result() for p in pp.map(viewer, [event] * viewers, chunksize=1)]


def viewer(event):
    try:
        resp = requests.put(event)
        resp.raise_for_status()
    except requests.HTTPError as e:
        # TODO: Bail out because we could no create a viewer.
        return
    url = resp.json().get("url")
    streams = streamlink.streams(url)

    with ThreadPool(max_workers=len(streams)) as tp:
        return [t.result() for t in tp.map(consume, streams, chunk_size=1)]


def consume(stream, chunk_size=4096):
    start = datetime.now()
    size = 0
    with stream.open() as fd:
        while chunk := fd.read(chunk_size):
            size = size + len(chunk)
    return datetime.now() - start, size


if __name__ == "__main__":
    main()
