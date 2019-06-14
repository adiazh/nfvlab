from charmhelpers.core.hookenv import (
    action_fail,
    action_get,
    action_set,
    status_set,
)
from charms.reactive import (
    when,
    clear_flag,
    set_flag,
    when_not,
)
import charms.sshproxy


@when('actions.updateall')
def do_updateall():
    err = ''
    try:
        cmd = "sudo apt-get update &&"
        cmd += "echo updated > /tmp/updated"
        result, err = charms.sshproxy._run(cmd)
    except:
        action_fail('command failed: ' + err)
    else:
        action_set({'output': result})
    finally:
        clear_flag('actions.updateall')


@when('actions.installweb')
def do_installweb():
    err = ''
    try:
        packagename = action_get('packagename')
        #cmd = ['sudo apt-get install -y {}'.format(packagename)]
        cmd = "sudo apt-get -y lighttpd"
        result, err = charms.sshproxy._run(cmd)
    except:
        action_fail('command failed: ' + err)
    else:
        action_set({'output': result})
    finally:
        clear_flag('actions.installweb')
