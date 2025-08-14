#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
گرفتن عکس ساده از دوربین بدون نمایش GUI
"""

from camera_controller import CameraController
import time
import os


def main():
    """گرفتن عکس از دوربین"""
    
    # مشخصات دوربین
    CAMERA_IP = "192.168.1.108"
    USERNAME = "admin"
    PASSWORD = "ArashArash"
    
    print("📸 گیرنده عکس دوربین ITC231-RF1A-IR")
    print("=" * 40)
    
    # ایجاد پوشه عکس‌ها
    if not os.path.exists("snapshots"):
        os.makedirs("snapshots")
        print("📁 پوشه snapshots ایجاد شد")
    
    # ایجاد کنترل کننده
    camera = CameraController(CAMERA_IP, USERNAME, PASSWORD)
    
    try:
        print(f"🔄 اتصال به دوربین {CAMERA_IP}...")
        
        if camera.open_camera():
            print("✅ دوربین متصل شد!")
            
            # نمایش اطلاعات
            info = camera.get_camera_info()
            print(f"\n📋 رزولوشن: {info.get('resolution', 'نامشخص')}")
            print(f"📋 نرخ فریم: {info.get('fps', 'نامشخص')} FPS")
            
            while True:
                print("\n" + "=" * 30)
                print("انتخاب‌های شما:")
                print("1. گرفتن یک عکس")
                print("2. گرفتن 5 عکس متوالی")
                print("3. گرفتن عکس هر 10 ثانیه (تا زمان توقف)")
                print("4. خروج")
                print("=" * 30)
                
                choice = input("انتخاب (1-4): ").strip()
                
                if choice == "1":
                    print("\n📸 گرفتن عکس...")
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"snapshots/photo_{timestamp}.jpg"
                    
                    if camera.save_snapshot(filename):
                        print(f"✅ عکس ذخیره شد: {filename}")
                    else:
                        print("❌ خطا در گرفتن عکس")
                
                elif choice == "2":
                    print("\n📸 گرفتن 5 عکس متوالی...")
                    for i in range(5):
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        filename = f"snapshots/series_{timestamp}_{i+1}.jpg"
                        
                        if camera.save_snapshot(filename):
                            print(f"✅ عکس {i+1}: {filename}")
                        else:
                            print(f"❌ خطا در عکس {i+1}")
                        
                        if i < 4:  # صبر بین عکس‌ها (جز آخری)
                            time.sleep(1)
                
                elif choice == "3":
                    print("\n⏰ شروع گرفتن عکس هر 10 ثانیه...")
                    print("برای توقف، Ctrl+C را فشار دهید\n")
                    
                    try:
                        counter = 1
                        while True:
                            timestamp = time.strftime("%Y%m%d_%H%M%S")
                            filename = f"snapshots/auto_{timestamp}.jpg"
                            
                            if camera.save_snapshot(filename):
                                print(f"✅ عکس خودکار {counter}: {filename}")
                                counter += 1
                            else:
                                print(f"❌ خطا در عکس خودکار {counter}")
                            
                            # صبر 10 ثانیه
                            for i in range(10, 0, -1):
                                print(f"\r⏳ عکس بعدی در {i} ثانیه...", end="", flush=True)
                                time.sleep(1)
                            print()  # خط جدید
                            
                    except KeyboardInterrupt:
                        print("\n⚠️ گرفتن عکس خودکار متوقف شد")
                
                elif choice == "4":
                    print("\n👋 خروج...")
                    break
                
                else:
                    print("❌ انتخاب نامعتبر!")
            
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
