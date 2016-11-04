import commands
import socket, sys
import datetime
import time, random

TCP_IP = 'server-1'
TCP_PORT = 80

BUFFER_SIZE = 1024


while 1:
 start_time = time.time()
 for i in range (0,10):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.bind(('0.0.0.0', 9080 + i))
   s.connect((TCP_IP, TCP_PORT))
   s.send('GET /file.bz2 /HTTP 1.1 \r\n\r\n')
   data = (s.recv(1000000))
   print "File received! Time: " + str(time.time() - start_time)
   s.close()
