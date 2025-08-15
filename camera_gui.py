#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
برنامه Windows Forms برای نمایش استریم زنده دوربین و گرفتن عکس
"""

import sys
import time
import threading
import requests
import cv2
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QWidget, QGridLayout,
                             QGroupBox, QTextEdit, QProgressBar, QStatusBar,
                             QMessageBox, QFileDialog, QComboBox, QSpinBox,
                             QCheckBox, QSlider, QFrame)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor, QIcon


class CameraStream(QThread):
    """Thread برای دریافت استریم دوربین"""
    frame_ready = pyqtSignal(np.ndarray)
    connection_status = pyqtSignal(bool, str)
    
    def __init__(self, ip, username, password):
        super().__init__()
        self.ip = ip
        self.username = username
        self.password = password
        self.running = False
        self.cap = None
        
        # آدرس‌های ممکن برای استریم
        self.stream_urls = [
            f"rtsp://{username}:{password}@{ip}:554/cam/realmonitor?channel=1&subtype=0",
            f"rtsp://{username}:{password}@{ip}/video1",
            f"http://{username}:{password}@{ip}/videostream.cgi",
            f"http://{username}:{password}@{ip}/mjpeg"
        ]
    
    def start_stream(self):
        """شروع استریم"""
        self.running = True
        self.start()
    
    def stop_stream(self):
        """توقف استریم"""
        self.running = False
        if self.cap:
            self.cap.release()
        self.quit()
        self.wait()
    
    def run(self):
        """اجرای thread"""
        connected = False
        
        for url in self.stream_urls:
            try:
                self.connection_status.emit(False, f"تلاش برای اتصال به: {url}")
                
                self.cap = cv2.VideoCapture(url)
                if self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        connected = True
                        self.connection_status.emit(True, f"اتصال موفق: {url}")
                        break
                    else:
                        self.cap.release()
                        
            except Exception as e:
                self.connection_status.emit(False, f"خطا: {str(e)}")
                continue
        
        if not connected:
            self.connection_status.emit(False, "هیچ استریمی در دسترس نیست")
            return
        
        # حلقه دریافت فریم
        while self.running and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.frame_ready.emit(frame)
                else:
                    self.connection_status.emit(False, "خطا در دریافت فریم")
                    break
                    
                self.msleep(33)  # ~30 FPS
                
            except Exception as e:
                self.connection_status.emit(False, f"خطا در استریم: {str(e)}")
                break
        
        if self.cap:
            self.cap.release()


class CameraGUI(QMainWindow):
    """کلاس اصلی برنامه گرافیکی"""
    
    def __init__(self):
        super().__init__()
        
        # تنظیمات دوربین
        self.camera_ip = "192.168.1.108"
        self.username = "admin"
        self.password = "ArashArash"
        
        # متغیرهای داخلی
        self.stream_thread = None
        self.current_frame = None
        self.is_streaming = False
        self.frame_count = 0
        self.start_time = time.time()
        
        # راه‌اندازی رابط
        self.init_ui()
        self.setup_styles()
        
        # تایمر برای به‌روزرسانی اطلاعات
        self.info_timer = QTimer()
        self.info_timer.timeout.connect(self.update_info)
        self.info_timer.start(1000)  # هر ثانیه
        
        # شروع خودکار استریم بعد از راه‌اندازی کامل UI
        QTimer.singleShot(500, self.auto_start_streaming)
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setWindowTitle("🎥 کنترل کننده دوربین ITC231-RF1A-IR")
        self.setGeometry(100, 100, 1200, 800)
        
        # ویجت اصلی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # طرح‌بندی اصلی
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # بخش نمایش ویدیو
        video_group = self.create_video_section()
        main_layout.addWidget(video_group, 2)
        
        # بخش کنترل‌ها
        control_group = self.create_control_section()
        main_layout.addWidget(control_group, 1)
        
        # نوار وضعیت
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("آماده")
    
    def create_video_section(self):
        """ایجاد بخش نمایش ویدیو"""
        group = QGroupBox("📺 نمایش زنده")
        layout = QVBoxLayout()
        
        # نمایش‌دهنده ویدیو
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("""
            QLabel {
                border: 3px solid #2196F3;
                border-radius: 10px;
                background-color: #1e1e1e;
                color: white;
                font-size: 16px;
                text-align: center;
            }
        """)
        self.video_label.setText("🎥\n\nدر حال اتصال به دوربین...\n\nاستریم خودکار شروع می‌شود")
        self.video_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.video_label)
        
        # کنترل‌های ویدیو - فقط دکمه عکس‌گیری
        video_controls = QHBoxLayout()
        
        self.snapshot_btn = QPushButton("📸 گرفتن عکس")
        self.snapshot_btn.clicked.connect(self.take_snapshot)
        self.snapshot_btn.setEnabled(False)
        
        video_controls.addWidget(self.snapshot_btn)
        
        layout.addLayout(video_controls)
        group.setLayout(layout)
        
        return group
    
    def create_control_section(self):
        """ایجاد بخش کنترل‌ها"""
        group = QGroupBox("🎛️ کنترل‌ها")
        layout = QVBoxLayout()
        
        # اطلاعات دوربین
        info_group = QGroupBox("📋 اطلاعات دوربین")
        info_layout = QGridLayout()
        
        info_layout.addWidget(QLabel("آدرس IP:"), 0, 0)
        self.ip_label = QLabel(self.camera_ip)
        info_layout.addWidget(self.ip_label, 0, 1)
        
        info_layout.addWidget(QLabel("نام کاربری:"), 1, 0)
        self.user_label = QLabel(self.username)
        info_layout.addWidget(self.user_label, 1, 1)
        
        info_layout.addWidget(QLabel("مدل:"), 2, 0)
        self.model_label = QLabel("ITC231-RF1A-IR")
        info_layout.addWidget(self.model_label, 2, 1)
        
        info_layout.addWidget(QLabel("وضعیت:"), 3, 0)
        self.status_label = QLabel("❌ قطع")
        info_layout.addWidget(self.status_label, 3, 1)
        
        info_layout.addWidget(QLabel("FPS:"), 4, 0)
        self.fps_label = QLabel("0.0")
        info_layout.addWidget(self.fps_label, 4, 1)
        
        info_layout.addWidget(QLabel("فریم‌ها:"), 5, 0)
        self.frame_label = QLabel("0")
        info_layout.addWidget(self.frame_label, 5, 1)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # تنظیمات عکس
        photo_group = QGroupBox("📷 تنظیمات عکس")
        photo_layout = QVBoxLayout()
        
        # کیفیت عکس
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("کیفیت:"))
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(95)
        self.quality_label_val = QLabel("95%")
        self.quality_slider.valueChanged.connect(
            lambda v: self.quality_label_val.setText(f"{v}%")
        )
        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.quality_label_val)
        photo_layout.addLayout(quality_layout)
        
        # نام‌گذاری خودکار
        self.auto_naming = QCheckBox("نام‌گذاری خودکار با زمان")
        self.auto_naming.setChecked(True)
        photo_layout.addWidget(self.auto_naming)
        
        photo_group.setLayout(photo_layout)
        layout.addWidget(photo_group)
        
        # کنترل‌های اضافی
        extra_group = QGroupBox("⚙️ عملیات")
        extra_layout = QVBoxLayout()
        
        self.test_btn = QPushButton("🔍 تست اتصال")
        self.test_btn.clicked.connect(self.test_connection)
        
        self.save_settings_btn = QPushButton("💾 ذخیره تنظیمات")
        self.save_settings_btn.clicked.connect(self.save_settings)
        
        self.about_btn = QPushButton("ℹ️ درباره برنامه")
        self.about_btn.clicked.connect(self.show_about)
        
        extra_layout.addWidget(self.test_btn)
        extra_layout.addWidget(self.save_settings_btn)
        extra_layout.addWidget(self.about_btn)
        
        extra_group.setLayout(extra_layout)
        layout.addWidget(extra_group)
        
        # لاگ
        log_group = QGroupBox("📝 لاگ رویدادها")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("background-color: #2b2b2b; color: #00ff00; font-family: Consolas;")
        
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        group.setLayout(layout)
        return group
    
    def setup_styles(self):
        """تنظیم استایل‌ها"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 10px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QLabel {
                font-size: 12px;
            }
        """)
    
    def log_message(self, message):
        """اضافه کردن پیام به لاگ"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        
        # نگه داشتن حداکثر 100 خط
        if self.log_text.document().blockCount() > 100:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.movePosition(cursor.Down, cursor.KeepAnchor)
            cursor.removeSelectedText()
    
    def auto_start_streaming(self):
        """شروع خودکار استریم هنگام راه‌اندازی برنامه"""
        self.log_message("شروع خودکار استریم...")
        self.start_streaming()
        
        # اگر اتصال برقرار نشد، هر 10 ثانیه دوباره سعی کن
        self.retry_timer = QTimer()
        self.retry_timer.timeout.connect(self.retry_connection)
        self.retry_timer.start(10000)  # هر 10 ثانیه
    
    def retry_connection(self):
        """تلاش مجدد برای اتصال"""
        if not self.is_streaming:
            self.log_message("تلاش مجدد برای اتصال...")
            self.start_streaming()
        else:
            # اگر استریم فعال است، تایمر را متوقف کن
            if hasattr(self, 'retry_timer'):
                self.retry_timer.stop()
    
    def start_streaming(self):
        """شروع استریم"""
        if self.is_streaming:
            return
        
        self.log_message("شروع اتصال به دوربین...")
        self.status_bar.showMessage("در حال اتصال...")
        
        # ایجاد thread استریم
        self.stream_thread = CameraStream(self.camera_ip, self.username, self.password)
        self.stream_thread.frame_ready.connect(self.update_frame)
        self.stream_thread.connection_status.connect(self.handle_connection_status)
        
        # شروع استریم
        self.stream_thread.start_stream()
        
        # فعال کردن دکمه عکس‌گیری
        self.snapshot_btn.setEnabled(True)
        
        self.is_streaming = True
        self.frame_count = 0
        self.start_time = time.time()
    
    def stop_streaming(self):
        """توقف استریم - فقط برای بستن برنامه"""
        if not self.is_streaming:
            return
        
        self.log_message("توقف استریم...")
        
        if self.stream_thread:
            self.stream_thread.stop_stream()
            self.stream_thread = None
        
        # غیرفعال کردن دکمه عکس‌گیری
        self.snapshot_btn.setEnabled(False)
        
        self.is_streaming = False
        self.status_label.setText("❌ قطع")
    
    def update_frame(self, frame):
        """به‌روزرسانی فریم نمایش"""
        try:
            self.current_frame = frame.copy()
            self.frame_count += 1
            
            # اضافه کردن timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # تبدیل BGR به RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # ایجاد QImage
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # مقیاس‌بندی برای نمایش
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(
                self.video_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            self.video_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.log_message(f"خطا در نمایش فریم: {str(e)}")
    
    def handle_connection_status(self, connected, message):
        """مدیریت وضعیت اتصال"""
        self.log_message(message)
        
        if connected:
            self.status_label.setText("✅ متصل")
            self.status_bar.showMessage("استریم فعال")
        else:
            self.status_label.setText("❌ قطع")
            if self.is_streaming:
                self.status_bar.showMessage("خطا در استریم")
    
    def take_snapshot(self):
        """گرفتن عکس"""
        if self.current_frame is None:
            QMessageBox.warning(self, "خطا", "هیچ فریمی برای ذخیره موجود نیست!")
            return
        
        try:
            # تعیین نام فایل
            if self.auto_naming.isChecked():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"snapshots/gui_capture_{timestamp}.jpg"
            else:
                filename, _ = QFileDialog.getSaveFileName(
                    self, "ذخیره عکس", "snapshot.jpg", "JPEG files (*.jpg);;All files (*.*)"
                )
                if not filename:
                    return
            
            # ایجاد پوشه در صورت نیاز
            import os
            os.makedirs("snapshots", exist_ok=True)
            
            # ذخیره عکس
            quality = self.quality_slider.value()
            cv2.imwrite(filename, self.current_frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
            
            self.log_message(f"عکس ذخیره شد: {filename}")
            QMessageBox.information(self, "موفقیت", f"عکس با موفقیت ذخیره شد:\n{filename}")
            
        except Exception as e:
            error_msg = f"خطا در ذخیره عکس: {str(e)}"
            self.log_message(error_msg)
            QMessageBox.critical(self, "خطا", error_msg)
    
    def test_connection(self):
        """تست اتصال به دوربین"""
        self.log_message("تست اتصال به دوربین...")
        self.test_btn.setEnabled(False)
        
        try:
            import requests
            response = requests.get(f"http://{self.camera_ip}", timeout=5)
            if response.status_code == 200:
                self.log_message("✅ تست اتصال موفق")
                QMessageBox.information(self, "موفقیت", "اتصال به دوربین موفق است!")
            else:
                self.log_message(f"❌ تست اتصال ناموفق: {response.status_code}")
                QMessageBox.warning(self, "هشدار", f"کد خطا: {response.status_code}")
        except Exception as e:
            error_msg = f"❌ خطا در تست اتصال: {str(e)}"
            self.log_message(error_msg)
            QMessageBox.critical(self, "خطا", error_msg)
        
        self.test_btn.setEnabled(True)
    
    def save_settings(self):
        """ذخیره تنظیمات"""
        settings = {
            'camera_ip': self.camera_ip,
            'username': self.username,
            'quality': self.quality_slider.value(),
            'auto_naming': self.auto_naming.isChecked()
        }
        
        try:
            import json
            with open('camera_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            self.log_message("تنظیمات ذخیره شد")
            QMessageBox.information(self, "موفقیت", "تنظیمات با موفقیت ذخیره شد!")
            
        except Exception as e:
            error_msg = f"خطا در ذخیره تنظیمات: {str(e)}"
            self.log_message(error_msg)
            QMessageBox.critical(self, "خطا", error_msg)
    
    def show_about(self):
        """نمایش اطلاعات برنامه"""
        about_text = """
🎥 کنترل کننده دوربین ITC231-RF1A-IR

نسخه: 1.0
طراح: برنامه‌نویس پایتون

ویژگی‌ها:
• نمایش استریم زنده دوربین
• گرفتن عکس با کیفیت قابل تنظیم
• رابط گرافیکی کاربرپسند
• ذخیره تنظیمات
• لاگ رویدادها

ساخته شده با PyQt5 و OpenCV
        """
        QMessageBox.about(self, "درباره برنامه", about_text)
    
    def update_info(self):
        """به‌روزرسانی اطلاعات"""
        if self.is_streaming and self.frame_count > 0:
            elapsed_time = time.time() - self.start_time
            fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0
            self.fps_label.setText(f"{fps:.1f}")
            self.frame_label.setText(str(self.frame_count))
    
    def closeEvent(self, event):
        """رویداد بستن برنامه"""
        if self.is_streaming:
            self.stop_streaming()
        event.accept()


def main():
    """تابع اصلی"""
    app = QApplication(sys.argv)
    
    # تنظیم فونت فارسی
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(9)
    app.setFont(font)
    
    # ایجاد و نمایش برنامه
    window = CameraGUI()
    window.show()
    
    # اجرای برنامه
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
