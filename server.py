import socket, sys
import datetime
import time, random
TCP_IP = '72.36.65.116'
TCP_PORT = 5005
BUFFER_SIZE = 1024

if len(sys.argv) < 2:
 print ("Enter the server id")
 sys.exit(1)

while True:
  v = random.randint(1, 10)
  ts = time.time()
  MESSAGE = str(v) + ";" + sys.argv[1] + ";" + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((TCP_IP, TCP_PORT))
  s.send(MESSAGE)
  s.close()
  print (MESSAGE)
  time.sleep(60)
