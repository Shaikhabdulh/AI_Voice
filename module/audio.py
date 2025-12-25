# AI_Voice/audio.py

from faster_whisper import WhisperModel
from .audio_capture import record_audio
import sys


def whisper_transcription():
    """whisper_transcription transcription workflow"""
    print("="*60)
    print("🎙️  SPEECH-TO-TEXT TRANSCRIPTION")
    print("="*60 + "\n")
    
    # 1. Record the audio
    audio_data = record_audio()
    
    # 2. Validate recording
    if audio_data is None:
        print("\n❌ Recording failed or no valid audio captured.")
        print("💡 Tips:")
        print("   - Speak louder or move closer to microphone")
        print("   - Check microphone is not muted")
        print("   - Ensure recording duration > 0.5 seconds")
        print("   - Check microphone permissions")
        sys.exit(1)
    
    print("\n" + "="*60)
    
    # 3. Initialize Whisper model
    print("📝 Loading Whisper model...")
    try:
        model = WhisperModel(
            "small.en",  # Model size: tiny, base, small, medium, large-v3
            device="cpu",  # Device: cpu or cuda
            compute_type="float32",  # Compute type: int8 (faster) or float32 (more accurate)
            num_workers=4,  # Number of parallel workers
            cpu_threads=8  # CPU threads (adjust based on your CPU)
        )
        print("✅ Model loaded successfully\n")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        print("💡 Try installing: pip install faster-whisper")
        sys.exit(1)
    
    # 4. Transcribe with optimal settings
    print("🎯 Transcribing...\n")
    
    try:
        segments, info = model.transcribe(
            audio_data,
            language="en",  # Language code or None for auto-detect

            patience=1.0,                 # Higher values (e.g. 2.0) make beam search more thorough

            # VAD (Voice Activity Detection) - removes silence
            vad_filter=True,
            vad_parameters=dict(
                threshold=0.5,  # 0.0-1.0, higher = more aggressive filtering
                min_speech_duration_ms=250,  # Minimum speech segment length
                max_speech_duration_s=float('inf'),  # Maximum speech segment length
                min_silence_duration_ms=2000,  # Minimum silence to split segments
                speech_pad_ms=400  # Padding around speech segments
                # NOTE: window_size_samples is NOT a valid parameter - it's hardcoded
            ),
            
            # Hallucination prevention parameters
            beam_size=5,  # Higher = more accurate but slower (1-10)
            best_of=5,  # Number of candidates to consider
            temperature=0.0,  # Use 0.0 for deterministic output
            compression_ratio_threshold=2.4,  # Detect repetitive text
            log_prob_threshold=-1.0,  # Filter low confidence predictions
            no_speech_threshold=0.6,  # Threshold for detecting silence
            condition_on_previous_text=False,  # Reduce context-based hallucinations
            
            # Optional: Word-level timestamps
            word_timestamps=False,  # Set True for word-by-word timing
            
            # Optional: Initial prompt for better context
            # initial_prompt="This is a conversation about technical topics."
        )
        
        # 5. Process and display results
        print("="*60)
        print("📄 TRANSCRIPTION RESULTS")
        print("="*60 + "\n")
        
        # Display detected language and audio info
        print(f"🌐 Detected Language: {info.language} (probability: {info.language_probability:.2%})")
        print(f"⏱️  Audio Duration: {info.duration:.2f}s")
        if hasattr(info, 'duration_after_vad'):
            print(f"🔊 Speech Duration (after VAD): {info.duration_after_vad:.2f}s")
        print()
        
        # Collect and display segments
        transcription_parts = []
        has_speech = False
        
        for segment in segments:
            text = segment.text.strip()
            if text:
                has_speech = True
                # Display with timestamps
                print(f"[{segment.start:6.2f}s -> {segment.end:6.2f}s] {text}")
                transcription_parts.append(text)
        
        # 6. Display final results
        if not has_speech:
            print("⚠️  No speech detected in audio")
            print("💡 Try speaking louder or closer to the microphone")
        else:
            full_transcription = " ".join(transcription_parts)
            
            print("\n" + "="*60)
            print("📋 FULL TRANSCRIPTION")
            print("="*60)
            print(f"\n{full_transcription}\n")
            print("="*60)
            
            # # Save to file
            # try:
            #     with open("transcription.txt", "w", encoding="utf-8") as f:
            #         f.write(full_transcription)
            #     print("\n💾 Transcription saved to: transcription.txt")
            # except Exception as e:
            #     print(f"\n⚠️  Could not save file: {e}")
            
        print("\n✅ Done!")
        return full_transcription
    
    except Exception as e:
        print(f"\n❌ Transcription error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        return None

if __name__ == "__whisper_transcription__":
    try:
        whisper_transcription()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
