import socket
import struct
import getch
import time
<<<<<<< HEAD
import signal #send software interrupts in linux
=======
import signal
from multiprocessing import Process
>>>>>>> f5ab53682cafd62132909f2f197b05d6b84b96c1

TIMEOUT=10
def getch_func():
    try:
        signal.alarm(TIMEOUT)
        x=getch.getch()
        signal.alarm(0)
    except:
        x=''
    message = bytes(x, "utf-8")
    tcp_socket.sendall(message)
    return
    
def inter_timeout(signum, frame):
    pass
signal.signal(signal.SIGALRM, inter_timeout)


"""
First of all we start the client, and wait for udp messages in port 13117
We will wait for a message that is packed as 'ibh'  that starts with the magic cookie, followed by the number 2.
If the stacture matches the expected stracture we will read the last part of the message which is the port we need to connect to.
We will close the udp socket and open a new tcp socket that will try to connect the given port.
We  send our name and start the game, once the math question is recived we use getch to get a input from the user.
If 10 seconds have passed, we will send a empty message.
In the end we recive a message stating either we won or lost, and then we will close the tcp socket.
"""
if __name__ == '__main__':
    while True:
        print("Client started, listening for offer requests...")
        UDP_PORT = 13117
        tcp_connected=False
        while not tcp_connected:
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_sock.bind(('', UDP_PORT))
            stop = False
            data = None
            while not stop:
                data, addr = udp_sock.recvfrom(1024)
                if data is None:
                    continue
                try:
                    recieved_message = struct.unpack('ibh', data)
                    if  (recieved_message[0] == -1412571974) and (recieved_message[1] == 2): #the format of the invitation
                        stop = True
                except:
                    print("Couldn't connect")
                    continue
            udp_sock.close()
            print("Received offer from " + str(addr[0]) + " attempting to connect...")
            portnum = recieved_message[2] #wanted port number
            # print("Port num " + str(int(portnum)))
            try: #incase doens't connect
                tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # print(addr)
                tcp_socket.connect((addr[0], portnum))
                tcp_connected=True
            except:
                print("Couldn't establish connection")
                continue

        tcp_socket.sendall(bytes("The Furries", "utf-8"))

        print(tcp_socket.recv(1024).decode("utf-8"))
        try:
            signal.alarm(TIMEOUT)
            x=getch.getch()
            signal.alarm(0)
        except:
            x=''
        message = bytes(x, "utf-8")
        tcp_socket.sendall(message)
        # getch_sub=Process(target=getch_func())
        # getch_sub.start()
        server_message = tcp_socket.recv(1024)
        # getch_sub.kill()
        print(server_message.decode("utf-8"))
        tcp_socket.close()
        time.sleep(1)

