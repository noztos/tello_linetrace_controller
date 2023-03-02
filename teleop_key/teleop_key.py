import readchar
import socket

def main():
    serv_address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        try:
            key = readchar.readkey()
            print(key)
            send_len = sock.sendto(key.encode('utf-8'), serv_address)
        except KeyboardInterrupt:
            sock.close()
            break

if __name__ == '__main__':
    main()
