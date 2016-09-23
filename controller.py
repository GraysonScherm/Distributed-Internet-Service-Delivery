import socket

TCP_IP = '72.36.65.116'
TCP_PORT = 5005
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(3)


while 1:
  conn, addr = s.accept()
  print 'Connection address:', addr
  data = conn.recv(BUFFER_SIZE)
  if not data: break
  print "received data:", data
  conn.send(data)  # echo
conn.close()
