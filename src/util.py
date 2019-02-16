import re

def regex_diff_id(subject):
    return get_regex_match(subject, "(D[0-9]{4,})")

def regex_task_id(subject):
    return get_regex_match(subject, "(T[0-9]{4,})")

def get_regex_match(subject, regex_str, match_num=1):
    regex = re.compile(regex_str)
    match = regex.search(subject)
    return match.group(match_num) if match else None
