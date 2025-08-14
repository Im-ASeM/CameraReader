#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
کنترل ساده دوربین بدون OpenCV
"""

import requests
import time
import base64
from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth
import os


class SimpleCameraController:
    """کنترل کننده ساده دوربین بدون OpenCV"""
    
    def __init__(self, ip_address, username, password, port=80):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.port = port
        self.base_url = f"http://{ip_address}:{port}"
        self.auth = HTTPBasicAuth(username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.is_connected = False
        
    def test_connection(self):
        """تست اتصال به دوربین"""
        try:
            response = self.session.get(
                f"{self.base_url}/",
                timeout=10,
                verify=False
            )
            
            if response.status_code == 200:
                print(f"✅ اتصال به دوربین {self.ip_address} موفق بود")
                self.is_connected = True
                return True
            else:
                print(f"❌ خطا در اتصال: کد وضعیت {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ خطا در اتصال: {str(e)}")
            return False
    
    def get_snapshot_url(self):
        """دریافت آدرس عکس از دوربین"""
        snapshot_urls = [
            f"{self.base_url}/snapshot.cgi",
            f"{self.base_url}/cgi-bin/snapshot.cgi",
            f"{self.base_url}/tmpfs/auto.jpg",
            f"{self.base_url}/image.jpg",
            f"{self.base_url}/snapshot.jpg"
        ]
        
        for url in snapshot_urls:
            try:
                response = self.session.head(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ آدرس عکس پیدا شد: {url}")
                    return url
            except:
                continue
                
        return None
    
    def take_snapshot(self, filename=None):
        """گرفتن عکس از دوربین"""
        if not self.is_connected:
            print("❌ ابتدا به دوربین متصل شوید")
            return False
            
        snapshot_url = self.get_snapshot_url()
        if not snapshot_url:
            print("❌ آدرس عکس پیدا نشد")
            return False
            
        try:
            response = self.session.get(snapshot_url, timeout=10)
            
            if response.status_code == 200:
                if filename is None:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"snapshots/simple_{timestamp}.jpg"
                
                # اطمینان از وجود پوشه
                os.makedirs("snapshots", exist_ok=True)
                
                with open(filename, 'wb') as f:
                    f.write(response.content)
                    
                print(f"✅ عکس ذخیره شد: {filename}")
                return filename
            else:
                print(f"❌ خطا در دریافت عکس: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ خطا در ذخیره عکس: {str(e)}")
            return False
    
    def get_stream_url(self):
        """دریافت آدرس استریم"""
        stream_urls = [
            f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}/videostream.cgi",
            f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}/mjpeg",
            f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}/video.mjpg"
        ]
        
        for url in stream_urls:
            try:
                response = requests.head(url, timeout=5)
                if response.status_code == 200:
                    return url
            except:
                continue
                
        return None
    
    def get_camera_info(self):
        """دریافت اطلاعات دوربین"""
        return {
            "ip_address": self.ip_address,
            "username": self.username,
            "port": self.port,
            "model": "ITC231-RF1A-IR",
            "is_connected": self.is_connected,
            "snapshot_url": self.get_snapshot_url(),
            "stream_url": self.get_stream_url()
        }


def main():
    """تابع اصلی"""
    
    # مشخصات دوربین
    CAMERA_IP = "192.168.1.108"
    USERNAME = "admin"
    PASSWORD = "ArashArash"
    
    print("=" * 50)
    print("📷 کنترل ساده دوربین ITC231-RF1A-IR")
    print("=" * 50)
    
    # ایجاد کنترل کننده
    camera = SimpleCameraController(CAMERA_IP, USERNAME, PASSWORD)
    
    try:
        print("🔄 اتصال به دوربین...")
        
        if camera.test_connection():
            print("✅ دوربین متصل شد!")
            
            # نمایش اطلاعات
            info = camera.get_camera_info()
            print(f"\n📋 اطلاعات دوربین:")
            for key, value in info.items():
                print(f"   {key}: {value}")
            
            while True:
                print("\n" + "=" * 30)
                print("منوی اصلی:")
                print("1. گرفتن عکس")
                print("2. گرفتن 5 عکس متوالی")
                print("3. نمایش اطلاعات دوربین")
                print("4. تست اتصال")
                print("5. خروج")
                print("=" * 30)
                
                choice = input("انتخاب شما (1-5): ").strip()
                
                if choice == "1":
                    print("\n📸 گرفتن عکس...")
                    result = camera.take_snapshot()
                    if result:
                        print(f"✅ عکس ذخیره شد")
                    
                elif choice == "2":
                    print("\n📸 گرفتن 5 عکس متوالی...")
                    for i in range(5):
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        filename = f"snapshots/series_simple_{timestamp}_{i+1}.jpg"
                        
                        result = camera.take_snapshot(filename)
                        if result:
                            print(f"✅ عکس {i+1}: {filename}")
                        else:
                            print(f"❌ خطا در عکس {i+1}")
                        
                        if i < 4:
                            time.sleep(1)
                
                elif choice == "3":
                    print("\n📋 اطلاعات دوربین:")
                    info = camera.get_camera_info()
                    for key, value in info.items():
                        print(f"   {key}: {value}")
                        
                elif choice == "4":
                    print("\n🔄 تست اتصال...")
                    if camera.test_connection():
                        print("✅ اتصال موفق")
                    else:
                        print("❌ اتصال ناموفق")
                        
                elif choice == "5":
                    print("\n👋 خروج...")
                    break
                    
                else:
                    print("❌ انتخاب نامعتبر!")
            
        else:
            print("❌ خطا در اتصال به دوربین!")
            
    except KeyboardInterrupt:
        print("\n⚠️ برنامه متوقف شد")
        
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")


if __name__ == "__main__":
    main()
