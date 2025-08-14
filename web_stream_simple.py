#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نمایش استریم زنده دوربین از طریق مرورگر وب - نسخه ساده
"""

import time
import threading
import base64
import io
from camera_controller import CameraController
from flask import Flask, render_template, Response, jsonify
import requests


class SimpleWebStream:
    """سرور وب ساده برای نمایش استریم دوربین"""
    
    def __init__(self, camera_controller, host='localhost', port=5000):
        self.camera = camera_controller
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.frame_count = 0
        self.start_time = time.time()
        
        # تنظیم routes
        self.setup_routes()
    
    def setup_routes(self):
        """تنظیم مسیرهای وب"""
        
        @self.app.route('/')
        def index():
            """صفحه اصلی"""
            return '''
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎥 استریم زنده دوربین</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a1a;
            color: white;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            text-align: center;
        }
        h1 {
            color: #00ff88;
            margin-bottom: 30px;
        }
        .video-container {
            background: #333;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .video-stream {
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }
        .controls {
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .btn {
            background: #00ff88;
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        .btn:hover {
            background: #00cc6a;
        }
        .info {
            background: #444;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            text-align: right;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎥 استریم زنده دوربین ITC231-RF1A-IR</h1>
        
        <div class="video-container">
            <img src="/stream" alt="استریم زنده" class="video-stream" id="stream">
        </div>
        
        <div class="controls">
            <button class="btn" onclick="takePhoto()">📸 گرفتن عکس</button>
            <button class="btn" onclick="refreshStream()">🔄 تازه‌سازی</button>
            <button class="btn" onclick="toggleFullscreen()">🖥️ تمام صفحه</button>
        </div>
        
        <div class="info">
            <h3>اطلاعات دوربین:</h3>
            <p><strong>آدرس:</strong> 192.168.1.108</p>
            <p><strong>مدل:</strong> ITC231-RF1A-IR</p>
            <p><strong>وضعیت:</strong> <span id="status">متصل</span></p>
        </div>
    </div>

    <script>
        function takePhoto() {
            fetch('/snapshot')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ عکس ذخیره شد: ' + data.filename);
                    } else {
                        alert('❌ خطا: ' + data.error);
                    }
                });
        }
        
        function refreshStream() {
            const img = document.getElementById('stream');
            img.src = img.src + '?t=' + new Date().getTime();
        }
        
        function toggleFullscreen() {
            const img = document.getElementById('stream');
            if (document.fullscreenElement) {
                document.exitFullscreen();
            } else {
                img.requestFullscreen();
            }
        }
    </script>
</body>
</html>
            '''
        
        @self.app.route('/stream')
        def video_stream():
            """استریم ویدیو مستقیم از دوربین"""
            def proxy_stream():
                try:
                    # اتصال مستقیم به استریم دوربین
                    stream_url = f"http://admin:ArashArash@192.168.1.108:80/videostream.cgi"
                    
                    # درخواست استریم
                    response = requests.get(stream_url, stream=True, timeout=10)
                    
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            yield chunk
                            
                except Exception as e:
                    print(f"خطا در استریم: {e}")
                    # فریم خطا
                    yield b'--frame\\r\\nContent-Type: image/jpeg\\r\\n\\r\\n' + b'error' + b'\\r\\n'
            
            return Response(proxy_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
        @self.app.route('/snapshot')
        def take_snapshot():
            """گرفتن عکس"""
            if self.camera.is_connected:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"snapshots/web_{timestamp}.jpg"
                if self.camera.save_snapshot(filename):
                    return jsonify({'success': True, 'filename': filename})
                else:
                    return jsonify({'success': False, 'error': 'خطا در ذخیره'})
            else:
                return jsonify({'success': False, 'error': 'دوربین متصل نیست'})
    
    def start_server(self):
        """شروع سرور"""
        print(f"🌐 سرور وب در حال اجرا...")
        print(f"🔗 آدرس: http://{self.host}:{self.port}")
        print("🎥 برای مشاهده استریم، آدرس بالا را در مرورگر باز کنید")
        print("⚠️ برای توقف، Ctrl+C را فشار دهید")
        
        self.app.run(
            host=self.host,
            port=self.port,
            debug=False,
            threaded=True
        )


def main():
    """تابع اصلی"""
    
    CAMERA_IP = "192.168.1.108"
    USERNAME = "admin"
    PASSWORD = "ArashArash"
    
    print("=" * 50)
    print("🌐 سرور وب استریم دوربین")
    print("=" * 50)
    
    # ایجاد کنترل کننده دوربین
    camera = CameraController(CAMERA_IP, USERNAME, PASSWORD)
    
    try:
        print("🔄 بررسی اتصال دوربین...")
        
        if camera.test_connection():
            print("✅ دوربین در دسترس است!")
            
            # ایجاد سرور وب
            web_server = SimpleWebStream(camera)
            
            # شروع سرور
            web_server.start_server()
            
        else:
            print("❌ خطا در اتصال به دوربین!")
            
    except KeyboardInterrupt:
        print("\\n⚠️ سرور متوقف شد")
        
    except Exception as e:
        print(f"\\n❌ خطا: {str(e)}")
        
    finally:
        camera.close_camera()
        print("🔒 اتصال بسته شد")


if __name__ == "__main__":
    main()
