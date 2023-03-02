from djitellopy import Tello
import argparse
import cv2
import numpy as np
import socket
import time

def main():
    ## parse_args
    parser = argparse.ArgumentParser()
    parser.add_argument('--tello_ip')
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--hsv_min', nargs=3)
    parser.add_argument('--hsv_max', nargs=3)
    args = parser.parse_args()

    tello_ip = args.tello_ip if args.tello_ip else '192.168.10.1'
    use_window = not args.headless
    hsv_min = tuple(int(x) for x in args.hsv_min) if args.hsv_min else (0, 0, 0)
    hsv_max = tuple(int(x) for x in args.hsv_max) if args.hsv_max else (179, 255, 255)

    ## init_tello
    tello = Tello(host = args.tello_ip) if args.tello_ip else Tello()
    tello.connect()
    tello.streamoff()
    tello.streamon()

    ## create_window
    if use_window:
        window_name = 'linetrace'
        cv2.namedWindow(window_name)
        cv2.createTrackbar('H_min', window_name, hsv_min[0], 179, lambda _: None)
        cv2.createTrackbar('H_max', window_name, hsv_max[0], 179, lambda _: None)
        cv2.createTrackbar('S_min', window_name, hsv_min[1], 255, lambda _: None)
        cv2.createTrackbar('S_max', window_name, hsv_max[1], 255, lambda _: None)
        cv2.createTrackbar('V_min', window_name, hsv_min[2], 255, lambda _: None)
        cv2.createTrackbar('V_max', window_name, hsv_max[2], 255, lambda _: None)

    ## init socket
    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 10000))
    sock.setblocking(False)

    auto_mode = False
    while True:
        image = tello.get_frame_read().frame

        ## proc_image
        # resize
        small_image = cv2.resize(image, dsize=(480,360))

        # triming
        low_image = small_image[250:359, 0:479]

        # convert BGR to HSV
        hsv_image = cv2.cvtColor(low_image, cv2.COLOR_BGR2HSV)

        # range of "rope" color in HSV
        if use_window:
            hsv_min = (
                cv2.getTrackbarPos('H_min', window_name),
                cv2.getTrackbarPos('S_min', window_name),
                cv2.getTrackbarPos('V_min', window_name)
            )
            hsv_max = (
                cv2.getTrackbarPos('H_max', window_name),
                cv2.getTrackbarPos('S_max', window_name),
                cv2.getTrackbarPos('V_max', window_name)
            )

        # threshold range of "rope" color in HSV
        bin_image = cv2.inRange(hsv_image, hsv_min, hsv_max)

        # dilate
        kernel = np.ones((15, 15), np.uint8)
        bin_image = cv2.dilate(bin_image, kernel, iterations = 1)

        result_image = cv2.bitwise_and(hsv_image, hsv_image, mask=bin_image)

        # labeling
        num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(bin_image)
        num_labels = num_labels - 1
        stats = np.delete(stats, 0, 0)
        center = np.delete(center, 0, 0)
        if num_labels >= 1:
            max_index = np.argmax(stats[:,4])

            x = stats[max_index][0]
            y = stats[max_index][1]
            w = stats[max_index][2]
            h = stats[max_index][3]
            s = stats[max_index][4]
            mx = int(center[max_index][0])
            my = int(center[max_index][1])

            cv2.rectangle(result_image, (x, y), (x+w, y+h), (255, 0, 255))
            cv2.putText(result_image, "%d,%d"%(mx,my), (mx, my), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))

        ## show_image
        if use_window:
            def align_width(image, width):
                h, w = image.shape[:2]
                height = round(h * (width / w))
                return cv2.resize(image, dsize=(width, height))

            display_image = np.vstack((
                align_width(small_image, 960),
                align_width(low_image, 960),
                align_width(cv2.cvtColor(bin_image, cv2.COLOR_GRAY2BGR), 960),
                align_width(result_image, 960)
            ))
            cv2.imshow(window_name, display_image)
            cv2.waitKey(1)

        ## receive_command
        try:
            command, address = sock.recvfrom(1)
            command = command.decode('utf-8')
        except (BlockingIOError,  socket.error):
            command = ''

        ## auto_mode
        if command == '1':
            auto_mode = True
        elif command == '0':
            auto_mode = False

        if auto_mode:
            ## auto_control
            a = b = c = d = 0
            b = 30

            dx = 0.3 * (240 - mx)
            d = 0.0 if abs(dx) < 20.0 else dx #dead band
            d = -d
            d =  100 if d >  100.0 else d #limiter
            d = -100 if d < -100.0 else d #limiter

            tello.send_rc_control(int(a), int(b), int(c), int(d))
        else:
            ## teleop_control
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

    ## destroy_window
    if use_window:
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
