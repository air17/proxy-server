import re

import pytest
from aiohttp import web

from main import Proxy

hacker_news = Proxy("https://news.ycombinator.com", f"http://127.0.0.1:8000")


def test_tm_sign_added_correctly():
    document = \
        """
        <html>
        <head><title>Tests passed</title></head>
        <body>
        <div>
        Those test suites passed tests successfully
        <select><option>Yes</option</select>
        </div>
        </body>
        </html>
        """
    modified_document = hacker_news.add_trademark(document)
    assert len(re.findall(r"™", modified_document)) == 3


@pytest.mark.asyncio
async def test_server_response_is_ok(aiohttp_client):
    app = web.Application()
    app.router.add_get("/{path:.*}", hacker_news.proxify)

    client = await aiohttp_client(app)
    resp = await client.get('/')

    assert resp.status == 200

    text = await resp.text()
    assert 'Hacker™ News' in text
