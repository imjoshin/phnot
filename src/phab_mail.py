import email
import imaplib
import subprocess
import time
import os
import sys
import conf
import auth
import util
from entities import Diff, Task, ArcNotification, MailNotification, Notification

class PhabMail:
    def __init__(self, email, password, diff_label, task_label):
        self.email = email
        self.password = password
        self.diff_label = diff_label
        self.task_label = task_label
        self.last_diff_id = -1
        self.last_task_id = -1
        self.connection = None

    def connect(self):
        if not self.connection:
            self.connection = imaplib.IMAP4_SSL(conf.SMTP_SERVER)
            self.connection.login(self.email, self.password)

            self.connection.select(self.diff_label)
            ids = self._get_new_email_ids(-1)
            self.last_diff_id = int(ids[-1]) - 100

            self.connection.select(self.task_label)
            ids = self._get_new_email_ids(-1)
            self.last_task_id = int(ids[-1]) - 100

        return self.connection

    def _get_new_email_ids(self, last_id):
        _, data = self.connection.search(None, 'ALL')
        str_ids = data[0].split()
        new_ids = [id for id in str_ids if int(id) > last_id]
        return new_ids

    def _get_new_email(self, last_id, open):
        new_ids = self._get_new_email_ids(last_id)

        if len(new_ids) == 0:
            return [], last_id

        filter_ids = [o.id for o in open]
        ids = ','.join(new_ids)
        typ, data = self.connection.fetch(ids, '(RFC822)' )
        new_mail = []

        for response_part in data:
            if isinstance(response_part, tuple):
                mail = email.message_from_string(response_part[1])
                new_mail.append(mail)

        return new_mail, new_ids[-1]

    def get_diff_notifications(self, diffs, parser):
        diff_ids = [diff.id for diff in diffs]
        self.connection.select(self.diff_label)
        new_mail, last_id = self._get_new_email(self.last_diff_id, diffs)
        notifications = []

        for mail in new_mail:
            should_ignore_subject = sum([1 for sub in conf.IGNORED_SUBJECTS if sub in mail['subject']])
            should_ignore_user = sum([1 for sub in conf.IGNORED_USERS if sub in mail['from']])
            if should_ignore_subject or should_ignore_user:
                continue

            diff_id = util.regex_diff_id(mail['subject'])
            print(mail.get_payload(decode=True), "\n\n\n\n")

            if diff_id in diff_ids:
                notifications.append(mail['subject'])

        self.last_diff_id = last_id

        return notifications
