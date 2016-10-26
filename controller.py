import socket
import sys
import sqlite3
import re
from datetime import datetime

def insertInto (cur, recieved, source, id): #inserts data into the table
 energyValue, serverID, date, private_ip, numberOfActiveUsers = recieved
 value = float(energyValue)
 sID = int(serverID)

 print (id, value, source[0], sID, date, private_ip, int(numberOfActiveUsers))
 cur.execute ("INSERT into energyValues(id, value, ip, server, time, private_ip, users_number) values (?, ?, ?, ?, ?, ?, ?)", 
 (id, value, source[0], sID, date, private_ip, int(numberOfActiveUsers)))
 #date_object = datetime.strptime (date, '%Y-%m-%d %H:%M:%S')
 
def listenTCP(TCP_IP, TCP_PORT, connLimit): #opens listening TCP ports
 s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 s.bind((TCP_IP, TCP_PORT))
 s.listen(connLimit)
 return s

def openDB(dbname): #opens database
 db = sqlite3.connect(dbname)
 cursor = db.cursor()
 return db, cursor

def runTCP(s, db, cursor, addressList, id): #accepts TCP connections from the addressList and calls insertion function
 BUFFER_SIZE = 1024
 while 1:
  conn, addr = s.accept()
  try:
   print 'Connection address:', addr
   if addr[0] not in addressList:
    break
   data = conn.recv(BUFFER_SIZE)
   if not data: break
   recieved = re.split(';', data) #split data into an array
   id += 1
   insertInto(cursor, recieved, addr, id)
   db.commit()
   conn.send(data)  # echo
  except KeyboardInterrupt: #not sure if it works properly
   print "Closing connection"
   conn.close()
   db_conn.close()

s = listenTCP('72.36.65.116', 5005, 3)
db, cursor = openDB('controller.db')
cursor.execute("SELECT MAX(id) from energyValues")
id = cursor.fetchone()[0] #take the last id in the table
if id == None:
 id = 0
print(id)

addressList = ('172.17.4.5', '172.17.4.6', '172.17.4.7') #we will accept TCP only from these IP addresses
runTCP(s, db, cursor, addressList, id)

conn.close()
db.close()	
