from ncclient.xml_ import BASE_NS_1_0
from ncclient.operations.third_party.nexus.rpc import ExecCommand

from .default import DefaultDeviceHandler

class NetironDeviceHandler(DefaultDeviceHandler):
    def __init__(self, device_params):
        super(NetironDeviceHandler, self).__init__(device_params)

    def get_capabilities(self):
        c = super(NetironDeviceHandler, self).get_capabilities()
        c[0] = "urn:ietf:params:xml:ns:netconf:base:1.0"
	c[1] = "urn:ietf:params:netconf:base:1.1"
        c[2] = "urn:ietf:params:netconf:capability:writeable-running:1.0"
        return c

    def get_xml_base_namespace_dict(self):
        return { None : BASE_NS_1_0 }
    
    def handle_connection_exceptions(self, sshsession):
        return False
