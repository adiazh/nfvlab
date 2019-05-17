from charmhelpers.core.hookenv import (
    action_get,
    action_fail,
    action_set,
    status_set,
)
from charms.reactive import (
    clear_flag,
    set_flag,
    when,
    when_not,
)

import charms.sshproxy

@when_not('ffmpeg.installed')
def install_ffmpeg_proxy_charm():
    set_flag('ffmpeg.installed')
    status_set('active', 'Ready!')

@when('actions.server')
def server():
    err = ''
    try:
        cmd = '/usr/local/bin/wrapper.sh'
        result, err = charms.sshproxy._run(cmd)
    except:
        action_fail('command failed:' + err)
    else:
        action_set({'output': result})
    finally:
        clear_flag('actions.touch')