'''
The server of the chat software

@auther: Tony Code

'''
from socket import *
from database import store
from time import ctime, sleep
from assist import process

DBPATH = 'database/userinfo.db'
HOST = 'localhost'#input('Please Enter the server ip:')
PORT = 12345
BUFSIZ = 1024
ADDR = (HOST, PORT)
AD = {}
pub_keys = {}
received = b""


udpSerSock = socket(AF_INET, SOCK_DGRAM)
udpSerSock.bind(ADDR)

def getkey(a, b):
    for i,j in enumerate(a):
        if a[j] == b:
            return j

while True:
    print('waiting for message...')
    try:
        package, addr = udpSerSock.recvfrom(BUFSIZ)
        print(package)
    except:
        print('a connection closed')
        continue
    sign, s_name, r_name, length, msg = process.analyze(package)

    if sign == 'connect':
        if addr not in AD.values():
            pub_keys[s_name] = msg
            for na, ad in AD.items():
                package = process.assemble('key', s_name, na, len(msg), msg.decode('utf-8'))
                udpSerSock.sendto(package, ad)
            AD[s_name] = addr
            for na, pbkey in pub_keys.items():
                if na == s_name:
                    continue
                package = process.assemble('key', na, s_name, len(pbkey), pbkey.decode('utf-8'))
                udpSerSock.sendto(package, addr)
            message = f'{s_name} comes in\n'
            for na, ad in AD.items(): 
                package = process.assemble('receive', 'server', na, len(message), message)
                udpSerSock.sendto(package, ad)
    elif sign == 'receive':
        udpSerSock.sendto(package, AD[r_name])
    elif sign == 'disconnect':
        AD.pop(s_name)
        pub_keys.pop(s_name)
        for na, ad in AD.items():
            package = process.assemble('disconnect', s_name, na, len('cancel'), 'cancel')
            udpSerSock.sendto(package, ad)
    elif sign == 'register':
        username, password = (msg.decode('utf-8')).split(' ', 1)
        state = store.store_new_info(username, password, DBPATH)
        if(state):
            package = process.assemble('register', 'server', 'unknown', len('success'), 'success')
            udpSerSock.sendto(package, addr)
        else:
            package = process.assemble('register', 'server', 'unknown', len('success'), 'fail')
            udpSerSock.sendto(package, addr)
    elif sign == 'login':
        username, password = (msg.decode('utf-8')).split(' ', 1)    
        state = store.check_login_info(username, password, DBPATH)
        if(state):
            package = process.assemble('login', 'server', 'unknown', len('success'), 'success')
            udpSerSock.sendto(package, addr)
        else:
            package = process.assemble('login', 'server', 'unknown', len('success'), 'fail')
            udpSerSock.sendto(package, addr)
    print(AD)
    #print(pub_keys)


udpSerSock.close()
