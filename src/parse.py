import util
import re
import conf
import auth
from bs4 import BeautifulSoup
import soupsieve
from entities import Notification

class DiffParser():
    def _get_new_revision(self, id, desc, body):
        ret = None
        username = util.get_regex_match(body, ">([^>]+) created this revision")

        if not util.should_ignore_username(username):
            short_message = "{} created a new revision - {}: {}.".format(username, id, desc)
            long_message = "@" + short_message
            ret = Notification(id, desc, short_message, long_message)

        return ret

    def _get_request_changes(self, id, desc, body):
        ret = None
        username = util.get_regex_match(body, ">([^>]+) requested changes to this revision.")

        if not util.should_ignore_username(username):
            short_message = "{} requested changes to {}.".format(username, id)
            long_message = "@{} requested changes to {}: {}.".format(username, id, desc)
            ret = Notification(id, desc, short_message, long_message)
        elif 'This revision now requires changes to proceed' in body:
            short_message = "{} requires changes to proceed.".format(id)
            long_message = "*{}: {}* requires changes to proceed.".format(id, desc)
            ret = Notification(id, desc, short_message, long_message)

        return ret

    def _get_comments(self, id, desc, body):
        ret = None
        username = util.get_regex_match(body, ">([^>]+) added a comment.")

        if not util.should_ignore_username(username):
            short_message = "{} added a comment to {}.".format(username, id)
            long_message = "@{} added a comment to *{}: {}*.".format(username, id, desc)
            soup = BeautifulSoup(body, 'html.parser')
            paragraphs = soup.select("div > div > p")
            if len(paragraphs) > 0 and len(paragraphs[0].parent.text) > 0:
                long_message = "{}\n```{}```".format(long_message, paragraphs[0].parent.text)

            ret = Notification(id, desc, short_message, long_message)

        return ret

    def _get_inline_comments(self, id, desc, body):
        ret = None
        username = util.get_regex_match(body, ">([^>]+) added inline comments")

        # found inline comments
        if not util.should_ignore_username(username):
            short_message = "{} added inline comments to {}.".format(username, id)
            long_message = "@{} added inline comments to *{}: {}*.".format(username, id, desc)
            soup = BeautifulSoup(body, 'html.parser')
            comment_divs = soup.select("div > strong + div > div > div > div")
            files = {}
            comments = []

            # try to find any actual comments
            for div in comment_divs:
                # filter out those with color - those are old comments
                comments = [comment.text for comment in div.select("p") if 'color' not in comment.parent['style']]

            for comment in comments:
                long_message = "{}\n```{}```".format(long_message, comment)

            ret = Notification(id, desc, short_message, long_message)

        return ret

    def _get_ready_to_land(self, id, desc, body):
        ret = None

        if 'This revision is now accepted and ready to land.' in body:
            short_message = "{} is now accepted and ready to land.".format(id)
            long_message = "*{}: {}* is now accepted and ready to land.".format(id, desc)
            ret = Notification(id, desc, short_message, long_message)

        return ret

    def parse(self, id, desc, body):
        notifications = [
            self._get_inline_comments(id, desc, body),
            self._get_comments(id, desc, body),
            self._get_request_changes(id, desc, body),
            self._get_ready_to_land(id, desc, body),
        ]

        return [n for n in notifications if n is not None]

class TaskParser():
    def _get_comments(self, id, desc, body):
        ret = None
        username = util.get_regex_match(body, ">([^>]+) added a comment.")

        if not util.should_ignore_username(username):
            short_message = "{} added a comment to {}.".format(username, id)
            long_message = "@{} added a comment to *{}: {}*.".format(username, id, desc)
            soup = BeautifulSoup(body, 'html.parser')
            paragraphs = soup.select("div > div > p")
            if len(paragraphs) > 0 and len(paragraphs[0].parent.text) > 0:
                long_message = "{}\n```{}```".format(long_message, paragraphs[0].parent.text)

            ret = Notification(id, desc, short_message, long_message)

        return ret

    def _get_task_move(self, id, desc, body):
        ret = None
        username = util.get_regex_match(body, ">([^>]+) moved this task")
        movement = util.get_regex_match(body, "moved this task ([^\.]+)")

        if not util.should_ignore_username(username):
            short_message = "{} moved {} {}.".format(username, id, movement)
            long_message = "@{} moved *{}: {}* {}.".format(username, id, desc, movement)
            ret = Notification(id, desc, short_message, long_message)

        return ret

    def parse(self, id, desc, body):
        notifications = [
            self._get_comments(id, desc, body),
            self._get_task_move(id, desc, body),
        ]

        return [n for n in notifications if n is not None]
