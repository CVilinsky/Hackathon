import socket
import struct
from getch import getch
import time
from threading import Timer

def get_input():
    x=getch()
    return x

if __name__ == '__main__':
    while True:
        TIMEOUT=10
        print("Client started, listening for offer requests...")
        UPD_PORT = 13117
        cache_anointment = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cache_anointment.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        cache_anointment.bind(('', UPD_PORT))
        stop = False
        data = None
        while not stop:
            data, addr = cache_anointment.recvfrom(1024)
            if data is None:
                continue
            try:
                values_message = struct.unpack('ibh', data)
                if  (values_message[0] == -1412571974) and (values_message[1] == 2):
                    stop = True
            except:
                continue
        cache_anointment.close()
        print("Received offer from " + str(addr[0]) + " attempting to connect...")
        portnum = values_message[2]
        # print("Port num " + str(int(portnum)))

        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((socket.gethostname(), portnum))

        tcp_socket.sendall(bytes("THE Gays", "utf-8"))

        print(tcp_socket.recv(1024).decode("utf-8"))
        timeout=10
        t=Timer(timeout,print,[''])
        t.start()
        message = getch()
        tcp_socket.sendall(message)
        t.cancel()

        server_message = tcp_socket.recv(1024)
        print(server_message.decode("utf-8"))
        tcp_socket.close()
