from colors import Colors
from entities import Diff, Task
import subprocess
import conf
import util

class ConsoleManager:
    def update_view(self, diffs, tasks):
        task_header = self._format_header("Phab Tasks", Colors.FG.magenta)
        diff_header = self._format_header("Open Diffs", Colors.FG.yellow)

        task_str = '\n'.join([self._format_task(task) for task in tasks])
        diff_str = '\n'.join([self._format_diff(diff) for diff in diffs])

        str = "{}\n\n{}\n\n\n{}\n\n{}".format(task_header, task_str, diff_header, diff_str)
        bottom_pad = (self._get_terminal_height() - str.count('\n') - 2) * '\n'

        self._empty_terminal()
        print(str + bottom_pad)

    def _get_terminal_height(self):
        p = subprocess.Popen('tput lines', stdout=subprocess.PIPE, shell=True)
        line_str, err = p.communicate()
        return int(line_str)

    def _empty_terminal(self):
        print(chr(27) + "[2J")

    def _format_diff(self, diff):
        id = "{}{}{}".format(Colors.bold, diff.id, Colors.reset)
        status = " " if diff.status not in conf.DIFF_STATUS_MAP else conf.DIFF_STATUS_MAP[diff.status]
        return "{} {}  {}".format(id, status, diff.description)

    def _format_task(self, task):
        id = "{}{}{}".format(Colors.bold, task.id, Colors.reset)
        priority = " " if task.priority not in conf.TASK_PRIORITY_MAP else conf.TASK_PRIORITY_MAP[task.priority]
        return "{} {}  {}".format(id, priority, task.description)

    def _format_header(self, str, color):
        return "{}{}===={}{} {} {}===={}".format(
            Colors.bold, color, Colors.reset, Colors.bold, str, color, Colors.reset)

    def get_diffs(self):
        cmd = 'cd {}; duoconnect -arc -relay phab.duosec.org arc list'.format(conf.REPO_DIR)
        # cmd = 'cat ~/src/list.txt'
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        diff_str, err = p.communicate()

        has_diffs = bool(util.regex_phab_id(diff_str.decode()))
        if not has_diffs:
            return []

        diffs = []
        for line in diff_str.decode().split('\n'):
            if line.strip() == "":
                break

            diffs.append(Diff(line))

        return diffs

    def get_tasks(self):
        cmd = 'cd {}; duoconnect -arc -relay phab.duosec.org arc tasks'.format(conf.REPO_DIR)
        # cmd = 'cat ~/src/tasks.txt'
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        task_str, err = p.communicate()

        has_tasks = bool(util.regex_phab_id(task_str.decode()))
        if not has_tasks:
            return []

        tasks = []
        for line in task_str.decode().split('\n'):
            if line.strip() == "":
                break

            tasks.append(Task(line))

        return tasks
