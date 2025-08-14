#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت اصلی برای کنترل دوربین ITC231-RF1A-IR
"""

from camera_controller import CameraController
import time
import sys


def main():
    """
    تابع اصلی برنامه
    """
    # مشخصات دوربین شما
    CAMERA_IP = "192.168.1.108"
    USERNAME = "admin"
    PASSWORD = "ArashArash"
    
    print("=" * 50)
    print("🎥 کنترل کننده دوربین ITC231-RF1A-IR")
    print("=" * 50)
    
    # ایجاد نمونه کنترل کننده دوربین
    camera = CameraController(CAMERA_IP, USERNAME, PASSWORD)
    
    try:
        # باز کردن دوربین
        print("\n🔄 در حال باز کردن دوربین...")
        if camera.open_camera():
            print("✅ دوربین با موفقیت باز شد!")
            
            # نمایش اطلاعات دوربین
            info = camera.get_camera_info()
            print("\n📋 اطلاعات دوربین:")
            for key, value in info.items():
                print(f"   {key}: {value}")
            
            # منوی اصلی
            while True:
                print("\n" + "=" * 30)
                print("منوی اصلی:")
                print("1. نمایش استریم زنده")
                print("2. گرفتن عکس")
                print("3. نمایش اطلاعات دوربین")
                print("4. تست اتصال")
                print("5. خروج")
                print("=" * 30)
                
                choice = input("انتخاب شما (1-5): ").strip()
                
                if choice == "1":
                    print("\n🎥 شروع نمایش استریم زنده...")
                    print("برای خروج از استریم، کلید ESC را فشار دهید")
                    time.sleep(2)
                    camera.show_live_stream()
                    
                elif choice == "2":
                    print("\n📸 در حال گرفتن عکس...")
                    snapshot_path = camera.save_snapshot()
                    if snapshot_path:
                        print(f"✅ عکس با موفقیت ذخیره شد: {snapshot_path}")
                    
                elif choice == "3":
                    print("\n📋 اطلاعات دوربین:")
                    info = camera.get_camera_info()
                    for key, value in info.items():
                        print(f"   {key}: {value}")
                        
                elif choice == "4":
                    print("\n🔄 در حال تست اتصال...")
                    if camera.test_connection():
                        print("✅ اتصال موفق است")
                    else:
                        print("❌ اتصال ناموفق")
                        
                elif choice == "5":
                    print("\n👋 خروج از برنامه...")
                    break
                    
                else:
                    print("❌ انتخاب نامعتبر! لطفاً عددی بین 1 تا 5 وارد کنید.")
        
        else:
            print("❌ خطا در باز کردن دوربین!")
            print("لطفاً موارد زیر را بررسی کنید:")
            print("- آدرس IP دوربین صحیح باشد")
            print("- نام کاربری و رمز عبور درست باشد")
            print("- دوربین در شبکه قابل دسترسی باشد")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️ برنامه توسط کاربر متوقف شد")
        
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {str(e)}")
        return 1
        
    finally:
        # بستن اتصال دوربین
        print("\n🔄 در حال بستن اتصال دوربین...")
        camera.close_camera()
        print("✅ اتصال دوربین بسته شد")
        
    return 0


def test_camera_simple():
    """
    تست ساده دوربین (فقط باز و بسته کردن)
    """
    print("🧪 تست ساده دوربین...")
    
    CAMERA_IP = "192.168.1.108"
    USERNAME = "admin"
    PASSWORD = "ArashArash"
    
    camera = CameraController(CAMERA_IP, USERNAME, PASSWORD)
    
    try:
        # باز کردن دوربین
        if camera.open_camera():
            print("✅ دوربین با موفقیت باز شد!")
            
            # صبر 3 ثانیه
            print("⏳ صبر 3 ثانیه...")
            time.sleep(3)
            
            # گرفتن یک عکس
            snapshot = camera.save_snapshot("test_image.jpg")
            if snapshot:
                print(f"✅ عکس تست ذخیره شد: {snapshot}")
            
        else:
            print("❌ خطا در باز کردن دوربین!")
            
    finally:
        # بستن دوربین
        camera.close_camera()
        print("✅ دوربین بسته شد")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_camera_simple()
    else:
        exit_code = main()
        sys.exit(exit_code)
