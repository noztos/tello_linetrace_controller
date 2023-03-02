FROM python:3.9.10-slim-buster

RUN apt-get update && apt-get install -y \
    libopencv-dev \
    patch \
    && rm -rf /var/lib/apt/lists/*
RUN pip install numpy --upgrade
RUN pip install opencv-python==4.5.5.64
RUN pip install opencv-contrib-python==4.5.5.64
RUN pip install djitellopy==2.4.0

COPY djitellopy.patch tmp/djitellopy.patch
RUN patch usr/local/lib/python3.9/site-packages/djitellopy/tello.py < tmp/djitellopy.patch

COPY controller.py controller.py
