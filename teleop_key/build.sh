#!/bin/sh
cd `dirname $0`
docker build -t tello_teleop_key -f Dockerfile .
