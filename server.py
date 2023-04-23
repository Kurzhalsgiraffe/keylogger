import socket  # Import socket module

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
#AF_INET steht für die Adress Family und beschreibt die art von Adressen mit der der Socket kommunizieren kann. In dem fall INET = IPv4
#SOCK_STREAM beschreibt die art der verbindung. In dem fall SOCK_STREAM = TCP
host = "127.0.0.1"
port = 1005
s.bind((host, port))  # Assigns the IP and Port to a socket instance

s.listen(5)  # Now wait for client connection.
#The number stands for: number of unaccepted connections that the system will allow before refusing new connections
conn, addr = s.accept()  # Establish connection with client.
#Returns a tuple, where the first one is a new socket objet used to send and receive data. The second one is the address bound to the socket of the client.
print('Got connection from', addr)
try:
    while True:
        com = input("Enter the msg:")
        conn.sendall(bytes(com, "ascii"))#Sendet alle daten
        recv = conn.recv(1024)#Data recieved from the socket. 1024 is the maximum amount of data to be received at once
        recv = str(recv)[2:-1]
        if(recv == "Verbindung wird getrennt."):
            break
        print(recv)
except KeyboardInterrupt:
    pass

conn.close()  # Close the connection
print("Connection closed.")
print("Fertig")
