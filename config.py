#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فایل تنظیمات پروژه
"""

# تنظیمات دوربین
CAMERA_CONFIG = {
    "ip_address": "192.168.1.108",
    "username": "admin",
    "password": "ArashArash",
    "port": 80,
    "model": "ITC231-RF1A-IR"
}

# تنظیمات استریم
STREAM_CONFIG = {
    "timeout": 10,  # ثانیه
    "retry_attempts": 3,
    "frame_rate": 30
}

# مسیرهای استریم ممکن برای دوربین ITC231-RF1A-IR
STREAM_URLS = [
    "/videostream.cgi",
    "/mjpeg",
    "/video.mjpg",
    "/cam/realmonitor?channel=1&subtype=0",
    "/axis-cgi/mjpg/video.cgi",
    "/snapshot.cgi",
    "/cgi-bin/snapshot.cgi"
]

# تنظیمات فایل‌ها
FILE_CONFIG = {
    "snapshot_format": "jpg",
    "snapshot_quality": 95,
    "default_save_path": "./snapshots/"
}
