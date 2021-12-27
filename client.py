import socket
import struct
import getch
import time
import signal

TIMEOUT=10
def inter_timeout(signum, frame):
    pass
signal.signal(signal.SIGALRM, inter_timeout)

if __name__ == '__main__':
    while True:
        print("Client started, listening for offer requests...")
        UPD_PORT = 13117
        tcp_connected=False
        while not tcp_connected:
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_sock.bind(('', UPD_PORT))
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
                    continue
            udp_sock.close()
            print("Received offer from " + str(addr[0]) + " attempting to connect...")
            portnum = recieved_message[2] #wanted port number
            # print("Port num " + str(int(portnum)))
            try: #incase doens't connect
                tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_socket.connect((socket.gethostname(), portnum))
                tcp_connected=True
            except:
                continue

        tcp_socket.sendall(bytes("Micky and the Fire", "utf-8"))

        print(tcp_socket.recv(1024).decode("utf-8"))
        try:
            signal.alarm(TIMEOUT)
            x=getch.getch()
            signal.alarm(0)
        except:
            x=''
        message = bytes(x, "utf-8")
        tcp_socket.sendall(message)
        server_message = tcp_socket.recv(1024)
        print(server_message.decode("utf-8"))
        tcp_socket.close()
        time.sleep(1)
