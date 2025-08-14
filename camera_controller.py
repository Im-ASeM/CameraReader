import cv2
import requests
import time
import base64
from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth
import numpy as np


class CameraController:
    """
    کنترل کننده دوربین ITC231-RF1A-IR
    """
    
    def __init__(self, ip_address, username, password, port=80):
        """
        مقداردهی اولیه کنترل کننده دوربین
        
        Args:
            ip_address (str): آدرس IP دوربین
            username (str): نام کاربری
            password (str): رمز عبور
            port (int): پورت اتصال (پیش‌فرض 80)
        """
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.port = port
        self.base_url = f"http://{ip_address}:{port}"
        self.auth = HTTPBasicAuth(username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.cap = None
        self.is_connected = False
        
    def test_connection(self):
        """
        تست اتصال به دوربین
        
        Returns:
            bool: True اگر اتصال موفق باشد
        """
        try:
            # تست اتصال با درخواست به صفحه اصلی دوربین
            response = self.session.get(
                f"{self.base_url}/",
                timeout=10,
                verify=False
            )
            
            if response.status_code == 200:
                print(f"✅ اتصال به دوربین {self.ip_address} موفق بود")
                return True
            else:
                print(f"❌ خطا در اتصال: کد وضعیت {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ خطا: زمان اتصال به پایان رسید")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ خطا: امکان اتصال به دوربین وجود ندارد")
            return False
        except Exception as e:
            print(f"❌ خطای غیرمنتظره: {str(e)}")
            return False
    
    def connect_stream(self):
        """
        اتصال به استریم ویدیویی دوربین
        
        Returns:
            bool: True اگر اتصال موفق باشد
        """
        try:
            # آدرس‌های مختلف برای استریم (RTSP و HTTP)
            stream_urls = [
                # RTSP URLs (معمولاً موثرتر)
                f"rtsp://{self.username}:{self.password}@{self.ip_address}:554/cam/realmonitor?channel=1&subtype=0",
                f"rtsp://{self.username}:{self.password}@{self.ip_address}/video1",
                f"rtsp://{self.username}:{self.password}@{self.ip_address}/ch1/main",
                f"rtsp://{self.username}:{self.password}@{self.ip_address}/stream1",
                
                # HTTP MJPEG URLs
                f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}/videostream.cgi",
                f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}/mjpeg",
                f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}/video.mjpg",
                f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}/cam/realmonitor?channel=1&subtype=0",
                f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}/snapshot.cgi",
                f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}/cgi-bin/snapshot.cgi",
                f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}/axis-cgi/mjpg/video.cgi",
                f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}/video",
                f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}/video1.mjpg",
                f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}/live.htm",
                f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}/videostream.asf"
            ]
            
            for url in stream_urls:
                print(f"🔄 تلاش برای اتصال به: {url}")
                self.cap = cv2.VideoCapture(url)
                
                if self.cap.isOpened():
                    # تست خواندن یک فریم
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        print(f"✅ اتصال به استریم موفق بود: {url}")
                        self.is_connected = True
                        return True
                    else:
                        self.cap.release()
                        
            print("❌ هیچ یک از آدرس‌های استریم کار نکرد")
            return False
            
        except Exception as e:
            print(f"❌ خطا در اتصال به استریم: {str(e)}")
            return False
    
    def open_camera(self):
        """
        باز کردن دوربین (تست اتصال + اتصال به استریم)
        
        Returns:
            bool: True اگر عملیات موفق باشد
        """
        print(f"🔄 شروع اتصال به دوربین {self.ip_address}...")
        
        # ابتدا تست اتصال
        if not self.test_connection():
            return False
            
        # سپس اتصال به استریم
        if not self.connect_stream():
            return False
            
        print("🎉 دوربین با موفقیت باز شد!")
        return True
    
    def close_camera(self):
        """
        بستن اتصال دوربین
        """
        try:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
                
            self.session.close()
            self.is_connected = False
            print("✅ اتصال دوربین بسته شد")
            
        except Exception as e:
            print(f"❌ خطا در بستن دوربین: {str(e)}")
    
    def capture_frame(self):
        """
        گرفتن یک فریم از دوربین
        
        Returns:
            numpy.ndarray: تصویر گرفته شده یا None در صورت خطا
        """
        if not self.is_connected or self.cap is None:
            print("❌ دوربین متصل نیست")
            return None
            
        ret, frame = self.cap.read()
        if ret:
            return frame
        else:
            print("❌ خطا در خواندن فریم")
            return None
    
    def show_live_stream(self, window_name="Camera Stream"):
        """
        نمایش استریم زنده دوربین
        
        Args:
            window_name (str): نام پنجره نمایش
        """
        if not self.is_connected:
            print("❌ ابتدا به دوربین متصل شوید")
            return
            
        print("🎥 نمایش استریم زنده شروع شد. برای خروج ESC را فشار دهید")
        
        while True:
            frame = self.capture_frame()
            if frame is not None:
                # نمایش تاریخ و زمان روی تصویر
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame, timestamp, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow(window_name, frame)
                
                # خروج با کلید ESC
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC key
                    break
            else:
                print("❌ خطا در دریافت فریم")
                break
                
        cv2.destroyAllWindows()
    
    def save_snapshot(self, filename=None):
        """
        ذخیره یک عکس از دوربین
        
        Args:
            filename (str): نام فایل (اختیاری)
            
        Returns:
            str: مسیر فایل ذخیره شده یا None در صورت خطا
        """
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{timestamp}.jpg"
            
        frame = self.capture_frame()
        if frame is not None:
            cv2.imwrite(filename, frame)
            print(f"✅ عکس ذخیره شد: {filename}")
            return filename
        else:
            print("❌ خطا در گرفتن عکس")
            return None
    
    def get_camera_info(self):
        """
        دریافت اطلاعات دوربین
        
        Returns:
            dict: اطلاعات دوربین
        """
        info = {
            "ip_address": self.ip_address,
            "username": self.username,
            "port": self.port,
            "model": "ITC231-RF1A-IR",
            "is_connected": self.is_connected
        }
        
        if self.is_connected and self.cap is not None:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            info.update({
                "resolution": f"{width}x{height}",
                "fps": fps
            })
            
        return info
