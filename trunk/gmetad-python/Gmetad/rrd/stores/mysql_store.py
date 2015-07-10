from Gmetad.rrd.rrd_store import RRDStore
import mysql.connector as mdb
from mysql.connector import errorcode
import logging

def get_rrd_store(impid="mysql", cfgid="rrd-store"):
    ''' Get the specified alert method from the factory via cfgid '''
    return MysqlStore(impid, cfgid)

class MysqlStore(RRDStore):
    ''' The RRD store class implemented via MySQL '''

    MYSQL_HOST = 'host'             # The host of MySQL
    MYSQL_PORT = 'port'             # The port of MySQL
    MYSQL_DB = 'db'                 # The database in MySQL
    MYSQL_USER = 'user'             # The user to connect MySQL
    MYSQL_PASS = 'pass'             # The password to connect MySQL

    _cfgDefaults = {
        MYSQL_HOST: '127.0.0.1',
        MYSQL_PORT: 3306,
        MYSQL_DB: None,
        MYSQL_USER: 'root',
        MYSQL_PASS: None,
    }

    def initConfDefaults(self):
        self.cfg = MysqlStore._cfgDefaults

    def initConfHandlers(self):
        '''Init the handler array of configs'''
        self.cfgHandlers = {
            MysqlStore.MYSQL_HOST: self._parseMysqlHost,
            MysqlStore.MYSQL_PORT: self._parseMysqlPort,
            MysqlStore.MYSQL_DB: self._parseMysqlDB,
            MysqlStore.MYSQL_USER: self._parseMysqlUser,
            MysqlStore.MYSQL_PASS: self._parseMysqlPass,
        }

    def _parseMysqlHost(self, arg):
        ''' Parse the Mysql host. '''
        self.cfg[MysqlStore.MYSQL_HOST] = arg.strip().strip('"')

    def _parseMysqlPort(self, arg):
        ''' Parse the Mysql port. '''
        self.cfg[MysqlStore.MYSQL_PORT] = arg.strip().strip('"')

    def _parseMysqlDB(self, arg):
        ''' Parse the Mysql port. '''
        self.cfg[MysqlStore.MYSQL_DB] = arg.strip().strip('"')

    def _parseMysqlUser(self, arg):
        ''' Parse the Mysql port. '''
        self.cfg[MysqlStore.MYSQL_USER] = arg.strip().strip('"')

    def _parseMysqlPass(self, arg):
        ''' Parse the Mysql port. '''
        self.cfg[MysqlStore.MYSQL_PASS] = arg.strip().strip('"')

    def _connect(self):
        try:
            _mdb = mdb.connect(
                host=self.cfg[MysqlStore.MYSQL_HOST],
                port=self.cfg[MysqlStore.MYSQL_PORT],
                database=self.cfg[MysqlStore.MYSQL_DB],
                user=self.cfg[MysqlStore.MYSQL_USER],
                password=self.cfg[MysqlStore.MYSQL_PASS],
            )
            return _mdb
        except mdb.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exists")
            else:
                print(err)
            raise

    def getHostInfo(self, hostKey):
        ''' Get the host information from mysql-server '''
        _mdb = self._connect()
        cursor = _mdb.cursor()
        query = "SELECT user_id as user, project_id as dept FROM mappings WHERE fixed_ip=%(fixed_ip)s limit 1"
        cursor.execute(query, {'fixed_ip': hostKey})
        dbrow = cursor.fetchone()
        if dbrow is None:
            return
        row = dict(zip(cursor.column_names, dbrow))
        logging.warning(row)
        cursor.close()
        _mdb.close()
        return row

