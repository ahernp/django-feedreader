"""Local Server to return RSS feed data for unit testing"""
import http.server
import socketserver
import threading

PORT = 8081
TEST_RSS = b"""<?xml version="1.0" encoding="utf-8"?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
    <channel>
        <title>test feed</title>
        <link>http://example.com/test/</link>
        <description>Test Feed.</description>
        <atom:link href="http://example.com/test/feed/" rel="self"></atom:link>
        <lastBuildDate>Sun, 13 Apr 2014 09:33:47 +0000</lastBuildDate>
        <item>
            <title>Test Entry</title>
            <link>http://example.com/test1/</link>
            <description>&lt;h1 id="TEST1"&gt;Test One&lt;/h1&gt;</description>
            <pubDate>Sun, 13 Apr 2014 09:33:47 +0000</pubDate>
            <guid>http://example.com/test1/</guid>
        </item>
        <item>
            <title>Test Entry 2</title>
            <link>http://example.com/test2/</link>
            <description>&lt;h1 id="TEST2"&gt;Test Two&lt;/h1&gt;</description>
            <pubDate>Sun, 13 Apr 2014 09:33:47 +0000</pubDate>
            <guid>http://example.com/test2/</guid>
        </item>
    </channel>
</rss>"""


class Handler(http.server.SimpleHTTPRequestHandler):
    """Local Server to return RSS feed data"""

    def do_GET(self):
        """Construct a server response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/rss+xml')
        self.end_headers()
        # Can use self.path to choose data to return
        self.wfile.write(TEST_RSS)
        return

    def log_request(self, code):
        """Suppress display of status code messages on terminal"""
        pass


class TestServer(socketserver.TCPServer):
    allow_reuse_address = True


test_server = TestServer(('', PORT), Handler)


def setUpModule():
    """Start server to return test rss data"""
    thread = threading.Thread(target=test_server.serve_forever)
    thread.daemon = True
    thread.start()


def tearDownModule():
    """Stop server which returned test rss data"""
    test_server.shutdown()


if __name__ == '__main__':  # pragma: no cover
    test_server.serve_forever()
