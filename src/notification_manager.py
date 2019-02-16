import conf
import subprocess
import json
import os
import util

class NotificationManager:
    def __init__(self, mail, console):
        self.mail = mail
        self.console = console
        self.last_diffs = console.get_diffs()
        self.last_tasks = console.get_tasks()

    def post_notification(self, notification):
        if 'apple' in conf.METHODS:
            self._post_to_applescript(notification)
        if 'slack' in conf.METHODS:
            self._post_to_slack(notification)

    def _post_to_applescript(self, notification):
        title = "{}: {}".format(notification.id, notification.description)
        message = notification.short_message.replace('"', '\\\"')
        cmd = "osascript -e 'display notification \"{}\" with title \"{}\"'".format(message, title)
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

    def _post_to_slack(self, notification):
        message = util.replace_phab_ids_with_slack_links(notification.long_message)
        data = {
            'channel': conf.SLACK_USER_ID,
            'text': message,
            'username': 'Phabricator',
            'link_names': True
        }

        cmd = "curl -X POST -H 'Content-type: application/json' --data '{}' {}".format(json.dumps(data), os.environ['PHNOT_SLACK_HOOK'])
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
