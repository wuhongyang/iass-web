from Gmetad.gmetad_confable import GmetadConfable
import importlib


def get_rrd_store(impid, cfgid="rrd-store"):
    ''' Get the specified RRD store from the factory via cfgid '''
    store_module = importlib.import_module("Gmetad.rrd.stores." + impid + "_store")
    return store_module.get_rrd_store(impid, cfgid)

class RRDStore(GmetadConfable):

    def getHostInfo(self, hostKey):
        raise Exception, 'No definition provided for RRDStore "getHostInfo" method.'