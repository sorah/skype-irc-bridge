# irc <-> skype bridge

Customized version of [takano32/skype-bridge/Skype4Py](https://github.com/takano32/skype-bridge/tree/master/Skype4Py/IRC)

## Supported dependencies

- Python 2.7.5
- Xvfb
- irc == 8.5.3
- Skype4Py == 1.0.35
- PyGTK == 2.24.0
- honcho == 0.4.2
- configobj == 4.7.2

## Setup

    $ PYTHON=python2.7 VIRTUALENV_CMD=virtualenv-python2.7 ./setup.sh
    $ vim bridge.conf
    $ ./start.sh

(Install PyGTK before run ./setup.sh)

## Configuration

```
[skype]
xmlrpc_port = 12861
xmlrpc_host = localhost

[irc]
xmlrpc_port = 12860
xmlrpc_host = localhost
dump_all_notification = true # if dump_all_notification key exists, will dump all notification to default_channel
irc_with_nick = true # if irc_with_nick key exists, will bridge to skype with nick in IRC
default_channel = '#skype-bridge'
nick = 'skype'
host = 'localhost'
port = 6667

[configname]
skype = "#chatroom/$id"
irc   = "#myskyperoom"

[configname2]
skype = "#chatroom/$id"
irc = "#test-skype"
...
```

You can get skype chatroom id in default_channel.

## License

    https://github.com/takano32/skype-bridge/tree/master/Skype4Py/IRC
    Copyright (C) 2013  takano32 <tak at no32.tk>, sorah <her at sorah.jp>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

http://twitter.com/takano32/status/391408176693657600
