# AI_Voice/module/audio_capture.py

import sounddevice as sd
import threading
import numpy as np
from typing import Optional, Tuple
import time


RATE = 16000
MAX_DURATION = 10
MIN_RMS_THRESHOLD = 0.01  # Minimum audio energy to consider valid
MIN_DURATION = 0.5  # Minimum recording duration in seconds


class AudioRecorder:
    """Thread-safe audio recorder with validation"""
    
    def __init__(self, sample_rate=RATE, max_duration=MAX_DURATION):
        self.sample_rate = sample_rate
        self.max_duration = max_duration
        self.recording = []
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()  # Thread safety
        self.stream = None
        self.start_time = None
        
    def audio_callback(self, indata, frames, time_info, status):
        """Thread-safe callback for audio capture"""
        if status:
            print(f"⚠️  Audio Status: {status}")
        
        if not self.stop_flag.is_set():
            # Thread-safe append with lock
            with self.lock:
                self.recording.append(indata.copy())
    
    def calculate_rms(self, audio_data: np.ndarray) -> float:
        """Calculate Root Mean Square (audio energy level)"""
        return np.sqrt(np.mean(audio_data ** 2))
    
    def validate_audio(self, audio_data: np.ndarray) -> Tuple[bool, str]:
        """
        Validate recorded audio quality
        
        Returns:
            (is_valid, message)
        """
        # Check if empty
        if len(audio_data) == 0:
            return False, "Empty recording - no audio captured"
        
        # Check duration
        duration = len(audio_data) / self.sample_rate
        if duration < MIN_DURATION:
            return False, f"Recording too short: {duration:.2f}s (min: {MIN_DURATION}s)"
        
        # Check if audio contains any sound (RMS threshold)
        rms = self.calculate_rms(audio_data)
        if rms < MIN_RMS_THRESHOLD:
            return False, f"Audio too quiet (RMS: {rms:.4f}). No speech detected."
        
        # Check for clipping (values at -1 or 1)
        max_val = np.abs(audio_data).max()
        if max_val >= 0.99:
            print(f"⚠️  Warning: Audio may be clipped (max: {max_val:.3f})")
        
        # Check for NaN or Inf values
        if not np.isfinite(audio_data).all():
            return False, "Audio contains invalid values (NaN or Inf)"
        
        return True, "Audio valid"
    
    def normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio to [-0.95, 0.95] range"""
        max_val = np.abs(audio_data).max()
        if max_val > 0:
            audio_data = audio_data / max_val * 0.95
        return audio_data
    
    def record_audio(self) -> Optional[np.ndarray]:
        """
        Record audio with validation
        
        Returns:
            numpy array (float32, 1D) ready for Whisper, or None if invalid
        """
        print("🎤 Recording... (Press Enter to stop, or wait 60 seconds)")
        
        # Reset state
        with self.lock:
            self.recording = []
        self.stop_flag.clear()
        self.start_time = time.time()
        
        try:
            # Start audio stream with optimized settings
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self.audio_callback,
                blocksize=int(self.sample_rate * 0.1),  # 100ms chunks
                latency='low'
            )
            
            with self.stream:
                # Wait for Enter key in separate thread
                def wait_enter():
                    try:
                        input()
                        self.stop_flag.set()
                    except EOFError:
                        pass  # Handle non-interactive environments
                
                enter_thread = threading.Thread(target=wait_enter, daemon=True)
                enter_thread.start()
                
                # Wait for Enter or timeout
                self.stop_flag.wait(timeout=self.max_duration)
                self.stop_flag.set()
                
                # Small delay to ensure last chunks are captured
                time.sleep(0.2)
            
        except Exception as e:
            print(f"❌ Recording error: {e}")
            return None
        
        finally:
            # Cleanup
            if self.stream and not self.stream.closed:
                self.stream.close()
        
        # Calculate actual duration
        actual_duration = time.time() - self.start_time
        
        print(f"🛑 Recording complete ({actual_duration:.2f}s)")
        
        # Process recorded chunks with thread safety
        with self.lock:
            if not self.recording:
                print("❌ Error: No audio data captured")
                return None
            
            try:
                # Concatenate all chunks
                audio_data = np.concatenate(self.recording, axis=0)
            except ValueError as e:
                print(f"❌ Error concatenating audio: {e}")
                return None
        
        # Convert to 1D float32 for Whisper
        audio_data = audio_data.flatten().astype(np.float32)
        
        # Validate audio quality
        is_valid, message = self.validate_audio(audio_data)
        
        if not is_valid:
            print(f"❌ Invalid audio: {message}")
            return None
        
        print(f"✅ {message}")
        
        # Normalize audio
        audio_data = self.normalize_audio(audio_data)
        
        # Print stats
        duration = len(audio_data) / self.sample_rate
        rms = self.calculate_rms(audio_data)
        max_val = np.abs(audio_data).max()
        
        print(f"📊 Audio Stats:")
        print(f"   - Duration: {duration:.2f}s")
        print(f"   - Samples: {len(audio_data):,}")
        print(f"   - RMS Energy: {rms:.4f}")
        print(f"   - Peak Level: {max_val:.3f}")
        print(f"   - Sample Rate: {self.sample_rate} Hz")
        
        return audio_data


# Simple wrapper function for backward compatibility
def record_audio() -> Optional[np.ndarray]:
    """
    Record audio and return numpy array ready for Whisper
    
    Returns:
        numpy array (float32, 1D) or None if recording failed
    """
    recorder = AudioRecorder(sample_rate=RATE, max_duration=MAX_DURATION)
    return recorder.record_audio()
