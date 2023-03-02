xhost +
docker run \
  --rm \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  tello_teleop_controller:latest python controller.py --tello_ip 127.0.0.1
