from __future__ import annotations

import subprocess
from functools import wraps


class Command:
    """Command object."""

    AND = ' && '
    OR = ' || '
    JOIN = '; '
    DEFAULT_ADD = AND

    def __init__(self, cmd_line: str = '', extra_paths=None):
        """
        Build a Command object.
        :param cmd_line: Command line (snippet) to be executed.
        :param extra_paths: Extra dirs to add to PATH.
        :return: A new Command object.
        """
        self.cmd_lines = []
        if extra_paths:
            self.add(f'export PATH={":".join(extra_paths)}:$PATH')
        if cmd_line:
            self.add(cmd_line)
        self.process = None
        self._output = None
        self._returncode = None

    @property
    def command(self) -> str:
        """
        :return: Whole command (joining all command lines).
        """
        cmd = []
        if self.cmd_lines:
            cmd.append(self.cmd_lines[0][1])
            for cmd_line in self.cmd_lines[1:]:
                cmd.extend(cmd_line)
        return ''.join(cmd)

    @staticmethod
    def check_process(method):

        @wraps(method)
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
    def output(self) -> str | None:
        """
        :return: Process output or None if the process has not finished yet.
        In case of errors, it stores process errors.
        """
        return self._output

    @property
    @check_process
    def returncode(self) -> int | None:
        """
        :return: Return code of the command or `None` if the process has not finished yet.
        """
        return self._returncode

    @property
    def succeded(self) -> bool:
        """
        :return: `True` if the command finished with no errors or `False` otherwise.
        """
        return self.returncode == 0

    @property
    def empty_output(self) -> bool:
        """
        :return: `True` if the command output has no content or `False` otherwise.
        """
        return len(self.output) == 0

    def __repr__(self):
        """
        :return: The whole command to be executed.
        @public
        """
        return self.command

    def run(self, *, delay: float = 0, detach: bool = False) -> bool | None:
        """
        Run the command.
        :param delay: Time to delay (in seconds) before running the command.
        :param detach: `True` for detaching the process or `False` otherwise.
        :return: `True` if the process finished successfully.
        `False` if the process finished with errors.
        `None` if the process was detached.
        """
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
            return None
        self._output, _ = self.process.communicate()
        self._returncode = self.process.returncode

        return self.returncode == 0

    def add(self, cmd_line: str, cmd_join: str = '') -> None:
        """
        Add the given command line to the current Command.
        :param cmd_line: Command line to be added.
        :param cmd_join: Join operator.
        """
        cmd_join = cmd_join or Command.DEFAULT_ADD
        self.cmd_lines.append((cmd_join, cmd_line))

    def __add__(self, cmd_line: object) -> Command:
        """
        :return: Command with the given command line added to the existing ones.
        @public
        """
        if isinstance(cmd_line, str):
            return Command(cmd_line)
        else:
            raise TypeError('Command line must be a string')

    @check_process
    def get_num_lines_in_output(self) -> int | None:
        """
        :return: Number of lines in output or `None` if the process has not finished yet.
        """
        return len([line for line in self.output.split('\n') if line])

    @check_process
    def in_output(self, text: str, *, ignore_case=False) -> bool | None:
        """
        Check if given text appears on process output.
        :param text: The text to check.
        :param ignore_case: Ignore case on checking.
        :return: `True` if text is present in process output.
        `False` if text is not present in process output.
        `None` if the process has not finished yet.
        """
        if ignore_case:
            return text.lower() in self.output.lower()
        return text in self.output
