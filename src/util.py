import re
import auth
import conf

def should_ignore_username(username):
    ignore_due_to_current_user = conf.IGNORE_MY_ACTIONS and username == auth.MAIL_USER
    return username is None or ignore_due_to_current_user or sum([1 for user in conf.IGNORED_USERS if user in username])

def regex_phab_id(subject):
    return get_regex_match(subject, "([DT][0-9]{4,})")

def replace_phab_ids_with_slack_links(subject):
    return re.sub(r'([DT][0-9]{4,})', r'<https://phab.duosec.org/\1|\1>', subject)

def get_regex_match(subject, regex_str, match_num=1):
    regex = re.compile(regex_str)
    match = regex.search(subject)
    return match.group(match_num) if match else None
