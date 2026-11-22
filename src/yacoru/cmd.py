from __future__ import annotations

import subprocess


class Command:
    AND = ' && '
    OR = ' || '
    JOIN = '; '
    DEFAULT_ADD = AND

    def __init__(self, cmd_line: str = '', extra_paths=None):
        self.cmd_lines = []
        if extra_paths:
            self.add(f'export PATH={":".join(extra_paths)}:$PATH')
        if cmd_line:
            self.add(cmd_line)
        self.process = None
        self._output = None
        self._returncode = None

    @property
    def command(self):
        cmd = []
        if self.cmd_lines:
            cmd.append(self.cmd_lines[0][1])
            for cmd_line in self.cmd_lines[1:]:
                cmd.extend(cmd_line)
        return ''.join(cmd)

    @staticmethod
    def check_process(method):
        def wrapper(self, *args, **kwargs):
            if self._output is None:
                if self.process is None:
                    return None
                else:
                    if self.process.poll() is None:
                        return None
                    else:
                        self._output, _ = self.process.communicate()
                        self._returncode = self.process.returncode
            return method(self, *args, **kwargs)

        return wrapper

    @property
    @check_process
    def output(self):
        return self._output

    @property
    @check_process
    def returncode(self):
        return self._returncode

    @property
    def succeded(self):
        return self.returncode == 0

    @property
    def empty_output(self):
        return len(self.output) == 0

    def __repr__(self):
        return self.command

    def run(self, *, delay: float = 0, detach: bool = False) -> bool:
        if delay:
            self.cmd_lines.insert(0, (Command.DEFAULT_ADD, f'sleep {delay}'))
        # https://docs.python.org/3/library/subprocess.html#popen-objects
        self.process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            encoding='utf-8',
            start_new_session=detach,
        )
        if detach:
            return True
        self._output, _ = self.process.communicate()
        self._returncode = self.process.returncode

        return self.returncode == 0

    def add(self, cmd_line: str, cmd_join: str = '') -> None:
        cmd_join = cmd_join or Command.DEFAULT_ADD
        self.cmd_lines.append((cmd_join, cmd_line))

    def __add__(self, cmd_line: object) -> Command:
        if isinstance(cmd_line, str):
            return Command(cmd_line)
        else:
            raise TypeError('Command line must be a string')

    @check_process
    def get_num_lines_in_output(self) -> int | None:
        return len([line for line in self.output.split('\n') if line])

    @check_process
    def in_output(self, text: str, *, ignore_case=False) -> bool | None:
        if ignore_case:
            return text.lower() in self.output.lower()
        return text in self.output
