import util
import auth
import conf

class Diff:
    def __init__(self, diff_str):
        self.id = util.get_regex_match(diff_str, "(D[0-9]+):")
        self.description = util.get_regex_match(diff_str, "D[0-9]+: (.*)").strip()
        self.status = util.get_regex_match(diff_str, "^\* ([a-zA-Z ]+) D").strip()

class Task:
    def __init__(self, task_str):
        self.id = util.get_regex_match(task_str, "(T[0-9]+)")
        self.description = util.get_regex_match(task_str, "T[0-9]+ (.+)\s\s+({})".format(conf.PRIORITIES)).strip()
        self.priority = util.get_regex_match(task_str, "T[0-9]+ .+\s\s+({})\s\s+".format(conf.PRIORITIES)).strip()
        self.status = util.get_regex_match(task_str, "T[0-9]+ .+\s\s+({})\s\s+(.*)".format(conf.PRIORITIES), match_num=2).strip()

class ArcNotification:
    def __init__(self, id, description, message):
        self.id = id
        self.description = description
        self.message = message

class MailNotification:
    def __init__(self, mail_user, mail_subject):
        if auth.MAIL_USER in mail_user:
            self.user = "You"
        else:
            self.user = util.get_regex_match(mail_user, "\((.*)\)")

        self.action = util.get_regex_match(mail_subject, "\[Differential\] \[([a-zA-Z ]*)\]").lower()
        self.id = util.get_regex_match(mail_subject, "(D[0-9]+):")
        self.description = util.get_regex_match(mail_subject, "D[0-9]+: (.*)")
        self.message = "{} {} {}".format(self.user, self.action, self.id)

class Notification:
    def __init__(self, id, description, short_message, long_message):
        self.id = id
        self.description = description
        self.short_message = short_message
        self.long_message = long_message
