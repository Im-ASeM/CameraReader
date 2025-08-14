#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نمایش‌دهنده دوربین با matplotlib برای ویندوز
"""

import cv2
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from camera_controller import CameraController
import numpy as np
import time


class CameraViewer:
    """نمایش‌دهنده دوربین با matplotlib"""
    
    def __init__(self, camera_controller):
        self.camera = camera_controller
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.set_title('🎥 دوربین ITC231-RF1A-IR - استریم زنده', fontsize=14)
        self.ax.axis('off')
        
    def update_frame(self, frame_num):
        """به‌روزرسانی فریم در matplotlib"""
        frame = self.camera.capture_frame()
        
        if frame is not None:
            # تبدیل BGR به RGB برای matplotlib
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # اضافه کردن timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame_rgb, timestamp, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            self.ax.clear()
            self.ax.imshow(frame_rgb)
            self.ax.set_title(f'🎥 دوربین ITC231-RF1A-IR - {timestamp}', fontsize=12)
            self.ax.axis('off')
            
        return []
    
    def show_live_stream(self):
        """نمایش استریم زنده با matplotlib"""
        print("🎥 شروع نمایش استریم زنده...")
        print("برای خروج، پنجره را ببندید")
        
        # ایجاد انیمیشن
        ani = animation.FuncAnimation(
            self.fig, self.update_frame, 
            interval=50, blit=False, cache_frame_data=False
        )
        
        plt.tight_layout()
        plt.show()


def main():
    """اجرای نمایش‌دهنده دوربین"""
    
    # مشخصات دوربین
    CAMERA_IP = "192.168.1.108"
    USERNAME = "admin"
    PASSWORD = "ArashArash"
    
    print("=" * 50)
    print("🎥 نمایش‌دهنده دوربین ITC231-RF1A-IR")
    print("=" * 50)
    
    # ایجاد کنترل کننده دوربین
    camera = CameraController(CAMERA_IP, USERNAME, PASSWORD)
    
    try:
        # اتصال به دوربین
        if camera.open_camera():
            print("✅ دوربین متصل شد!")
            
            # نمایش اطلاعات
            info = camera.get_camera_info()
            print("\n📋 اطلاعات دوربین:")
            for key, value in info.items():
                print(f"   {key}: {value}")
            
            print("\n🎥 آماده‌سازی نمایش...")
            
            # ایجاد نمایش‌دهنده
            viewer = CameraViewer(camera)
            
            # شروع نمایش
            viewer.show_live_stream()
            
        else:
            print("❌ خطا در اتصال به دوربین!")
            
    except KeyboardInterrupt:
        print("\n⚠️ برنامه متوقف شد")
        
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        
    finally:
        camera.close_camera()
        print("✅ اتصال بسته شد")


if __name__ == "__main__":
    main()
