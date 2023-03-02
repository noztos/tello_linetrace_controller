from djitellopy import Tello
import argparse
import cv2
import socket
import time

def main():
    ## parse_args
    parser = argparse.ArgumentParser()
    parser.add_argument('--tello_ip')
    args = parser.parse_args()

    ## init_tello
    tello = Tello(host = args.tello_ip) if args.tello_ip else Tello()
    tello.connect()
    tello.streamoff()
    tello.streamon()

    ## init_window
    window_name = 'teleop'
    cv2.namedWindow(window_name)

    ## init socket
    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 10000))
    sock.setblocking(False)

    # time.sleep(10)

    while True:
        image = tello.get_frame_read().frame

        ## show_image
        cv2.imshow(window_name, image)
        cv2.waitKey(1)

        ## receive_command
        try:
            command, address = sock.recvfrom(1)
            command = command.decode('utf-8')
        except (BlockingIOError,  socket.error):
            command = ''

        ## control
        if command == 't':
            tello.takeoff()
        elif command == 'l':
            tello.land()
        elif command == 'w':
            tello.move_forward(30)
        elif command == 's':
            tello.move_back(30)
        elif command == 'a':
            tello.move_left(30)
        elif command == 'd':
            tello.move_right(30)
        elif command == 'q':
            break # exit_loop

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
