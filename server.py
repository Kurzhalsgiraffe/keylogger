from socket import socket

host = "127.0.0.1"
port = 1005

sock = socket()
sock.bind((host, port))

sock.listen(5)  # listen for client connection. The number stands for: number of unaccepted connections that the system will allow before refusing new connections
conn, addr = sock.accept()  # Establish connection with client. conn: new socket object used to send and receive data. addr address bound to the socket of the client.
print('Got connection from', addr)

while True:
    inpt = input("Enter command:")
    conn.sendall(bytes(inpt, "ascii"))
    recv = conn.recv(1024)  #Data recieved from the socket. 1024 is the maximum amount of data to be received at once
    if recv:
        recv = str(recv)[2:-1]
        if(recv == "terminating"):
            print("Terminated client. Good bye!")
            break
        else:
            print(recv)

conn.close()
print("Connection closed.")