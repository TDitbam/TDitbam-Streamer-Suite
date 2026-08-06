import os
import time
import queue
import threading
import asyncio
import re
import traceback
import base64
import json
import wave
import urllib.error
import urllib.request
from typing import Dict, Any, Optional

import edge_tts
from deep_translator import GoogleTranslator
from pygame import mixer
from gtts import gTTS

from .app_logger import get_logger, get_app_dir
from .thai_separator import translate_mixed_text
from .collectors.yt_chat import youtube_collector
from .collectors.twitch_chat import twitch_collector
from .collectors.tiktok_chat import tiktok_collector

logger = get_logger("Engine")

class ChatTTSEngine:
    def __init__(self):
        self.is_running = False
        self.current_session_id = 0
        self.msg_queue = queue.Queue(maxsize=100)
        self.audio_queue = queue.Queue(maxsize=100)
        self.seen_messages = set()
        self.max_seen_messages = 500
        self.threads = []
        self._lifecycle_lock = threading.RLock()
        self._mixer_lock = threading.Lock()
        self._session_stop_event = threading.Event()
        
        # ใช้ AppData แทนโฟลเดอร์ปัจจุบัน
        app_dir = get_app_dir()
        self.msg_dir = os.path.join(app_dir, "msg_queue")
        self.audio_dir = os.path.join(app_dir, "temp_audio")
        self.profanity_file = os.path.join(app_dir, "bad_words.txt")
        
        self._ensure_directories()
        
        self.voice = "th-TH-PremwadeeNeural"
        self.voice_provider = "edge"
        self.gtts_language = "th"
        self.gemini_api_key = ""
        self.gemini_model = "gemini-3.1-flash-tts-preview"
        self.gemini_voice = "Kore"
        self.gemini_style = "Read the transcript naturally and clearly."
        self.openai_api_key = ""
        self.openai_model = "tts-1"
        self.openai_voice = "alloy"
        self.openai_instructions = "Speak naturally and clearly."
        self.openai_speed = 1.0
        self.delay_per_char = 0.03
        self.max_delay = 2.0
        self.auto_translate = False
        self.translator = GoogleTranslator(source='auto', target='th')
        
        # Profanity Filter
        self.profanity_enabled = False
        self.profanity_list = []
        self._load_profanity_list()
        
        self._init_mixer()

    def _clear_queues(self):
        """Empty both message and audio queues."""
        while not self.msg_queue.empty():
            try: self.msg_queue.get_nowait()
            except queue.Empty: break
            
        while not self.audio_queue.empty():
            try: self.audio_queue.get_nowait()
            except queue.Empty: break
        logger.info("Queues cleared.")

    def _load_profanity_list(self):
        """Load profanity list from file."""
        if os.path.exists(self.profanity_file):
            try:
                with open(self.profanity_file, "r", encoding="utf-8") as f:
                    self.profanity_list = [line.strip().lower() for line in f if line.strip()]
                logger.info(f"Loaded {len(self.profanity_list)} profanity words.")
            except Exception as e:
                logger.error(f"Failed to load profanity list: {e}")
        else:
            self.profanity_list = []

    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        for d in [self.msg_dir, self.audio_dir]:
            if not os.path.exists(d): 
                os.makedirs(d)

    def _init_mixer(self):
        """Initialize pygame mixer."""
        try:
            mixer.init()
        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {e}")

    def _cleanup_temp_files(self):
        """Remove old files from transient directories."""
        logger.info("Cleaning up old files...")
        for d in [self.msg_dir, self.audio_dir]:
            if os.path.exists(d):
                for f in os.listdir(d):
                    try: 
                        # Mandatory for Windows: check if it's an mp3 and ensure mixer is unloaded elsewhere
                        os.remove(os.path.join(d, f))
                    except Exception as e: 
                        logger.debug(f"Could not remove {f}: {e}")

    def extract_video_id(self, url_or_id: str) -> str:
        """Extract YouTube video ID from URL or return raw ID."""
        patterns = [
            r"v=([a-zA-Z0-9_-]{11})", 
            r"youtu\.be/([a-zA-Z0-9_-]{11})", 
            r"live/([a-zA-Z0-9_-]{11})",
            r"video/([a-zA-Z0-9_-]{11})/livestreaming"
        ]
        for p in patterns:
            m = re.search(p, url_or_id)
            if m: return m.group(1)
        return url_or_id.strip()

    def _process_message(self, data: Any) -> Optional[str]:
        """Filter, translate and format the incoming message."""
        if isinstance(data, str):
            return data
            
        author = data.get("author", "Unknown")
        message = data.get("message", "")

        # Profanity Filter
        if self.profanity_enabled:
            msg_lower = message.lower()
            for word in self.profanity_list:
                if word in msg_lower:
                    logger.warning(f"Message from {author} blocked by profanity filter.")
                    return None

        # Length Filter
        if len(message) > 200:
            logger.warning(f"Message too long from {author}, skipped.")
            return None

        # Duplicate Filter
        msg_id = f"{author}:{message}"
        if msg_id in self.seen_messages:
            return None
        
        self.seen_messages.add(msg_id)
        if len(self.seen_messages) > self.max_seen_messages:
            self.seen_messages.clear()
            
        # Translation using Thai separator to handle mixed English-Thai text
        if self.auto_translate:
            try:
                translated = translate_mixed_text(message, self.translator)
                if translated != message:
                    logger.info(f"Translated: {message} -> {translated}")
                    message = translated
            except Exception as te:
                logger.error(f"Translation Error: {te}")
        
        return f"{author} พูดว่า {message}"

    def _save_gtts(self, text: str, path: str):
        gTTS(text=text, lang=self.gtts_language).save(path)

    def _save_gemini_tts(self, text: str, path: str):
        """Generate 24 kHz mono PCM with Gemini and wrap it in a WAV file."""
        api_key = self.gemini_api_key.strip() or os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("Gemini API key is required when Gemini Voice is selected.")

        prompt = f"{self.gemini_style.strip()}\n\n### TRANSCRIPT\n{text}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {"voiceName": self.gemini_voice}
                    }
                },
            },
        }
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.gemini_model}:generateContent"
        )
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Gemini API HTTP {error.code}: {detail[:500]}") from error

        try:
            encoded_audio = result["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            pcm_audio = base64.b64decode(encoded_audio)
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise RuntimeError("Gemini API returned no audio data.") from error

        with wave.open(path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(24000)
            wav_file.writeframes(pcm_audio)

    def _save_openai_tts(self, text: str, path: str):
        """Generate an MP3 through OpenAI's Audio Speech API."""
        api_key = self.openai_api_key.strip() or os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("OpenAI API key is required when OpenAI Voice is selected.")

        payload = {
            "model": self.openai_model,
            "voice": self.openai_voice,
            "input": text,
            "response_format": "mp3",
            "speed": max(0.25, min(float(self.openai_speed), 4.0)),
        }
        # Style instructions are supported by GPT-4o mini TTS, but not by
        # the classic tts-1 models.
        if self.openai_model.startswith("gpt-4o-mini-tts") and self.openai_instructions.strip():
            payload["instructions"] = self.openai_instructions.strip()

        request = urllib.request.Request(
            "https://api.openai.com/v1/audio/speech",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                audio = response.read()
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI API HTTP {error.code}: {detail[:500]}") from error
        if not audio:
            raise RuntimeError("OpenAI API returned no audio data.")
        with open(path, "wb") as audio_file:
            audio_file.write(audio)

    async def _generate_audio(self, text: str, path: str):
        """Generate audio using the selected provider with bounded retries."""
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                # Add a small delay between retries to avoid rate limits
                if attempt > 0:
                    await asyncio.sleep(retry_delay * attempt)
                
                if self.voice_provider == "gemini":
                    await asyncio.to_thread(self._save_gemini_tts, text, path)
                elif self.voice_provider == "openai":
                    await asyncio.to_thread(self._save_openai_tts, text, path)
                elif self.voice_provider == "gtts":
                    await asyncio.to_thread(self._save_gtts, text, path)
                else:
                    communicate = edge_tts.Communicate(text, self.voice)
                    await communicate.save(path)
                return # Success
            except Exception as e:
                logger.warning(f"{self.voice_provider} TTS attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    if self.voice_provider in ("gtts", "gemini", "openai"):
                        raise
                    logger.warning(f"All {self.voice_provider} attempts failed, using gTTS fallback.")
                    try:
                        await asyncio.to_thread(self._save_gtts, text, path)
                    except Exception as ge:
                        logger.error(f"gTTS fallback also failed: {ge}")
                        raise ge

    def _session_is_active(self, session_id: int, stop_event: threading.Event) -> bool:
        """Return True only while this exact engine session still owns the engine."""
        return (
            self.is_running
            and not stop_event.is_set()
            and session_id == self.current_session_id
        )

    async def generator_task(self, session_id: int, stop_event, msg_queue, audio_queue):
        """Main generator loop: process messages and generate audio."""
        logger.info(f"Generator started (Session: {session_id}, Voice: {self.voice})")
        while self._session_is_active(session_id, stop_event):
            try:
                try:
                    data = msg_queue.get(timeout=0.2)
                except queue.Empty:
                    continue

                processed_text = self._process_message(data)
                if not processed_text:
                    continue

                logger.info(f"Processing: {processed_text}")
                extension = ".wav" if self.voice_provider == "gemini" else ".mp3"
                path = os.path.join(self.audio_dir, f"session_{session_id}_{time.time_ns()}{extension}")
                
                try:
                    await self._generate_audio(processed_text, path)
                    # Double check session before putting to queue
                    if self._session_is_active(session_id, stop_event):
                        audio_queue.put((path, len(processed_text)), timeout=1.0)
                    else:
                        if os.path.exists(path): os.remove(path)
                except queue.Full:
                    logger.warning("Audio queue full, dropping message.")
                    if os.path.exists(path): os.remove(path)
                except Exception as ge:
                    logger.error(f"Audio Generation Error: {ge}")
                    continue

            except Exception as e:
                logger.error(f"Generator Error: {e}")
                await asyncio.sleep(1)
        logger.info(f"Generator stopped (Session: {session_id})")

    def player_loop(self, session_id: int, stop_event, audio_queue):
        """Main player loop: play generated audio files."""
        logger.info(f"Player started (Session: {session_id})")
        while self._session_is_active(session_id, stop_event):
            try:
                try:
                    path, char_count = audio_queue.get(timeout=0.2)
                except queue.Empty:
                    continue

                if os.path.exists(path):
                    try:
                        # Only one session may own pygame's process-global
                        # music channel. This also makes stop() wait until the
                        # previous player has fully released it.
                        with self._mixer_lock:
                            if not self._session_is_active(session_id, stop_event):
                                continue
                            logger.info(f"Playing: {path}")
                            mixer.music.load(path)
                            mixer.music.play()
                            while mixer.music.get_busy() and self._session_is_active(session_id, stop_event):
                                stop_event.wait(0.1)
                            mixer.music.stop()
                            mixer.music.unload()
                        
                        # Apply delay per character
                        stop_event.wait(min(char_count * self.delay_per_char, self.max_delay))
                    except Exception as e: 
                        logger.error(f"Play Error: {e}")
                    finally:
                        try:
                            if os.path.exists(path): os.remove(path)
                        except: pass
            except Exception as e: 
                logger.error(f"Player Loop Error: {e}")
        logger.info(f"Player stopped (Session: {session_id})")

    def start(self, config_dict: Dict[str, Any]):
        """Initialize and start all engine components and collectors."""
        with self._lifecycle_lock:
            if self.is_running:
                self._stop_locked()

            # Queues belong to exactly one session. A collector left waiting
            # on network I/O may wake after stop, but can then only write to
            # its retired queue, never into the new session.
            self.msg_queue = queue.Queue(maxsize=100)
            self.audio_queue = queue.Queue(maxsize=100)
            self._session_stop_event = threading.Event()
            msg_queue = self.msg_queue
            audio_queue = self.audio_queue
            stop_event = self._session_stop_event
            self.seen_messages.clear()
            self.is_running = True
            self.current_session_id += 1
            current_sid = self.current_session_id

            # Keep setup inside the lifecycle lock so Stop cannot invalidate
            # a half-built session while its worker list is being created.
            self.voice = config_dict.get("voice", "th-TH-PremwadeeNeural")
            self.voice_provider = config_dict.get("voice_provider", "edge")
            self.gtts_language = config_dict.get("gtts_language", "th")
            self.gemini_api_key = config_dict.get("gemini_api_key", "")
            self.gemini_model = config_dict.get("gemini_model", "gemini-3.1-flash-tts-preview")
            self.gemini_voice = config_dict.get("gemini_voice", "Kore")
            self.gemini_style = config_dict.get("gemini_style", "Read the transcript naturally and clearly.")
            self.openai_api_key = config_dict.get("openai_api_key", "")
            self.openai_model = config_dict.get("openai_model", "tts-1")
            self.openai_voice = config_dict.get("openai_voice", "alloy")
            self.openai_instructions = config_dict.get("openai_instructions", "Speak naturally and clearly.")
            self.openai_speed = float(config_dict.get("openai_speed", 1.0))
            self.delay_per_char = float(config_dict.get("delay_per_char", 0.03))
            self.max_delay = float(config_dict.get("max_delay", 2.0))
            self.auto_translate = str(config_dict.get("auto_translate")) == "True"
            self.profanity_enabled = str(config_dict.get("profanity_enabled")) == "True"

            logger.info(f"Starting Engine Session {current_sid}...")
            logger.info(f"Config: Voice={self.voice}, AutoTranslate={self.auto_translate}, Profanity={self.profanity_enabled}")

            try:
                self._cleanup_temp_files()
                self._load_profanity_list()
                
                # Every worker captures the immutable ID, cancellation event,
                # and queues belonging to this session.
                self.threads = [
                    threading.Thread(target=lambda: asyncio.run(self.generator_task(current_sid, stop_event, msg_queue, audio_queue)), daemon=True),
                    threading.Thread(target=lambda: self.player_loop(current_sid, stop_event, audio_queue), daemon=True)
                ]

                is_running_check = lambda: self._session_is_active(current_sid, stop_event)
                
                if str(config_dict.get("yt_enabled")) == "True" and config_dict.get("yt_id"):
                    vid = self.extract_video_id(config_dict.get("yt_id", ""))
                    self.threads.append(threading.Thread(
                        target=youtube_collector,
                        args=(vid, msg_queue, is_running_check),
                        daemon=True
                    ))
                    
                if str(config_dict.get("tw_enabled")) == "True" and config_dict.get("tw_channel"):
                    channel = config_dict.get("tw_channel", "")
                    self.threads.append(threading.Thread(
                        target=twitch_collector,
                        args=(channel, msg_queue, is_running_check),
                        daemon=True
                    ))

                if str(config_dict.get("tk_enabled")) == "True" and config_dict.get("tk_username"):
                    username = config_dict.get("tk_username", "")
                    self.threads.append(threading.Thread(
                        target=tiktok_collector,
                        args=(username, msg_queue, is_running_check),
                        daemon=True
                    ))

                for t in self.threads:
                    t.start()
                logger.info(f"Engine session {current_sid} started with {len(self.threads)-2} collectors")
            except Exception as e:
                logger.error(f"Failed to start engine: {e}\n{traceback.format_exc()}")
                self._stop_locked()

    def stop(self):
        """Stop all engine components."""
        with self._lifecycle_lock:
            self._stop_locked()

    def _stop_locked(self):
        """Stop the active session while the lifecycle lock is held."""
        old_threads = list(self.threads)
        self.is_running = False
        self._session_stop_event.set()
        # The cancellation event invalidates this session immediately. Keep
        # the numeric ID unchanged on Stop so logs count actual starts as
        # Session 1, 2, 3... instead of skipping every other number.
        self._clear_queues()
        self.seen_messages.clear()

        # Wait for any active player to observe cancellation and release
        # pygame before a subsequent start can create another player.
        with self._mixer_lock:
            try:
                mixer.music.stop()
                mixer.music.unload()
            except Exception:
                pass

        # Give cooperative workers a bounded grace period. Network libraries
        # may remain blocked, so session isolation remains the final barrier.
        deadline = time.monotonic() + 1.0
        current_thread = threading.current_thread()
        for worker in old_threads:
            if worker is current_thread or not worker.is_alive():
                continue
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            worker.join(remaining)

        lingering = sum(t.is_alive() for t in old_threads)
        self.threads = []
        self._cleanup_temp_files()
        if lingering:
            logger.warning(f"Session invalidated; {lingering} network worker(s) still shutting down in isolation.")
        logger.info("Engine session stopped and cleared.")

    def update_config(self, config_dict: Dict[str, Any]):
        """Update engine configuration in real-time."""
        try:
            if "voice" in config_dict:
                self.voice = config_dict["voice"]
            if "voice_provider" in config_dict:
                self.voice_provider = config_dict["voice_provider"]
            if "gtts_language" in config_dict:
                self.gtts_language = config_dict["gtts_language"]
            if "gemini_api_key" in config_dict:
                self.gemini_api_key = config_dict["gemini_api_key"]
            if "gemini_model" in config_dict:
                self.gemini_model = config_dict["gemini_model"]
            if "gemini_voice" in config_dict:
                self.gemini_voice = config_dict["gemini_voice"]
            if "gemini_style" in config_dict:
                self.gemini_style = config_dict["gemini_style"]
            if "openai_api_key" in config_dict:
                self.openai_api_key = config_dict["openai_api_key"]
            if "openai_model" in config_dict:
                self.openai_model = config_dict["openai_model"]
            if "openai_voice" in config_dict:
                self.openai_voice = config_dict["openai_voice"]
            if "openai_instructions" in config_dict:
                self.openai_instructions = config_dict["openai_instructions"]
            if "openai_speed" in config_dict:
                self.openai_speed = float(config_dict["openai_speed"])
            if "delay_per_char" in config_dict:
                self.delay_per_char = float(config_dict.get("delay_per_char", 0.03))
            if "max_delay" in config_dict:
                self.max_delay = float(config_dict.get("max_delay", 2.0))
            if "auto_translate" in config_dict:
                self.auto_translate = str(config_dict["auto_translate"]) == "True"
            if "profanity_enabled" in config_dict:
                self.profanity_enabled = str(config_dict["profanity_enabled"]) == "True"
                if self.profanity_enabled:
                    self._load_profanity_list()
            logger.info("Engine configuration updated in real-time.")
        except Exception as e:
            logger.error(f"Failed to update config in real-time: {e}")

