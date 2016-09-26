import commands
import socket, sys
import datetime
import time, random
TCP_IP = '72.36.65.116'
TCP_PORT = 5005
BUFFER_SIZE = 1024

#if len(sys.argv) < 2:
#  print ("Enter the server id")
#  sys.exit(1)

intf = 'eth1'
intf_ip = commands.getoutput("ip address show dev " + intf).split()
intf_ip = intf_ip[intf_ip.index('inet') + 1].split('/')[0]
print intf_ip

while True:
  v = random.randint(1, 10)
  ts = time.time()
  MESSAGE = str(v) + ";" + intf_ip + ";" + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((TCP_IP, TCP_PORT))
  s.send(MESSAGE)
  s.close()
  print (MESSAGE)
  time.sleep(60)
