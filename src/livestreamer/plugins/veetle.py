from livestreamer.compat import urlparse
from livestreamer.exceptions import PluginError, NoStreamsError
from livestreamer.plugin import Plugin
from livestreamer.plugin.api import http
from livestreamer.stream import HTTPStream


class Veetle(Plugin):
    APIURL = "http://veetle.com/index.php/stream/ajaxStreamLocation/{0}/flash"

    @classmethod
    def can_handle_url(self, url):
        return "veetle.com" in url

    def _get_streams(self):
        parsed = urlparse(self.url)

        if parsed.fragment:
            channelid = parsed.fragment
        elif "/v/" in parsed.path:
            channelid = parsed.path.rpartition("/v/")[-1]
        else:
            channelid = parsed.path.rpartition("view/")[-1]

        if not channelid:
            raise NoStreamsError(self.url)

        channelid = channelid.lower().replace("/", "_")

        self.logger.debug("Fetching stream info")
        res = http.get(self.APIURL.format(channelid))
        json = http.json(res)

        if not isinstance(json, dict):
            raise PluginError("Invalid JSON response")
        elif not ("success" in json and "payload" in json):
            raise PluginError("Invalid JSON response")
        elif json["success"] == False:
            raise NoStreamsError(self.url)

        streams = {}
        streams["live"] = HTTPStream(self.session, json["payload"])

        return streams


__plugin__ = Veetle
