import socket
import struct
import threading
import time
import concurrent.futures
import random
import multiprocessing
from typing import DefaultDict

winners_dict=DefaultDict()

def send_broadcast_suggestion(socket_udp):
    message = struct.pack('Ibh', 0xabcddcba, 0x2, 2101)
    socket_udp.sendto(message, ("<broadcast>", 13117))


def thread_send_Announcements(upd_socket):
    threading.Timer(1.0, thread_send_Announcements, args=[upd_socket]).start()
    send_broadcast_suggestion(upd_socket)


def start_new_game(clientside):
    start_time = time.time()
    # task="Please Answer the following question: \n How much is 2+2?"
    # tcp_socket.sendall(task)
    while time.time() - start_time < 10:
        clientside.settimeout(10)
        try:
            message = clientside.recv(1024)
            if message==b'4':
                return ("Winner",time.time())
            else :
                return ("Looser",time.time())
        except:
            pass
    return ("Tie",time.time())


if __name__ == '__main__':
    sockets_list = []
    SERVER_IP = socket.gethostname()
    PORT_NUM = 2101
    print(f"Server started,listening on IP address {SERVER_IP} \n Come To me baby")
    upd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    upd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sending_suggestions_thread = multiprocessing.Process(target=thread_send_Announcements, args=(upd_socket,))
    sending_suggestions_thread.start()
    # while True:
    #     pass
    global tcp_socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(('', PORT_NUM))
    tcp_socket.listen(2)
    with concurrent.futures.ThreadPoolExecutor(2) as executor:
        while True:
            # tcp_socket.settimeout(30)
            clientside, address_1 = tcp_socket.accept()
            group_name = clientside.recv(1024).decode("utf-8")
            sockets_list.append((clientside, group_name))
            print(f"Player 1 connected, group name : {group_name} \n Waiting for Player 2")

            clientside, address_2 = tcp_socket.accept()
            group_name = clientside.recv(1024).decode("utf-8")
            sockets_list.append((clientside, group_name))
            print(f"Player 2 connected, group name : {group_name} \n Game will start if a few seconds")

            time.sleep(2)

            # random.shuffle(sockets_list)

            group1 = sockets_list[0][1]
            group2 = sockets_list[1][1]

            start_message = bytes(
                "Group 1:\n==\n" + group1 + "\n\nGroup "
                                                               "2:\n==\n" + group2 + "\n"
                                                                                       "\nPlease Answer the following question: \n How much is 2+2?",
                "utf-8")

            for client, group_name in sockets_list:
                client.sendall(start_message)
            game1 = executor.submit(start_new_game, sockets_list[0][0])
            game2 = executor.submit(start_new_game, sockets_list[1][0])

            group1_result = game1.result()
            group2_result = game2.result()

            result_message = "Game over! \n The correct answer was 4! \n Congratulations to the winner:"

            if group1_result[0] =="Tie" and group2_result[0]=="Tie":
                print("Tie")
                result_message = bytes(result_message + "All Buddies get the same score, it a Tie!", "utf-8")
                for client, group_name in sockets_list:
                            client.sendall(result_message)
            else:
                if group1_result[1]<group2_result[1]:
                    if group1_result[0]=="Winner":
                        print(f"{group1} is winner")
                        result_message = bytes(result_message + f"{group1}", "utf-8")
                        for client, group_name in sockets_list:
                            client.sendall(result_message)
                        # winners_dict[group1]+=1
                    else:
                        print(f"{group2} is winner")
                        result_message = bytes(result_message + f"{group2}", "utf-8")
                        for client, group_name in sockets_list:
                            client.sendall(result_message)
                        # winners_dict[group2]+=1
                else:
                    if group2_result[0]=="Winner":
                        print(f"{group2} is winner")
                        result_message = bytes(result_message + f"{group2}", "utf-8")
                        for client, group_name in sockets_list:
                            client.sendall(result_message)
                        # winners_dict[group2]+=1
                    else:
                        print(f"{group1} is winner")
                        result_message = bytes(result_message + f"{group1}", "utf-8")
                        for client, group_name in sockets_list:
                            client.sendall(result_message)
                        # winners_dict[group1]+=1
            print("Game over, sending out offer requests... ")
            sockets_list = []
            sending_suggestions_thread = multiprocessing.Process(target=thread_send_Announcements, args=(upd_socket,))
            sending_suggestions_thread.start()
