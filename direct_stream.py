#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نمایش مستقیم استریم دوربین در مرورگر
"""

from flask import Flask, Response
import requests
import time


app = Flask(__name__)

# مشخصات دوربین
CAMERA_IP = "192.168.1.108"
USERNAME = "admin"
PASSWORD = "ArashArash"
PORT = 80

# آدرس‌های ممکن برای استریم
STREAM_URLS = [
    f"http://{USERNAME}:{PASSWORD}@{CAMERA_IP}:{PORT}/videostream.cgi",
    f"http://{USERNAME}:{PASSWORD}@{CAMERA_IP}:{PORT}/mjpeg",
    f"http://{USERNAME}:{PASSWORD}@{CAMERA_IP}:{PORT}/video.mjpg",
    f"http://{USERNAME}:{PASSWORD}@{CAMERA_IP}:{PORT}/cam/realmonitor?channel=1&subtype=0"
]


@app.route('/')
def index():
    """صفحه اصلی"""
    return f'''
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎥 استریم زنده دوربین ITC231-RF1A-IR</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .video-container {{
            background: rgba(0, 0, 0, 0.4);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            max-width: 95vw;
            text-align: center;
        }}
        
        .video-stream {{
            max-width: 100%;
            max-height: 70vh;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            border: 3px solid rgba(255,255,255,0.2);
        }}
        
        .controls {{
            margin-top: 20px;
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        .btn {{
            background: linear-gradient(45deg, #00ff88, #00cc6a);
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3);
            min-width: 150px;
        }}
        
        .btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0, 255, 136, 0.4);
        }}
        
        .btn:active {{
            transform: translateY(-1px);
        }}
        
        .info-panel {{
            background: rgba(0, 0, 0, 0.4);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            max-width: 500px;
        }}
        
        .info-panel h3 {{
            color: #ffd700;
            margin-bottom: 15px;
            text-align: center;
        }}
        
        .info-item {{
            background: rgba(255, 255, 255, 0.1);
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 8px;
            border-right: 4px solid #00ff88;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .status-dot {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #00ff88;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.7; transform: scale(1.1); }}
            100% {{ opacity: 1; transform: scale(1); }}
        }}
        
        .footer {{
            margin-top: auto;
            text-align: center;
            padding: 20px;
            opacity: 0.8;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2em;
            }}
            .video-container {{
                padding: 20px;
            }}
            .btn {{
                min-width: 120px;
                padding: 12px 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎥 استریم زنده دوربین</h1>
        <p>ITC231-RF1A-IR | نمایش تصاویر با کیفیت بالا</p>
    </div>
    
    <div class="video-container">
        <img src="/stream" alt="استریم زنده دوربین" class="video-stream" id="videoStream">
        
        <div class="controls">
            <button class="btn" onclick="refreshStream()">🔄 تازه‌سازی استریم</button>
            <button class="btn" onclick="toggleFullscreen()">🖥️ تمام صفحه</button>
            <button class="btn" onclick="downloadFrame()">💾 دانلود فریم</button>
        </div>
    </div>
    
    <div class="info-panel">
        <h3>📊 اطلاعات دوربین</h3>
        <div class="info-item">
            <span><strong>وضعیت:</strong></span>
            <span>آنلاین <span class="status-dot"></span></span>
        </div>
        <div class="info-item">
            <span><strong>آدرس IP:</strong></span>
            <span>{CAMERA_IP}</span>
        </div>
        <div class="info-item">
            <span><strong>مدل:</strong></span>
            <span>ITC231-RF1A-IR</span>
        </div>
        <div class="info-item">
            <span><strong>پورت:</strong></span>
            <span>{PORT}</span>
        </div>
        <div class="info-item">
            <span><strong>زمان:</strong></span>
            <span id="currentTime">--</span>
        </div>
    </div>
    
    <div class="footer">
        <p>کنترل کننده دوربین تحت وب | طراحی شده با ❤️</p>
    </div>

    <script>
        // تازه‌سازی استریم
        function refreshStream() {{
            const img = document.getElementById('videoStream');
            const timestamp = new Date().getTime();
            const originalSrc = img.src.split('?')[0];
            img.src = originalSrc + '?refresh=' + timestamp;
            
            // نمایش پیام موفقیت
            showNotification('🔄 استریم تازه‌سازی شد');
        }}
        
        // تمام صفحه
        function toggleFullscreen() {{
            const video = document.getElementById('videoStream');
            
            if (document.fullscreenElement) {{
                document.exitFullscreen();
                showNotification('🖥️ خروج از حالت تمام صفحه');
            }} else {{
                video.requestFullscreen().then(() => {{
                    showNotification('🖥️ ورود به حالت تمام صفحه');
                }}).catch(err => {{
                    showNotification('❌ خطا در حالت تمام صفحه', 'error');
                }});
            }}
        }}
        
        // دانلود فریم فعلی
        function downloadFrame() {{
            const img = document.getElementById('videoStream');
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            ctx.drawImage(img, 0, 0);
            
            canvas.toBlob(function(blob) {{
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'camera_frame_' + new Date().getTime() + '.png';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                showNotification('💾 فریم دانلود شد');
            }});
        }}
        
        // نمایش اعلان
        function showNotification(message, type = 'success') {{
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: ${{type === 'error' ? '#ff4444' : '#00ff88'}};
                color: white;
                padding: 15px 25px;
                border-radius: 10px;
                font-weight: bold;
                z-index: 1000;
                animation: slideDown 0.3s ease;
            `;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {{
                notification.remove();
            }}, 3000);
        }}
        
        // به‌روزرسانی زمان
        function updateTime() {{
            const now = new Date();
            const timeString = now.toLocaleString('fa-IR');
            document.getElementById('currentTime').textContent = timeString;
        }}
        
        // مدیریت خطاهای بارگیری تصویر
        document.getElementById('videoStream').onerror = function() {{
            this.style.background = 'linear-gradient(45deg, #ff6b6b, #ee5a52)';
            this.alt = 'خطا در بارگیری استریم - در حال تلاش مجدد...';
            showNotification('⚠️ خطا در بارگیری استریم', 'error');
            
            // تلاش مجدد بعد از 3 ثانیه
            setTimeout(refreshStream, 3000);
        }};
        
        // اجرای اولیه
        updateTime();
        setInterval(updateTime, 1000);
        
        // کلیدهای میانبر
        document.addEventListener('keydown', function(e) {{
            switch(e.key) {{
                case 'r':
                case 'R':
                    refreshStream();
                    break;
                case 'f':
                case 'F':
                    toggleFullscreen();
                    break;
                case 'd':
                case 'D':
                    downloadFrame();
                    break;
            }}
        }});
        
        // اضافه کردن استایل انیمیشن
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideDown {{
                from {{ transform: translateX(-50%) translateY(-100%); opacity: 0; }}
                to {{ transform: translateX(-50%) translateY(0); opacity: 1; }}
            }}
        `;
        document.head.appendChild(style);
        
        console.log('🎥 استریم زنده دوربین ITC231-RF1A-IR آماده است!');
        console.log('میانبرهای کیبورد: R=تازه‌سازی، F=تمام‌صفحه، D=دانلود');
    </script>
</body>
</html>
    '''


@app.route('/stream')
def video_stream():
    """پروکسی استریم ویدیو"""
    def generate():
        # تلاش برای اتصال به هر یک از آدرس‌های ممکن
        for stream_url in STREAM_URLS:
            try:
                print(f"🔄 تلاش برای اتصال به: {stream_url}")
                
                response = requests.get(
                    stream_url, 
                    stream=True, 
                    timeout=10,
                    headers={{'User-Agent': 'Mozilla/5.0'}}
                )
                
                if response.status_code == 200:
                    print(f"✅ اتصال موفق به: {stream_url}")
                    
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            yield chunk
                    break
                    
            except Exception as e:
                print(f"❌ خطا در {stream_url}: {e}")
                continue
        
        # در صورت عدم موفقیت، ارسال پیام خطا
        error_response = b"""--frame\r\nContent-Type: text/plain\r\n\r\nخطا در اتصال به استریم دوربین\r\n"""
        yield error_response
    
    return Response(
        generate(), 
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


def main():
    """تابع اصلی"""
    print("=" * 60)
    print("🎥 سرور استریم مستقیم دوربین ITC231-RF1A-IR")
    print("=" * 60)
    print(f"🌐 آدرس سرور: http://localhost:5000")
    print(f"📡 دوربین: {CAMERA_IP}")
    print("🎬 برای مشاهده استریم، آدرس بالا را در مرورگر باز کنید")
    print("⚠️ برای توقف سرور، Ctrl+C را فشار دهید")
    print("=" * 60)
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n⚠️ سرور متوقف شد")
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")


if __name__ == "__main__":
    main()
