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

    def get_notifications(self, diffs, tasks):
        diff_notifications = self._get_arc_notifications(self.last_diffs, diffs, "Opened", "Landed")
        task_notifications = self._get_arc_notifications(self.last_tasks, tasks, "Assigned", "Closed")
        mail_notifications = self.mail.get_new_notifications(diffs)

        self.last_diffs = diffs
        self.last_tasks = tasks

        return diff_notifications + task_notifications + mail_notifications

    def _get_arc_notifications(self, prev, cur, new_verb, old_verb):
        notifications = []

        prev_ids = [a.id for a in prev]
        cur_ids = [a.id for a in cur]

        same = [a for a in cur if a.id in prev_ids]
        new = [a for a in cur if a.id not in prev_ids]
        closed = [a for a in prev if a.id not in cur_ids]

        for a in new:
            notifications.append(ArcNotification(a.id, a.description, "{} {}".format(new_verb, a.id)))
        for a in closed:
            notifications.append(ArcNotification(a.id, a.description, "{} {}".format(old_verb, a.id)))

        for current in same:
            attrs = [a for a in dir(current) if not a.startswith('_')]
            previous = next(a for a in prev if a.id == current.id)
            changes = []

            for attr in attrs:
                if getattr(current, attr) != getattr(previous, attr):
                    changes.append(attr)

            if len(changes) > 0:
                msgs = []
                for change in changes:
                    msgs.append("Changed {} from \"{}\" to \"{}\"".format(change, getattr(previous, change), getattr(current, change)))
                notifications.append(ArcNotification(current.id, current.description, '\n'.join(msgs)))

        return notifications

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
