import re
import requests

from hamper.interfaces import ChatPlugin


class Tinyurl(ChatPlugin):
    name = 'tinyurl'
    priority = 2

    # Regex is taken from:
    # http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    regex = ur"""
    (                       # Capture 1: entire matched URL
      (?:
        (?P<prot>https?://)     # http or https protocol
        |                       #   or
        www\d{0,3}[.]           # "www.", "www1.", "www2." ... "www999."
        |                           #   or
        [a-z0-9.\-]+[.][a-z]{2,4}/  # looks like domain name
                                    # followed by a slash
      )
      (?:                                  # One or more:
        [^\s()<>]+                         # Run of non-space, non-()<>
        |                                  # or
        \(([^\s()<>]+|(\([^\s()<>]+\)))*\) # balanced parens, up to 2 levels
      )+
      (?:                                  # End with:
        \(([^\s()<>]+|(\([^\s()<>]+\)))*\) # balanced parens, up to 2 levels
        |                                  # or
        [^\s`!()\[\]{};:'".,<>?]           # not a space or one of
                                           # these punct chars
      )
    )
    """

    def setup(self, loader):
        self.regex = re.compile(self.regex, re.VERBOSE | re.IGNORECASE | re.U)
        self.api_url = 'http://tinyurl.com/api-create.php?url={0}'
        # If an exclude value is found in the url
        # it will not be shortened
        self.excludes = ['imgur.com', 'gist.github.com', 'pastebin.com']
        # Make sure they've configured the tinyurl config values.

    def message(self, bot, comm):
        match = self.regex.search(comm['message'])
        # Found a url
        if match:
            # base url isn't % encoded, python 2.7 doesn't do this well, and I
            # couldn't figure it out.
            long_url = match.group(0)

            # Only shorten urls which are longer than a tinyurl url (12 chars)
            if len(long_url) <= 30:
                return False

            # Don't shorten url's which are in the exclude list
            for item in self.excludes:
                if item in long_url.lower():
                    return False

            # tinyurl requires a valid URI
            if not match.group('prot'):
                long_url = 'http://' + long_url

            # tinyurl requires valid % encoded urls
            resp = requests.get(self.api_url.format(long_url))
            data = resp.content

            if resp.status_code == 200:
                bot.reply(
                    comm,
                    "{0}'s shortened url is {1}" .format(comm['user'], data)
                )
            else:
                bot.reply(comm, "This command is broken!")

        # Always let the other plugins run
        return False


tinyurl = Tinyurl()
