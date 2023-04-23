import socket               # Import socket module

s = socket.socket()         # Create a socket object

host = "127.0.0.1" # Get local machine name
port = 1005           # Reserve a port for your service.

s.connect((host, port))
while True:
    recv = s.recv(1024)
    recv = str(recv)[2:-1]
    if recv == "Exit Connection":
        s.send(bytes("Verbindung wird getrennt.", 'ascii'))
        s.close()
        break
    elif recv:
        print(recv)
        s.send(bytes("Angekommen", 'ascii'))
print("Fertig")
