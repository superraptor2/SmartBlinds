
class DbClass:
    def __init__(self):
        import mysql.connector as connector

        self.__dsn = {
            "host": "169.254.10.1",
            "user": "root",
            "passwd": "root",
            "db": "dbsmartblinds"
        }

        self.__connection = connector.connect(**self.__dsn)
        self.__cursor = self.__connection.cursor()

    def getLogs(self):
        sqlQuery = "SELECT reden, toestand, datumUur FROM dbsmartblinds.tbllog"
        self.__cursor.execute(sqlQuery)
        result = self.__cursor.fetchall()
        return result

    def getUser(self, username):
        sqlquery = "SELECT username, password FROM dbsmartblinds.tblusers WHERE username = '{param1}'"
        sqlCommand = sqlquery.format(param1=username)
        self.__cursor.execute(sqlCommand)
        result = self.__cursor.fetchone()
        self.__cursor.close()
        return result

    def getDevices(self):
        query = "SELECT idDevice, devicename FROM dbsmartblinds.tbldevices"
        self.__cursor.execute(query)
        result = self.__cursor.fetchall()
        self.__cursor.close()
        return result

    def getDevice(self, deviceid):
        query = "SELECT idDevice, devicename FROM dbsmartblinds.tbldevices WHERE idDevice = '" + deviceid + "'"
        self.__cursor.execute(query)
        result = self.__cursor.fetchall()
        self.__cursor.close()
        return result

    def getDataFromDatabase(self):
        # Query zonder parameters
        sqlQuery = "SELECT * FROM tablename"
        
        self.__cursor.execute(sqlQuery)
        result = self.__cursor.fetchall()
        self.__cursor.close()
        return result

    def getDataFromDatabaseMetVoorwaarde(self, voorwaarde):
        # Query met parameters
        sqlQuery = "SELECT * FROM tablename WHERE columnname = '{param1}'"
        # Combineren van de query en parameter
        sqlCommand = sqlQuery.format(param1=voorwaarde)
        
        self.__cursor.execute(sqlCommand)
        result = self.__cursor.fetchall()
        self.__cursor.close()
        return result

    def setDataToDatabase(self, value1):
        # Query met parameters
        sqlQuery = "INSERT INTO tablename (columnname) VALUES ('{param1}')"
        # Combineren van de query en parameter
        sqlCommand = sqlQuery.format(param1=value1)

        self.__cursor.execute(sqlCommand)
        self.__connection.commit()
        self.__cursor.close()