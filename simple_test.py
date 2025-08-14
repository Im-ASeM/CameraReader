#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تست ساده دوربین - فقط برای بررسی اتصال
"""

from camera_controller import CameraController
import time


def main():
    """تست ساده اتصال به دوربین"""
    
    # مشخصات دوربین
    CAMERA_IP = "192.168.1.108"
    USERNAME = "admin"
    PASSWORD = "ArashArash"
    
    print("🧪 تست ساده دوربین ITC231-RF1A-IR")
    print("=" * 40)
    
    # ایجاد کنترل کننده
    camera = CameraController(CAMERA_IP, USERNAME, PASSWORD)
    
    try:
        print(f"🔄 تست اتصال به {CAMERA_IP}...")
        
        # تست اتصال
        if camera.test_connection():
            print("✅ اتصال موفق!")
            
            # تلاش برای اتصال به استریم
            print("🔄 تلاش برای اتصال به استریم...")
            if camera.connect_stream():
                print("✅ اتصال به استریم موفق!")
                
                # گرفتن یک فریم تست
                print("📸 گرفتن فریم تست...")
                frame = camera.capture_frame()
                
                if frame is not None:
                    print("✅ فریم با موفقیت دریافت شد!")
                    
                    # ذخیره عکس تست
                    snapshot = camera.save_snapshot("test_connection.jpg")
                    if snapshot:
                        print(f"✅ عکس تست ذخیره شد: {snapshot}")
                else:
                    print("❌ خطا در دریافت فریم")
                    
            else:
                print("❌ خطا در اتصال به استریم")
                
        else:
            print("❌ خطا در اتصال به دوربین")
            
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        
    finally:
        # بستن اتصال
        camera.close_camera()
        print("🔒 اتصال بسته شد")
        
    print("\n✨ تست کامل شد!")


if __name__ == "__main__":
    main()
