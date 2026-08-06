"""
Music Player Application for MiniOS
Simple audio player with play/pause, volume, and progress
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QMessageBox,
    QSlider, QFrame
)
from PySide6.QtCore import Qt, QTimer, QUrl, Signal
from PySide6.QtGui import QFont
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

import os


class MusicPlayerWidget(QWidget):
    """Music player application widget"""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.is_playing = False
        
        # Setup audio output
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.7)  # 70% volume
        
        # Setup media player
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.mediaStatusChanged.connect(self.handle_media_status)
        self.player.errorOccurred.connect(self.handle_error)
        self.player.playbackStateChanged.connect(self.handle_playback_state)
        
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #0d0d0d;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #888888;
                background: transparent;
            }
            QLabel#title {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
            }
            QLabel#now_playing {
                color: #cccccc;
                font-size: 14px;
            }
            QPushButton {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #888888;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #2a2a2a;
                color: #ffffff;
            }
            QPushButton#play_btn {
                background: #2a4a2a;
                border: 1px solid #3a5a3a;
                color: #88ff88;
                font-size: 20px;
                min-width: 60px;
                min-height: 60px;
            }
            QPushButton#play_btn:hover {
                background: #3a5a3a;
            }
            QSlider {
                height: 20px;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #1a1a1a;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #888888;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #aaaaaa;
            }
            QSlider::sub-page:horizontal {
                background: #2a5a2a;
                border-radius: 2px;
            }
            QSlider#volume_slider {
                max-width: 100px;
            }
            QSlider#volume_slider::sub-page:horizontal {
                background: #2a4a6a;
            }
            QFrame#separator {
                background: #1a1a1a;
                max-height: 1px;
                min-height: 1px;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🎵 Music Player")
        title.setObjectName("title")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet("color: #444444; font-size: 11px;")
        header_layout.addWidget(self.file_label)
        
        layout.addLayout(header_layout)
        
        # Separator
        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)
        
        # Now playing
        self.now_playing_label = QLabel("No music loaded")
        self.now_playing_label.setObjectName("now_playing")
        self.now_playing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.now_playing_label)
        
        # Progress bar
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)
        
        self.time_label = QLabel("0:00")
        self.time_label.setStyleSheet("color: #666666; font-size: 11px;")
        progress_layout.addWidget(self.time_label)
        
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.sliderMoved.connect(self.seek_position)
        progress_layout.addWidget(self.progress_slider)
        
        self.duration_label = QLabel("0:00")
        self.duration_label.setStyleSheet("color: #666666; font-size: 11px;")
        progress_layout.addWidget(self.duration_label)
        
        layout.addLayout(progress_layout)
        
        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.open_btn = QPushButton("📂")
        self.open_btn.setFixedSize(50, 50)
        self.open_btn.clicked.connect(self.open_file)
        self.open_btn.setToolTip("Open file (Ctrl+O)")
        control_layout.addWidget(self.open_btn)
        
        self.prev_btn = QPushButton("⏮")
        self.prev_btn.setFixedSize(50, 50)
        self.prev_btn.clicked.connect(self.prev_track)
        self.prev_btn.setEnabled(False)
        self.prev_btn.setToolTip("Previous track")
        control_layout.addWidget(self.prev_btn)
        
        self.play_btn = QPushButton("▶")
        self.play_btn.setObjectName("play_btn")
        self.play_btn.setFixedSize(70, 70)
        self.play_btn.clicked.connect(self.toggle_play)
        self.play_btn.setEnabled(False)
        control_layout.addWidget(self.play_btn)
        
        self.next_btn = QPushButton("⏭")
        self.next_btn.setFixedSize(50, 50)
        self.next_btn.clicked.connect(self.next_track)
        self.next_btn.setEnabled(False)
        self.next_btn.setToolTip("Next track")
        control_layout.addWidget(self.next_btn)
        
        control_layout.addStretch()
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(8)
        
        volume_label = QLabel("🔊")
        volume_label.setStyleSheet("color: #666666; font-size: 14px;")
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setObjectName("volume_slider")
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("70%")
        self.volume_label.setStyleSheet("color: #666666; font-size: 11px;")
        volume_layout.addWidget(self.volume_label)
        
        control_layout.addLayout(volume_layout)
        
        layout.addLayout(control_layout)
        
        layout.addStretch()
        
        self.setLayout(layout)
        
    def open_file(self):
        """Open an audio file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Audio File", "",
            "Audio Files (*.mp3 *.wav *.flac *.m4a *.ogg);;All Files (*)"
        )
        
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path):
        """Load an audio file"""
        self.current_file = file_path
        filename = os.path.basename(file_path)
        
        # Set media
        url = QUrl.fromLocalFile(file_path)
        self.player.setSource(url)
        
        # Update UI
        self.now_playing_label.setText(f"Loading: {filename}")
        self.file_label.setText(filename)
        self.play_btn.setEnabled(True)
        self.play_btn.setText("▶")
        self.is_playing = False
        
        # Enable buttons
        self.prev_btn.setEnabled(True)
        self.next_btn.setEnabled(True)
        
        print(f"Loaded: {file_path}")
    
    def toggle_play(self):
        """Toggle play/pause"""
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            # Currently playing - pause
            self.player.pause()
            self.is_playing = False
            self.play_btn.setText("▶")
            self.now_playing_label.setText(f"Paused: {os.path.basename(self.current_file)}" if self.current_file else "No music loaded")
        else:
            # Currently paused or stopped - play
            self.player.play()
            self.is_playing = True
            self.play_btn.setText("⏸")
            self.now_playing_label.setText(f"Playing: {os.path.basename(self.current_file)}" if self.current_file else "No music loaded")
    
    def set_volume(self, value):
        """Set volume level"""
        self.audio_output.setVolume(value / 100.0)
        self.volume_label.setText(f"{value}%")
    
    def seek_position(self, value):
        """Seek to position in track"""
        if self.player.duration() > 0:
            position = int(value * self.player.duration() / 1000)
            self.player.setPosition(position)
    
    def update_position(self, position):
        """Update position slider"""
        duration = self.player.duration()
        if duration > 0:
            progress = int(position * 1000 / duration)
            self.progress_slider.setValue(progress)
        
        # Update time label
        self.time_label.setText(self.format_time(position))
    
    def update_duration(self, duration):
        """Update duration label"""
        self.duration_label.setText(self.format_time(duration))
    
    def format_time(self, ms):
        """Format time in milliseconds to mm:ss"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def handle_playback_state(self, state):
        """Handle playback state changes"""
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self.is_playing = False
            self.play_btn.setText("▶")
            if self.current_file:
                self.now_playing_label.setText(f"Stopped: {os.path.basename(self.current_file)}")
    
    def handle_media_status(self, status):
        """Handle media status changes"""
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.now_playing_label.setText(f"Ready: {os.path.basename(self.current_file)}" if self.current_file else "No music loaded")
            self.play_btn.setEnabled(True)
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.is_playing = False
            self.play_btn.setText("▶")
            self.now_playing_label.setText("Track ended")
            self.progress_slider.setValue(0)
            self.time_label.setText("0:00")
    
    def handle_error(self, error):
        """Handle player errors"""
        error_messages = {
            QMediaPlayer.Error.NoError: "No error",
            QMediaPlayer.Error.ResourceError: "Resource error - file may be corrupted",
            QMediaPlayer.Error.FormatError: "Format error - unsupported audio format",
            QMediaPlayer.Error.NetworkError: "Network error",
            QMediaPlayer.Error.AccessDeniedError: "Access denied",
            QMediaPlayer.Error.ServiceMissingError: "Service missing - codec may not be installed"
        }
        
        error_msg = error_messages.get(error, f"Unknown error: {error}")
        QMessageBox.critical(self, "Player Error", f"Error playing audio:\n{error_msg}")
        self.play_btn.setText("▶")
        self.play_btn.setEnabled(False)
        self.now_playing_label.setText("Error loading file")
    
    def prev_track(self):
        """Go to previous track (placeholder)"""
        if self.current_file:
            self.player.setPosition(0)
            if self.is_playing:
                self.player.play()
    
    def next_track(self):
        """Go to next track (placeholder)"""
        if self.current_file:
            self.player.setPosition(0)
            self.player.play()
            self.is_playing = True
            self.play_btn.setText("⏸")
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_O and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.open_file()
        elif event.key() == Qt.Key.Key_Space:
            self.toggle_play()
        elif event.key() == Qt.Key.Key_Right:
            self.seek_position(min(self.progress_slider.value() + 50, 1000))
        elif event.key() == Qt.Key.Key_Left:
            self.seek_position(max(self.progress_slider.value() - 50, 0))
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle close event"""
        self.player.stop()
        event.accept()