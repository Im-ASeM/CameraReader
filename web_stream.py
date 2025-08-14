#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نمایش استریم زنده دوربین از طریق مرورگر وب
"""

import time
import threading
import base64
import io
from camera_controller import CameraController
from flask import Flask, render_template, Response, jsonify
import requests
from PIL import Image
import numpy as np


class WebStreamServer:
    """سرور وب برای نمایش استریم دوربین"""
    
    def __init__(self, camera_controller, host='localhost', port=5000):
        self.camera = camera_controller
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.is_streaming = False
        self.frame_count = 0
        self.start_time = time.time()
        self.current_frame = None
        
        # تنظیم routes
        self.setup_routes()
    
    def setup_routes(self):
        """تنظیم مسیرهای وب"""
        
        @self.app.route('/')
        def index():
            """صفحه اصلی"""
            return self.render_main_page()
        
        @self.app.route('/stream')
        def video_stream():
            """استریم ویدیو"""
            return Response(
                self.generate_frames(),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )
        
        @self.app.route('/info')
        def camera_info():
            """اطلاعات دوربین"""
            if self.camera.is_connected:
                info = self.camera.get_camera_info()
                info['fps_display'] = round(self.calculate_fps(), 1)
                info['frame_count'] = self.frame_count
                return jsonify(info)
            else:
                return jsonify({'error': 'دوربین متصل نیست'})
        
        @self.app.route('/snapshot')
        def take_snapshot():
            """گرفتن عکس"""
            if self.current_frame is not None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"snapshots/web_capture_{timestamp}.jpg"
                success = self.camera.save_snapshot(filename)
                if success:
                    return jsonify({'success': True, 'filename': filename})
                else:
                    return jsonify({'success': False, 'error': 'خطا در ذخیره عکس'})
            else:
                return jsonify({'success': False, 'error': 'فریم موجود نیست'})
    
    def render_main_page(self):
        """رندر صفحه اصلی HTML"""
        html_content = '''
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎥 استریم زنده دوربین ITC231-RF1A-IR</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .main-container {
            flex: 1;
            display: flex;
            gap: 20px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
            width: 100%;
        }
        
        .video-container {
            flex: 2;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        
        .video-stream {
            width: 100%;
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }
        
        .controls-panel {
            flex: 1;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            height: fit-content;
        }
        
        .info-section {
            margin-bottom: 30px;
        }
        
        .info-section h3 {
            color: #ffd700;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .info-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 10px;
            margin: 8px 0;
            border-radius: 8px;
            border-left: 4px solid #ffd700;
        }
        
        .controls-section h3 {
            color: #00ff88;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .btn {
            background: linear-gradient(45deg, #00ff88, #00cc6a);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            margin: 5px 0;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 255, 136, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #00ff88;
            margin-left: 10px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .footer {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        @media (max-width: 768px) {
            .main-container {
                flex-direction: column;
            }
            .header h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎥 استریم زنده دوربین ITC231-RF1A-IR</h1>
        <p>نمایش تصاویر زنده با کیفیت بالا</p>
    </div>
    
    <div class="main-container">
        <div class="video-container">
            <img src="/stream" alt="استریم زنده دوربین" class="video-stream" id="videoStream">
        </div>
        
        <div class="controls-panel">
            <div class="info-section">
                <h3>📊 اطلاعات دوربین</h3>
                <div class="info-item">
                    <strong>وضعیت:</strong> <span id="status">متصل</span>
                    <span class="status-indicator"></span>
                </div>
                <div class="info-item">
                    <strong>آدرس IP:</strong> <span id="ip">192.168.1.108</span>
                </div>
                <div class="info-item">
                    <strong>مدل:</strong> <span id="model">ITC231-RF1A-IR</span>
                </div>
                <div class="info-item">
                    <strong>رزولوشن:</strong> <span id="resolution">در حال بارگیری...</span>
                </div>
                <div class="info-item">
                    <strong>FPS:</strong> <span id="fps">در حال محاسبه...</span>
                </div>
                <div class="info-item">
                    <strong>تعداد فریم:</strong> <span id="frameCount">0</span>
                </div>
            </div>
            
            <div class="controls-section">
                <h3>🎮 کنترل‌ها</h3>
                <button class="btn" onclick="takeSnapshot()">
                    📸 گرفتن عکس
                </button>
                <button class="btn" onclick="refreshStream()">
                    🔄 تازه‌سازی استریم
                </button>
                <button class="btn" onclick="toggleFullscreen()">
                    🖥️ تمام صفحه
                </button>
                <button class="btn" onclick="window.location.reload()">
                    ↻ بارگیری مجدد صفحه
                </button>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>کنترل کننده دوربین تحت وب | طراحی شده با ❤️</p>
    </div>
    
    <script>
        // به‌روزرسانی اطلاعات دوربین
        function updateCameraInfo() {
            fetch('/info')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('status').textContent = 'قطع شده';
                        return;
                    }
                    
                    document.getElementById('resolution').textContent = data.resolution || 'نامشخص';
                    document.getElementById('fps').textContent = data.fps_display || '0';
                    document.getElementById('frameCount').textContent = data.frame_count || '0';
                })
                .catch(error => {
                    console.log('خطا در دریافت اطلاعات:', error);
                });
        }
        
        // گرفتن عکس
        function takeSnapshot() {
            fetch('/snapshot')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ عکس با موفقیت ذخیره شد: ' + data.filename);
                    } else {
                        alert('❌ خطا در گرفتن عکس: ' + data.error);
                    }
                })
                .catch(error => {
                    alert('❌ خطا در ارتباط با سرور');
                });
        }
        
        // تازه‌سازی استریم
        function refreshStream() {
            const img = document.getElementById('videoStream');
            const src = img.src;
            img.src = '';
            setTimeout(() => {
                img.src = src + '?t=' + new Date().getTime();
            }, 100);
        }
        
        // تمام صفحه
        function toggleFullscreen() {
            const video = document.getElementById('videoStream');
            if (document.fullscreenElement) {
                document.exitFullscreen();
            } else {
                video.requestFullscreen();
            }
        }
        
        // به‌روزرسانی خودکار هر 2 ثانیه
        setInterval(updateCameraInfo, 2000);
        
        // بارگیری اولیه
        updateCameraInfo();
        
        // مدیریت خطاهای تصویر
        document.getElementById('videoStream').onerror = function() {
            this.style.background = 'linear-gradient(45deg, #ff6b6b, #ee5a52)';
            this.alt = 'خطا در بارگیری استریم';
        };
    </script>
</body>
</html>
        '''
        return html_content
    
    def calculate_fps(self):
        """محاسبه FPS"""
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            return self.frame_count / elapsed_time
        return 0
    
    def generate_frames(self):
        """تولید فریم‌ها برای استریم"""
        while True:
            if not self.camera.is_connected:
                # فریم خطا
                yield self.create_error_frame()
                time.sleep(1)
                continue
            
            try:
                # دریافت فریم از دوربین
                frame = self.camera.capture_frame()
                
                if frame is not None:
                    self.current_frame = frame
                    self.frame_count += 1
                    
                    # اضافه کردن timestamp
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    import cv2
                    cv2.putText(frame, timestamp, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # تبدیل به JPEG
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    else:
                        yield self.create_error_frame()
                else:
                    yield self.create_error_frame()
                    
            except Exception as e:
                print(f"خطا در تولید فریم: {str(e)}")
                yield self.create_error_frame()
            
            time.sleep(0.033)  # ~30 FPS
    
    def create_error_frame(self):
        """ایجاد فریم خطا"""
        try:
            import cv2
            import numpy as np
            
            # ایجاد تصویر خطا
            error_img = np.zeros((480, 640, 3), dtype=np.uint8)
            error_img[:] = (50, 50, 100)  # پس‌زمینه قرمز تیره
            
            # متن خطا
            cv2.putText(error_img, "Camera Connection Lost", (120, 200), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(error_img, "Trying to reconnect...", (140, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # تبدیل به JPEG
            ret, buffer = cv2.imencode('.jpg', error_img)
            if ret:
                frame_bytes = buffer.tobytes()
                return (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except:
            pass
        
        # فریم پیش‌فرض در صورت خطا
        return (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + b'error' + b'\r\n')
    
    def start_server(self):
        """شروع سرور وب"""
        self.is_streaming = True
        print(f"🌐 سرور وب در حال اجرا...")
        print(f"🔗 آدرس: http://{self.host}:{self.port}")
        print("⚠️ برای توقف سرور، Ctrl+C را فشار دهید")
        
        self.app.run(
            host=self.host,
            port=self.port,
            debug=False,
            threaded=True,
            use_reloader=False
        )


def main():
    """تابع اصلی"""
    
    # مشخصات دوربین
    CAMERA_IP = "192.168.1.108"
    USERNAME = "admin"
    PASSWORD = "ArashArash"
    
    print("=" * 60)
    print("🌐 سرور وب استریم زنده دوربین ITC231-RF1A-IR")
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
            
            # ایجاد سرور وب
            web_server = WebStreamServer(camera)
            
            # شروع سرور
            web_server.start_server()
            
        else:
            print("❌ خطا در اتصال به دوربین!")
            print("💡 راهنمایی:")
            print("   - آدرس IP دوربین را بررسی کنید")
            print("   - اتصال شبکه را بررسی کنید")
            print("   - نام کاربری و رمز عبور را بررسی کنید")
            
    except KeyboardInterrupt:
        print("\n⚠️ سرور متوقف شد")
        
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {str(e)}")
        
    finally:
        camera.close_camera()
        print("🔒 اتصال بسته شد")


if __name__ == "__main__":
    main()
