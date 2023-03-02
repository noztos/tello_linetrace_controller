#!/bin/sh
cd `dirname $0`
docker build -t tello_linetrace_controller -f Dockerfile .
