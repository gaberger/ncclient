# Copyright 2009 Shikhar Bhushan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import capabilities
import operations
import transport

OPERATIONS = {
    'get': operations.Get,
    'get-config': operations.GetConfig,
    'edit-config': operations.EditConfig,
    'copy-config': operations.CopyConfig,
    'validate': operations.Validate,
    'commit': operations.Commit,
    'discard-changes': operations.DiscardChanges,
    'delete-config': operations.DeleteConfig,
    'lock': operations.Lock,
    'unlock': operations.Unlock,
    'close_session': operations.CloseSession,
    'kill-session': operations.KillSession,
}

def connect_ssh(*args, **kwds):
    session = transport.SSHSession(capabilities.CAPABILITIES)
    session.load_system_host_keys()
    session.connect(*args, **kwds)
    return Manager(session)

connect = connect_ssh # default session type

class Manager:
    
    'Facade for the API'
    
    RAISE_ALL = 0
    RAISE_ERROR = 1
    RAISE_NONE = 2
    
    def __init__(self, session, rpc_error=Manager.RAISE_ERROR):
        self._session = session
        self._raise = rpc_error

    def do(self, op, *args, **kwds):
        op = OPERATIONS[op](self._session)
        reply = op.request(*args, **kwds)
        if not reply.ok:
            if self._raise == Manager.RAISE_ALL:
                raise reply.error
            elif self._raise == Manager.RAISE_ERROR:
                for error in reply.errors:
                    if error.severity == 'error':
                        raise error
        return reply
    
    def __enter__(self):
        pass
    
    def __exit__(self, *args):
        self.close()
        return False
    
    def _get(self, type, *args, **kwds):
        reply = self.do(type)
        return reply.data
    
    def locked(self, target):
        "For use with 'with'. target is the datastore, e.g. 'candidate'"
        return operations.LockContext(self._session, target)
    
    get = lambda self, *args, **kwds: self._get('get')
    
    get_config = lambda self, *args, **kwds: self._get('get-config')
    
    edit_config = lambda self, *args, **kwds: self.do('edit-config', *args, **kwds)
    
    copy_config = lambda self, *args, **kwds: self.do('copy-config', *args, **kwds)
    
    validate = lambda self, *args, **kwds: self.do('validate', *args, **kwds)
    
    commit = lambda self, *args, **kwds: self.do('commit', *args, **kwds)
    
    discard_changes = lambda self, *args, **kwds: self.do('discard-changes', *args, **kwds)
    
    delete_config = lambda self, *args, **kwds: self.do('delete-config', *args, **kwds)
    
    lock = lambda self, *args, **kwds: self.do('lock', *args, **kwds)
    
    unlock = lambda self, *args, **kwds: self.do('unlock', *args, **kwds)
    
    close_session = lambda self, *args, **kwds: self.do('close-session', *args, **kwds)
    
    kill_session = lambda self, *args, **kwds: self.do('kill-session', *args, **kwds)
    
    def close(self):
        try: # try doing it clean
            self.close_session()
        except:
            pass
        if self._session.connected: # if that didn't work...
            self._session.close()