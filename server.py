import socket
import datetime
import time, random
TCP_IP = '72.36.65.116'
TCP_PORT = 5005
BUFFER_SIZE = 1024
while True:
  v = random.randint(1, 10)
  ts = time.time()
  MESSAGE = str(v) + ";" + "1" + ";" + datetime.datetime.fromtimestamp(ts).strf\
time('%Y-%m-%d %H:%M:%S')
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((TCP_IP, TCP_PORT))
  s.send(MESSAGE)
  s.close()
  print (MESSAGE)
  time.sleep(5)
