'''
The client of the chat software

@auther: Tony Code

'''
import rsa
import ctypes
import inspect
import threading
from socket import *
from tkinter import *
from assist import process
from time import sleep, ctime
from assist.sthread import stop_thread
from assist.client_gui import ChatRoom
from rsa import PublicKey, PrivateKey
from assist.register_and_login import LoginWindow



HOST = 'localhost' #input('Please input the ip of the server:')
PORT = 12345
BUFSIZ = 1024
ADDR = (HOST, PORT)

pub, priv = rsa.newkeys(1024)

class ChatRoomGUI(ChatRoom):
    """docstring for ChatRoomGUI"""
    def __init__(self,Client, ADDR, name):
        super(ChatRoomGUI, self).__init__()
        self.client = Client
        self.addr = ADDR
        self.name = name
        self.pub_keys = {}
        self.ads = {}
        self.received = b""
        self.send_init_message(pub)
                           
    def send_init_message(self, pub_key):
        sign = 'connect'
        s_name = self.name
        r_name = 'server'
        pub_key = self.turn_pub_key_to_string(pub_key)
        length = len(pub_key)
        package = self.assemble(sign, s_name, r_name, length, pub_key)
        self.client.sendto(package, self.addr)
        
    def show_self_message(self,msg):
        self.message_text.config(state=NORMAL)
        self.message_text.insert(END, ctime() + '\n')
        self.message_text.insert(END, self.name + ':\n')
        self.message_text.config(state=NORMAL)
        self.message_text.insert(END, msg + '\n')
        self.message_text.config(state=DISABLED)
        self.message_text.see(END)

    def show_message(self, s_name, msg):
        if(s_name != 'server'):
            msg = rsa.decrypt(msg, priv)
        msg = msg.decode('utf-8')
        self.message_text.config(state=NORMAL)
        self.message_text.insert(END, ctime() + '\n')
        if(s_name != 'server'):
            self.message_text.insert(END, s_name + ':\n')
        self.message_text.insert(END, msg + '\n')
        self.message_text.config(state=DISABLED)

    def assemble(self, sign, s_name, r_name, length, msg):
        sign = sign.encode('utf-8')
        s_name = s_name.encode('utf-8')
        r_name = r_name.encode('utf-8')
        length = str(length).encode('utf-8')
        package = sign + b' ' + s_name + b' ' + r_name + b' ' + length + b' ' + msg
        return package

    def analyze(self, package):
        sign, s_name, r_name, length, msg = package.split(b' ', 4)
        sign = sign.decode('utf-8')
        s_name = s_name.decode('utf-8')
        r_name = r_name.decode('utf-8')
        length = int(length.decode('utf-8'))
        return sign, s_name, r_name, length, msg


    def turn_pub_key_to_string(self, pub_key):
        a = str(pub_key['n'])
        b = str(pub_key['e'])
        return (a + ',' + b).encode('utf-8')

    def assemble_pub_key_from_string(self, pub_key):
        k = list(pub_key.decode('utf-8').split(','))
        pub_key = PublicKey(int(k[0]),int(k[1]))
        return pub_key

    def send_message(self):
        msg = self.message_ipt_text.get('0.0', END)
        self.message_ipt_text.delete('0.0', END)
        self.show_self_message(msg)
        msg = msg.encode('utf-8')
        for r_name, key in self.pub_keys.items():
            s_msg = rsa.encrypt(msg, self.pub_keys[r_name])
            length = len(s_msg)
            #print(r_name)
            #print(key)
            package = self.assemble('receive', self.name, r_name, length, s_msg)
            self.client.sendto(package, self.addr)


    def recv_message(self):
        while True:
            package, ADDR = self.client.recvfrom(1024)
            #print('received a message')
            sign, s_name, r_name, length, msg = self.analyze(package)
            #print('package analyze success')
            #print(sign)
            #self.received  = self.received + tempmsg
            #msg = self.received[0:length]
            #self.received = self.received[length:]
            if(sign == 'receive'):
                #print('start showing message')
                self.show_message(s_name, msg)
                self.message_text.see(END)
                #print('message showed')
            elif(sign == 'key'):
                pub_key = self.assemble_pub_key_from_string(msg)
                self.pub_keys[s_name] = pub_key
                #print("receive key successfully")
                #print(pub_key)
            elif(sign == 'disconnect'):
                self.pub_keys.pop(s_name)
                #print(self.pub_keys.keys())


udpCliSock = socket(AF_INET, SOCK_DGRAM)

login_window = LoginWindow(udpCliSock,ADDR)
    
mainloop()
    
state = login_window.get_state()
    
if state:
    NAME = login_window.get_name()
    
    chat_room = ChatRoomGUI(udpCliSock,ADDR, NAME)

    mthread = threading.Thread(target=chat_room.recv_message,args=[])

    mthread.start()

    mainloop()

    msg = 'disconnect'
    
    package = process.assemble('disconnect', NAME, 'server', len(msg), msg)
        
    udpCliSock.sendto(package, ADDR)
    
    stop_thread(mthread)

udpCliSock.close()
