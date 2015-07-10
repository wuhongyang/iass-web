from gmetad_config import getConfig


class GmetadConfable:
    ''' This is the base class for all gmetad configurable components. '''

    def __init__(self, impid, cfgid=None):
        # All method instances are initialized with a module id that should match a section id
        # found in the configuration file.
        self.cfgid = impid
        if cfgid is not None:
            self.cfgid += '.' + cfgid

        # Initialize the default values of method configs
        self.cfg = None
        self.initConfDefaults()

        # Initialize the config handlers
        self.cfgHandlers = None
        self.initConfHandlers()

        # Parse the config of alarm method
        self._parseConfig(getConfig().getSection(impid))

        if cfgid is not None:
            self._parseConfig(getConfig().getSection(impid + '.' + cfgid))

    def _parseConfig(self, cfgdata):
        if cfgdata is None:
            return
        '''Should be overridden by subclasses to parse configuration data, if any.'''
        for confKey, args in cfgdata:
            if self.cfgHandlers.has_key(confKey):
                self.cfgHandlers[confKey](args)

    def initConfDefaults(self):
        '''Init the default values of configs'''
        raise Exception, 'No definition provided for plugin "initConfDefaults" method.'

    def initConfHandlers(self):
        '''Init the handler array of configs'''
        raise Exception, 'No definition provided for plugin "initConfHandlers" method.'

    def start(self):
        '''Called by the engine during initialization to get the plugin going.  Must
        be overridden by subclasses.'''
        pass

    def stop(self):
        '''Called by the engine during shutdown to allow the plugin to shutdown.  Must
        be overridden by subclasses.'''
        pass

