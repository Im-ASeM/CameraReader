#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نمایش استریم زنده دوربین با رابط کاربری بهبود یافته
"""

import cv2
import time
import numpy as np
from camera_controller import CameraController
import threading
import sys


class LiveStreamViewer:
    """نمایش‌دهنده استریم زنده با قابلیت‌های پیشرفته"""
    
    def __init__(self, camera_controller):
        self.camera = camera_controller
        self.is_streaming = False
        self.frame_count = 0
        self.start_time = time.time()
        self.fps_display = 0
        
    def show_controls_info(self):
        """نمایش راهنمای کنترل‌ها"""
        print("\n🎮 کلیدهای کنترل:")
        print("┌─────────────────────────────────────┐")
        print("│ ESC یا Q    : خروج از استریم        │")
        print("│ SPACE       : گرفتن عکس            │")
        print("│ S           : ذخیره عکس با نام دلخواه│")
        print("│ F           : تمام صفحه             │")
        print("│ R           : ریستارت استریم        │")
        print("│ I           : نمایش/مخفی کردن اطلاعات│")
        print("└─────────────────────────────────────┘\n")
    
    def calculate_fps(self):
        """محاسبه FPS واقعی"""
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 1.0:  # هر ثانیه به‌روزرسانی
            self.fps_display = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = time.time()
    
    def add_overlay_info(self, frame, show_info=True):
        """اضافه کردن اطلاعات روی تصویر"""
        if not show_info:
            return frame
            
        # اندازه فریم
        height, width = frame.shape[:2]
        
        # پس‌زمینه برای متن
        overlay = frame.copy()
        
        # اطلاعات برای نمایش
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        camera_info = self.camera.get_camera_info()
        
        # متن‌های اطلاعاتی
        info_lines = [
            f"🎥 دوربین: {camera_info['model']}",
            f"📡 IP: {camera_info['ip_address']}",
            f"🔍 رزولوشن: {camera_info.get('resolution', 'نامشخص')}",
            f"⚡ FPS: {self.fps_display:.1f}",
            f"🕐 زمان: {timestamp}"
        ]
        
        # رسم پس‌زمینه
        cv2.rectangle(overlay, (10, 10), (400, 160), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # رسم متن‌ها
        y_offset = 35
        for line in info_lines:
            cv2.putText(frame, line, (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            y_offset += 25
        
        # نمایش راهنما در پایین
        guide_text = "ESC=خروج | SPACE=عکس | S=ذخیره | F=تمام‌صفحه | I=اطلاعات"
        cv2.putText(frame, guide_text, (10, height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        return frame
    
    def save_frame_with_name(self, frame):
        """ذخیره فریم با نام دلخواه"""
        try:
            print("\n📝 نام فایل را وارد کنید (بدون پسوند):")
            filename = input("نام فایل: ").strip()
            
            if not filename:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"live_capture_{timestamp}"
            
            filepath = f"snapshots/{filename}.jpg"
            
            cv2.imwrite(filepath, frame)
            print(f"✅ عکس ذخیره شد: {filepath}")
            
        except Exception as e:
            print(f"❌ خطا در ذخیره: {str(e)}")
    
    def show_live_stream(self):
        """نمایش استریم زنده اصلی"""
        if not self.camera.is_connected:
            print("❌ دوربین متصل نیست!")
            return
        
        print("🎥 شروع استریم زنده...")
        self.show_controls_info()
        
        # متغیرهای کنترل
        self.is_streaming = True
        show_info = True
        fullscreen = False
        window_name = "🎥 استریم زنده دوربین ITC231-RF1A-IR"
        
        # ایجاد پنجره
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1280, 720)
        
        snapshot_counter = 1
        
        try:
            while self.is_streaming:
                # دریافت فریم
                frame = self.camera.capture_frame()
                
                if frame is None:
                    print("❌ خطا در دریافت فریم")
                    break
                
                # محاسبه FPS
                self.calculate_fps()
                
                # اضافه کردن اطلاعات
                display_frame = self.add_overlay_info(frame, show_info)
                
                # نمایش فریم
                cv2.imshow(window_name, display_frame)
                
                # بررسی کلیدها
                key = cv2.waitKey(1) & 0xFF
                
                if key == 27 or key == ord('q') or key == ord('Q'):  # ESC یا Q
                    print("🛑 خروج از استریم...")
                    break
                    
                elif key == ord(' '):  # SPACE - عکس سریع
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filepath = f"snapshots/live_{timestamp}_{snapshot_counter:03d}.jpg"
                    cv2.imwrite(filepath, frame)
                    print(f"📸 عکس ذخیره شد: {filepath}")
                    snapshot_counter += 1
                    
                elif key == ord('s') or key == ord('S'):  # S - ذخیره با نام
                    # متوقف کردن موقت برای ورودی
                    cv2.destroyWindow(window_name)
                    self.save_frame_with_name(frame)
                    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                    if not fullscreen:
                        cv2.resizeWindow(window_name, 1280, 720)
                    
                elif key == ord('f') or key == ord('F'):  # F - تمام صفحه
                    fullscreen = not fullscreen
                    if fullscreen:
                        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                        print("🖥️ حالت تمام صفحه فعال شد")
                    else:
                        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                        cv2.resizeWindow(window_name, 1280, 720)
                        print("🖥️ حالت تمام صفحه غیرفعال شد")
                        
                elif key == ord('i') or key == ord('I'):  # I - نمایش/مخفی اطلاعات
                    show_info = not show_info
                    status = "فعال" if show_info else "غیرفعال"
                    print(f"ℹ️ نمایش اطلاعات {status} شد")
                    
                elif key == ord('r') or key == ord('R'):  # R - ریستارت
                    print("🔄 ریستارت استریم...")
                    self.camera.close_camera()
                    time.sleep(1)
                    if not self.camera.open_camera():
                        print("❌ خطا در ریستارت")
                        break
                    print("✅ ریستارت موفق")
                
                # بررسی بسته شدن پنجره
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
                    
        except KeyboardInterrupt:
            print("\n⚠️ استریم توسط کاربر متوقف شد")
            
        except Exception as e:
            print(f"\n❌ خطا در استریم: {str(e)}")
            
        finally:
            self.is_streaming = False
            cv2.destroyAllWindows()
            print("✅ استریم بسته شد")


def main():
    """تابع اصلی"""
    
    # مشخصات دوربین
    CAMERA_IP = "192.168.1.108"
    USERNAME = "admin"
    PASSWORD = "ArashArash"
    
    print("=" * 60)
    print("🎥 نمایش‌دهنده استریم زنده دوربین ITC231-RF1A-IR")
    print("=" * 60)
    
    # ایجاد کنترل کننده دوربین
    camera = CameraController(CAMERA_IP, USERNAME, PASSWORD)
    
    try:
        print("🔄 اتصال به دوربین...")
        
        if camera.open_camera():
            print("✅ دوربین متصل شد!")
            
            # نمایش اطلاعات دوربین
            info = camera.get_camera_info()
            print(f"\n📋 اطلاعات دوربین:")
            print(f"   🌐 آدرس: {info['ip_address']}")
            print(f"   🎬 مدل: {info['model']}")
            print(f"   🔍 رزولوشن: {info.get('resolution', 'نامشخص')}")
            print(f"   ⚡ FPS: {info.get('fps', 'نامشخص')}")
            
            # ایجاد نمایش‌دهنده استریم
            viewer = LiveStreamViewer(camera)
            
            # شروع استریم
            viewer.show_live_stream()
            
        else:
            print("❌ خطا در اتصال به دوربین!")
            print("💡 راهنمایی:")
            print("   - آدرس IP دوربین را بررسی کنید")
            print("   - اتصال شبکه را بررسی کنید")
            print("   - نام کاربری و رمز عبور را بررسی کنید")
            
    except KeyboardInterrupt:
        print("\n⚠️ برنامه متوقف شد")
        
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {str(e)}")
        
    finally:
        camera.close_camera()
        print("🔒 اتصال بسته شد")


if __name__ == "__main__":
    main()
