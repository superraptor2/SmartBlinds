
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

    def getLogsKeuze(self):
        sqlQuery = "SELECT idchoice, choice FROM dbsmartblinds.tblchoice"
        self.__cursor.execute(sqlQuery)
        result = self.__cursor.fetchall()
        return result

    def getLogKeuze(self, idchoice):
        sqlQuery = "SELECT idchoice, choice FROM dbsmartblinds.tblchoice WHERE idchoice ='" + idchoice + "'"
        self.__cursor.execute(sqlQuery)
        result = self.__cursor.fetchall()
        return result

    def getLogsAll(self):
        sqlQuery = "SELECT reden, datum, uur FROM dbsmartblinds.tbllog"
        self.__cursor.execute(sqlQuery)
        result = self.__cursor.fetchall()
        return result

    def getLogsManual(self):
        sqlQuery = "SELECT reden, datum, uur FROM dbsmartblinds.tbllog WHERE reden LIKE '%manually%'"
        self.__cursor.execute(sqlQuery)
        result = self.__cursor.fetchall()
        return result

    def getLogsAutomatic(self):
        sqlQuery = "SELECT reden, datum, uur FROM dbsmartblinds.tbllog WHERE reden LIKE '%automatic%'"
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

    def getLicht(self):
        query = "SELECT scenename FROM dbsmartblinds.tblscenes WHERE idScenes = '1'"
        self.__cursor.execute(query)
        result = self.__cursor.fetchone()
        self.__cursor.close()
        return result


    def updateToestandBlind(self, toestand):
        # Query met parameters
        sqlQuery = "UPDATE tbltoestand SET toestand = '{toestand}' WHERE idtoestand = 1"
        # Combineren van de query en parameter
        sqlCommand = sqlQuery.format(toestand=toestand)
        self.__cursor.execute(sqlCommand)
        self.__connection.commit()
        self.__cursor.close()

    def updateToestandFan(self, toestand):
        # Query met parameters
        sqlQuery = "UPDATE tbltoestand SET toestand = '{toestand}' WHERE idtoestand = 2"
        # Combineren van de query en parameter
        sqlCommand = sqlQuery.format(toestand=toestand)
        self.__cursor.execute(sqlCommand)
        self.__connection.commit()
        self.__cursor.close()

    def getToestandblind(self):
        sqlQuery = "SELECT toestand FROM dbsmartblinds.tbltoestand WHERE idtoestand=1;"
        self.__cursor.execute(sqlQuery)
        result = self.__cursor.fetchone()
        return result

    def getToestandfan(self):
        sqlQuery = "SELECT toestand FROM dbsmartblinds.tbltoestand WHERE idtoestand=2;"
        self.__cursor.execute(sqlQuery)
        result = self.__cursor.fetchone()
        return result

    def setDataToLog(self, reden, datum, uur):
        # Query met parameters
        sqlQuery = "INSERT INTO tbllog (reden, datum, uur) VALUES ('{reden}', '{datum}', '{uur}')"
        # Combineren van de query en parameter
        sqlCommand = sqlQuery.format(reden=reden, datum=datum, uur=uur)
        self.__cursor.execute(sqlCommand)
        self.__connection.commit()
        self.__cursor.close()

#Voorbeelden van school ====================


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