import socket
import struct
import threading
import time
import concurrent.futures
import random
import multiprocessing
from typing import DefaultDict
from colorama import Fore, Style,Back

winners_dict=DefaultDict(int) #Winners to get the highest score

"""
thread_send_Announcements & send_broadcast_suggestion:
Send the invitation to join the game through the given udp_socket.
The invitation sent is a broadcast message, and every 1 second.
"""

def send_broadcast_suggestion(udp_socket):
    message = struct.pack('Ibh', 0xabcddcba, 0x2, 2101) #unsigned integer, signed char and a short (16 bit integer)
    udp_socket.sendto(message, ("<broadcast>", 13117))


def thread_send_Announcements(udp_socket):
    threading.Timer(1.0, thread_send_Announcements, args=[udp_socket]).start()
    send_broadcast_suggestion(udp_socket)

"""
randomize_math :
Generates a simple math question, the output is a list.
The list contains the expected answer [0] and a string representing the question [1].
"""
def randomize_math(): #Randomizes a math question
    num1=random.choice([1,2,3,4,5])
    num2=random.choice([1,2,3,4])
    expected=num1+num2
    return [expected,f'{num1} + {num2}']


"""
start_new_game:
The game will end in 10 seconds, the server waits for answers from both clients.
The answer is sent with the current time stamp [1], the one who answered first either wins or loses depending on their answer.
If neither answered after 10 seconds it's a tie.
"""
def start_new_game(client,expected): #the game that everyone plays
    start_time = time.time()
    while time.time() - start_time < 10:
        client.settimeout(10) #will exit once 10 seconds have passed
        try:
            message = client.recv(1024).decode("utf-8")
            if message==expected:
                return ("Winner",time.time())
            else :
                return ("Looser",time.time())
        except:
            pass
    return ("Tie",time.time())

"""
Explanations:
Create a UDP socket that will wait for connections and send invitations.
Create a TCP socket that will get 2 connections from clients who were invited through the UDP socket.
The TCP socket will wait for 2 connections, each connection is saved into a list that will have two tuples one for each client.
We will communicate with the clients through the address recieved from them which is saved in [0] of the tuple.

The game begins once the question is sent to both of the participants.  
We will wait for both clients to respond, the one who responded first will either win or lose depending on their answer.
The winner will be saved inside a dictionary that represents the leaderboard.

In the end we will send the invitations again.  
"""
if __name__ == '__main__':
    sockets_list = []
    SERVER_IP = socket.gethostbyname(socket.gethostname()) 
    PORT_NUM = 2101
    print(f"Server started,listening on IP address {SERVER_IP} \nCome To me baby")
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sending_suggestions_thread = multiprocessing.Process(target=thread_send_Announcements, args=(udp_socket,))
    sending_suggestions_thread.start()

    global tcp_socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(('', PORT_NUM))
    tcp_socket.listen(2) #after 2 connections the socket will not accept new connections
    with concurrent.futures.ThreadPoolExecutor(2) as executor:
        while True:

            client, address_1 = tcp_socket.accept()
            group_name = client.recv(1024).decode("utf-8")
            sockets_list.append((client, group_name))
            print(f"{Fore.CYAN}Player 1{Style.RESET_ALL} connected, group name : {group_name} \nWaiting for Player 2")

            client, address_2 = tcp_socket.accept()
            group_name = client.recv(1024).decode("utf-8")
            sockets_list.append((client, group_name))
            print(f"{Fore.YELLOW}Player 2{Style.RESET_ALL} connected, group name : {group_name} \nGame will start if a few seconds")
            time.sleep(2)
            group1 = sockets_list[0][1]
            group2 = sockets_list[1][1]

            math_problem=randomize_math()

            start_message = bytes(f"{Back.BLUE}Welcome to Quick Maths.{Style.RESET_ALL}\n{Fore.CYAN}Player 1: {group1}{Style.RESET_ALL}\n{Fore.YELLOW}Player 2: {group2}{Style.RESET_ALL}\n==\nPlease Answer the following question: \nHow much is {math_problem[1]}?","utf-8")

            for clientadd, group_name in sockets_list:
                clientadd.sendall(start_message)

            """
            Send the start_new_game function to the clients and the expected answer.
            """
            game1 = executor.submit(start_new_game, sockets_list[0][0],math_problem[0])
            game2 = executor.submit(start_new_game, sockets_list[1][0],math_problem[0])

            group1_result = game1.result()
            group2_result = game2.result()

            result_message = f"Game over! \nThe correct answer was {math_problem[0]}! \nCongratulations to the winner:"

            if group1_result[0] =="Tie" and group2_result[0]=="Tie":
                print("Tie")
                result_message = bytes("Time's up {Back.MAGENTA}loosers{Style.RESET_ALL}, it a Tie!", "utf-8")
                for clientadd, group_name in sockets_list:
                            clientadd.sendall(result_message)
            else:
                if group1_result[1]<group2_result[1]:
                    if group1_result[0]=="Winner":
                        print(f"{group1} are the winner")
                        result_message = bytes(result_message + f"{group1}", "utf-8")
                        for clientadd, group_name in sockets_list:
                            clientadd.sendall(result_message)
                        winners_dict[group1]+=1
                    else:
                        print(f"{group2} are the winner")
                        result_message = bytes(result_message + f"{group2}", "utf-8")
                        for clientadd, group_name in sockets_list:
                            clientadd.sendall(result_message)
                        winners_dict[group2]+=1
                else:
                    if group2_result[0]=="Winner":
                        print(f"{group2} are the winner")
                        result_message = bytes(result_message + f"{group2}", "utf-8")
                        for clientadd, group_name in sockets_list:
                            clientadd.sendall(result_message)
                        winners_dict[group2]+=1
                    else:
                        print(f"{group1} are the winner")
                        result_message = bytes(result_message + f"{group1}", "utf-8")
                        for clientadd, group_name in sockets_list:
                            clientadd.sendall(result_message)
                        winners_dict[group1]+=1
            if len(winners_dict.keys())!=0:
                print(f"{max(winners_dict, key=winners_dict.get)} Has the Highest Score on the Server")
            print(f"{Fore.RED}Game over{Style.RESET_ALL}, sending out offer requests... ")

            sockets_list = []
            sending_suggestions_thread = multiprocessing.Process(target=thread_send_Announcements, args=(udp_socket,))
            sending_suggestions_thread.start()
