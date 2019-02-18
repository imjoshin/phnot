import email
import imaplib
import subprocess
import time
import os
import sys
import conf
import auth
import util
import parse
from entities import Notification

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
            self.last_diff_id = ids[-1]

            self.connection.select(self.task_label)
            ids = self._get_new_email_ids(-1)
            self.last_task_id = ids[-1]

        return self.connection

    def _get_new_email_ids(self, last_id):
        _, data = self.connection.search(None, 'ALL')
        str_ids = data[0].split()
        new_ids = [int(id) for id in str_ids if int(id) > int(last_id)]
        return new_ids

    def _get_new_email(self, last_id, open):
        new_ids = self._get_new_email_ids(last_id)

        if len(new_ids) == 0:
            return [], last_id

        ids = ",".join([str(id) for id in new_ids])
        typ, data = self.connection.fetch(ids, '(RFC822)' )
        new_mail = []

        for response_part in data:
            if isinstance(response_part, tuple):
                mail = email.message_from_string(response_part[1].decode())
                new_mail.append(mail)

        return new_mail, new_ids[-1]

    def get_diff_notifications(self, diff_ids):
        notifications, last_id = self._get_notifications(diff_ids, self.diff_label, self.last_diff_id, parse.DiffParser())
        self.last_diff_id = last_id
        return notifications

    def get_task_notifications(self, task_ids):
        notifications, last_id = self._get_notifications(task_ids, self.task_label, self.last_task_id, parse.TaskParser())
        self.last_task_id = last_id
        return notifications

    def _get_notifications(self, open_ids, label, last_id, parser):
        self.connection.select(label)
        new_mail, last_id = self._get_new_email(last_id, open)
        notifications = []

        for mail in new_mail:
            phab_id = util.regex_phab_id(mail['subject'])
            phab_desc = util.get_regex_match(mail['subject'], "[DT][0-9]+: (.*)")

            if phab_id in open_ids:
                body = mail.get_payload(decode=True)
                if mail.is_multipart():
                    body = ''.join([str(p) for p in body.get_payload(decode=True)])

                parsed = parser.parse(phab_id, phab_desc, body.decode())
                notifications = notifications + parsed

        return notifications, last_id
