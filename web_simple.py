#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سرور وب ساده برای نمایش استریم دوربین بدون OpenCV
"""

from flask import Flask, Response, jsonify
import requests
from camera_simple import SimpleCameraController
import time


class SimpleWebServer:
    """سرور وب ساده"""
    
    def __init__(self, camera_controller, host='localhost', port=5000):
        self.camera = camera_controller
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """تنظیم مسیرها"""
        
        @self.app.route('/')
        def index():
            return '''
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎥 استریم زنده دوربین</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            text-align: center;
        }
        h1 {
            color: #fff;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        .video-container {
            background: rgba(0,0,0,0.3);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        .video-stream {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }
        .controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
            margin: 20px 0;
        }
        .btn {
            background: linear-gradient(45deg, #00ff88, #00cc6a);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3);
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 255, 136, 0.4);
        }
        .info {
            background: rgba(0,0,0,0.4);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            text-align: right;
            backdrop-filter: blur(10px);
        }
        .info h3 {
            color: #ffd700;
            margin-bottom: 15px;
        }
        .info-item {
            background: rgba(255,255,255,0.1);
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 5px;
            border-right: 3px solid #ffd700;
        }
        .status {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #00ff88;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
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
            <button class="btn" onclick="showSnapshot()">🖼️ نمایش آخرین عکس</button>
            <button class="btn" onclick="toggleFullscreen()">🖥️ تمام صفحه</button>
        </div>
        
        <div class="info">
            <h3>📊 اطلاعات دوربین</h3>
            <div class="info-item">
                <span class="status"></span>
                <strong>وضعیت:</strong> متصل
            </div>
            <div class="info-item">
                <strong>آدرس IP:</strong> 192.168.1.108
            </div>
            <div class="info-item">
                <strong>مدل:</strong> ITC231-RF1A-IR
            </div>
            <div class="info-item">
                <strong>پورت:</strong> 80
            </div>
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
                })
                .catch(error => {
                    alert('❌ خطا در ارتباط با سرور');
                });
        }
        
        function refreshStream() {
            const img = document.getElementById('stream');
            const timestamp = new Date().getTime();
            img.src = '/stream?t=' + timestamp;
        }
        
        function showSnapshot() {
            window.open('/latest_snapshot', '_blank');
        }
        
        function toggleFullscreen() {
            const img = document.getElementById('stream');
            if (document.fullscreenElement) {
                document.exitFullscreen();
            } else {
                img.requestFullscreen().catch(err => {
                    alert('خطا در حالت تمام صفحه: ' + err.message);
                });
            }
        }
        
        // تازه‌سازی خودکار هر 30 ثانیه
        setInterval(refreshStream, 30000);
        
        // مدیریت خطاهای بارگیری تصویر
        document.getElementById('stream').onerror = function() {
            console.log('خطا در بارگیری استریم');
            setTimeout(refreshStream, 2000);
        };
    </script>
</body>
</html>
            '''
        
        @self.app.route('/stream')
        def video_stream():
            """پروکسی استریم ویدیو"""
            def generate():
                stream_url = self.camera.get_stream_url()
                if stream_url:
                    try:
                        response = requests.get(stream_url, stream=True, timeout=10)
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                yield chunk
                    except Exception as e:
                        print(f"خطا در استریم: {e}")
                        yield b"error"
                else:
                    yield b"no stream url found"
            
            return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
        @self.app.route('/snapshot')
        def take_snapshot():
            """گرفتن عکس"""
            result = self.camera.take_snapshot()
            if result:
                return jsonify({'success': True, 'filename': result})
            else:
                return jsonify({'success': False, 'error': 'خطا در گرفتن عکس'})
        
        @self.app.route('/info')
        def camera_info():
            """اطلاعات دوربین"""
            return jsonify(self.camera.get_camera_info())
    
    def start(self):
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
    camera = SimpleCameraController(CAMERA_IP, USERNAME, PASSWORD)
    
    try:
        print("🔄 بررسی اتصال دوربین...")
        
        if camera.test_connection():
            print("✅ دوربین در دسترس است!")
            
            # ایجاد سرور وب
            server = SimpleWebServer(camera)
            
            # شروع سرور
            server.start()
            
        else:
            print("❌ خطا در اتصال به دوربین!")
            
    except KeyboardInterrupt:
        print("\n⚠️ سرور متوقف شد")
        
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")


if __name__ == "__main__":
    main()
