# Yet Another Command Runner

Yacoru (pronounced `/ˈja.ko.ɾu/`) provides artefacts for **running commands on terminal** in a very easy way.

> [!NOTE]
> At this moment only _UNIX-like_ platforms are supported.

## Installation

Just install it from your favourite package manager:

```console
$ pip install yacoru
or ...
$ uv add yacoru
```

## Usage

This package provides an «OOP like API» to run commands on terminal:

```pycon
>>> from yacoru import Command

>>> cmd = Command('whoami')

>>> cmd
whoami

>>> cmd.run()  # True if returncode == 0
True

>>> cmd.output
'sdelquin\n'

>>> cmd.returncode
0
```

You can also **add a bunch of commands** step by step:

```pycon
>>> cmd = Command()

>>> cmd.add('whoami')
>>> cmd.add('head -2 pyproject.toml')
>>> cmd.add('du -sh')

>>> cmd
whoami && head -2 pyproject.toml && du -sh

>>> cmd.run()
True

>>> cmd.output
'sdelquin\n[project]\nname = "yacoru"\n 51M\t.\n'

>>> print(cmd.output)
sdelquin
[project]
name = "yacoru"
 51M	.
```

You can **detach commands** to run in a different process:

```pycon
>>> cmd = Command()

>>> cmd.add('sleep 5')
>>> cmd.add('whoami')

>>> cmd.run(detach=True)
True

>>> cmd.output
'sdelquin\n'

>>> cmd.returncode
0

>>> cmd.succeded
True
```

## API

Find the full API documentation [here](https://yacoru.matraka.es).

## Changelog

Check out the Changelog [here](https://github.com/sdelquin/yacoru/blob/main/CHANGELOG.md).
