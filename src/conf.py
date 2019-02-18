# -*- coding: UTF-8 -*-

# mail settings
MAIL_DOMAIN = "@duosecurity.com"
MAIL_DIFF_LABEL = "Differential"
MAIL_TASK_LABEL = "Maniphest"
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT = 993

# Misc
REPO_DIR = "~/src/trustedpath"
IGNORE_MY_ACTIONS = True

# Notification settings
METHODS = [
    'slack'
]
SLACK_USER_ID = "DFESEUQTY"
SLACK_BOT_USER = "Phabricator"
SLACK_BOT_ICON = ":phabricator:"

# Parsing settings
PRIORITIES = "Unbreak Now!|Needs Triage|Wishlist|High|Normal|Low"

DIFF_STATUS_MAP = {
    "Needs Revision": "\033[31m✗\033[0m",
    "Needs Review": "\033[33m⌽\033[0m",
    "Accepted": "\033[32m✔\033[0m"
}

TASK_PRIORITY_MAP = {
    "Unbreak Now!": "\033[31m⚠\033[0m",
    "Needs Triage": "\033[36m↻\033[0m",
    "Wishlist": "\033[33m★\033[0m",
    "High": "\033[31m⬆\033[0m",
    "Normal": "\033[33m▬\033[0m",
    "Low": "\033[32m⬇\033[0m"
}

IGNORED_USERS = ["-bot"]
