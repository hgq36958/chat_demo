"""
author:Jason
email:XXX@163.com
time: 2020-8-14
env: Python3.6
socket and Process exercise
"""
from socket import *
from multiprocessing import Process

# 服务器使用地址(会经常用的全局变量，不需要改变的，一般用大写字母表示)
HOST = "0.0.0.0"
PORT = 8000
ADDR = (HOST, PORT)

# 存储用户 {name:address ...}
user = {}

# 处理进入聊天室
def do_login(sock, name, address):
    if name in user or "管理" in name:
        sock.sendto(b"FAIL", address)
        return
    else:
        sock.sendto(b"OK", address)
        # 通知其他人
        msg = "欢迎 %s 进入聊天室" % name
        for i in user:
            sock.sendto(msg.encode(), user[i])
        # 存储用户
        user[name] = address
        # print(user)


# 处理聊天
def do_chat(sock, name, content):
    msg = "%s : %s" % (name, content)
    for i in user:
        # 刨除本人
        if i != name:
            sock.sendto(msg.encode(), user[i])


# 处理退出
def do_exit(sock, name):
    del user[name]  # 移除此人
    # 通知其他人
    msg = "%s 退出聊天室" % name
    for i in user:
        sock.sendto(msg.encode(), user[i])


# 子进程执行
def handle(sock):
    # 循环接收来自客户端请求
    while True:
        # 接收请求 (所有用户的所有请求)
        data, addr = sock.recvfrom(1024)
        tmp = data.decode().split(' ', 2)  # 对请求内容进行解析
        # 根据请求调用不同该函数处理
        if tmp[0] == 'L':
            # tmp ==> ["L","name"]
            do_login(sock, tmp[1], addr)  # 处理用户进入聊天具体事件
        elif tmp[0] == 'C':
            # tmp==>[C,name,msg]
            do_chat(sock, tmp[1], tmp[2])
        elif tmp[0] == 'E':
            # tmp==>[E,name]
            do_exit(sock, tmp[1])


# 启动函数用于搭建网络
def main():
    sock = socket(AF_INET, SOCK_DGRAM)  # UDP套接字
    sock.bind(ADDR)

    # 创建一个新的进程，用于分担功能
    p = Process(target=handle, args=(sock,))
    p.daemon = True
    p.start()
    # 父进程发送管理员消息
    while True:
        content = input("管理员消息：")
        # 服务端整个退出
        if content == "quit":
            break
        data = "C 管理员消息 " + content
        sock.sendto(data.encode(), ADDR)  # 父进程发送给子进程


if __name__ == '__main__':
    main()


