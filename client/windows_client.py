import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from typing import Optional

import keyboard
import numpy as np
import pyperclip
import requests
import sounddevice as sd
import soundfile as sf


DEFAULT_CONFIG = {
    "server_url": "http://127.0.0.1:8000",
    "api_key": "dev_key_123",
    "hotkey": "ctrl+shift+r",
    "auto_paste": True,
    "language": "en",
    "provider": None,
}


@dataclass
class ClientConfig:
    server_url: str
    api_key: Optional[str]
    hotkey: str
    auto_paste: bool
    language: Optional[str]
    provider: Optional[str]

    @staticmethod
    def load(path: str) -> "ClientConfig":
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(DEFAULT_CONFIG, fh, indent=2)
            print(f"Wrote default config to {path}. Edit it with your server URL and API key.")
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return ClientConfig(
            server_url=data.get("server_url", DEFAULT_CONFIG["server_url"]),
            api_key=data.get("api_key"),
            hotkey=data.get("hotkey", DEFAULT_CONFIG["hotkey"]),
            auto_paste=bool(data.get("auto_paste", DEFAULT_CONFIG["auto_paste"])),
            language=data.get("language"),
            provider=data.get("provider"),
        )


class Recorder:
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.frames: list[np.ndarray] = []
        self.stream: Optional[sd.InputStream] = None
        self.is_recording: bool = False

    def _callback(self, indata, frames, time_info, status):  # noqa: ANN001, ARG002
        if status:
            # Non-fatal warnings from PortAudio
            print(f"Audio status: {status}")
        self.frames.append(indata.copy())

    def start(self):
        if self.is_recording:
            return
        self.frames = []
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            callback=self._callback,
        )
        self.stream.start()
        self.is_recording = True
        print("Recording started...")

    def stop(self) -> str:
        if not self.is_recording:
            return ""
        assert self.stream is not None
        self.stream.stop()
        self.stream.close()
        self.stream = None
        self.is_recording = False
        print("Recording stopped.")

        if not self.frames:
            return ""

        audio = np.concatenate(self.frames, axis=0)
        tmp_path = tempfile.mktemp(prefix="dictation_", suffix=".wav")
        sf.write(tmp_path, audio, self.sample_rate, subtype="PCM_16")
        return tmp_path


def send_audio(server_url: str, api_key: Optional[str], wav_path: str, language: Optional[str], provider: Optional[str]) -> str:
    url = server_url.rstrip("/") + "/v1/transcribe"
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    data = {}
    if language:
        data["language"] = language
    if provider:
        data["provider"] = provider
    with open(wav_path, "rb") as fh:
        files = {"file": (os.path.basename(wav_path), fh, "audio/wav")}
        resp = requests.post(url, headers=headers, data=data, files=files, timeout=120)
    resp.raise_for_status()
    payload = resp.json()
    return str(payload.get("text", "")).strip()


def main():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    cfg = ClientConfig.load(config_path)

    recorder = Recorder()

    def toggle_recording():
        try:
            if not recorder.is_recording:
                recorder.start()
            else:
                wav_path = recorder.stop()
                if not wav_path:
                    print("No audio captured.")
                    return
                try:
                    text = send_audio(cfg.server_url, cfg.api_key, wav_path, cfg.language, cfg.provider)
                finally:
                    try:
                        os.remove(wav_path)
                    except OSError:
                        pass
                if text:
                    print(f"Transcription: {text}")
                    pyperclip.copy(text)
                    if cfg.auto_paste:
                        # Small delay to ensure clipboard is populated
                        time.sleep(0.05)
                        keyboard.send("ctrl+v")
                else:
                    print("Empty transcription result.")
        except Exception as exc:  # noqa: BLE001
            print(f"Error: {exc}")

    print("Orthopedic Dictation Client")
    print(f"Hotkey: {cfg.hotkey} (press to start/stop recording)")
    print("Press Ctrl+C to exit.")

    keyboard.add_hotkey(cfg.hotkey, toggle_recording)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        if recorder.is_recording:
            recorder.stop()
        print("Exiting.")


if __name__ == "__main__":
    if sys.platform != "win32":
        print("Warning: This client is intended for Windows 10/11.")
    main()

