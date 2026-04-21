"""
AudioShare Server
-----------------
Run this on any Python-capable device (PC, Android via Termux, etc.)
on the same Wi-Fi network as your listener devices.

Requirements:
    pip install flask pyaudio

For Android (Termux):
    pkg install python portaudio
    pip install flask pyaudio

Usage:
    python server.py

Then open http://<your-device-ip>:5000 in a browser on each listener device.
"""

import os
import io
import wave
import threading
import time
import struct
import json
from flask import Flask, Response, render_template_string, request, jsonify

# ── Try to import pyaudio (optional – needed only for mic/system capture) ──
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("[WARN] pyaudio not found – microphone/system audio capture disabled.")
    print("       File streaming still works.")

app = Flask(__name__)

# ── Global state ──────────────────────────────────────────────────────────────
import queue

clients: list[queue.Queue] = []       # SSE listener queues
clients_lock = threading.Lock()

stream_state = {
    "mode": "idle",          # "idle" | "file" | "mic"
    "filename": "",
    "playing": False,
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def broadcast_chunk(chunk: bytes):
    """Push an audio chunk to every connected SSE client."""
    dead = []
    with clients_lock:
        for q in clients:
            try:
                q.put_nowait(chunk)
            except queue.Full:
                dead.append(q)
        for q in dead:
            clients.remove(q)
            print(f"[WARNING] Removed client (queue full)")


def stream_wav_file(filepath: str):
    """Read a WAV file and broadcast it chunk-by-chunk."""
    stream_state["playing"] = True
    stream_state["mode"] = "file"
    stream_state["filename"] = os.path.basename(filepath)
    print(f"[INFO] Starting WAV stream: {filepath}")
    CHUNK = 4096
    try:
        with wave.open(filepath, "rb") as wf:
            data = wf.readframes(CHUNK)
            frame_count = 0
            while data and stream_state["playing"]:
                broadcast_chunk(data)
                frame_count += 1
                data = wf.readframes(CHUNK)
                time.sleep(0.01)
            print(f"[INFO] WAV stream complete: {frame_count} frames sent")
    except Exception as e:
        print(f"[ERROR] WAV stream: {e}")
        import traceback
        traceback.print_exc()
    finally:
        stream_state["playing"] = False
        stream_state["mode"] = "idle"
        stream_state["filename"] = ""
        broadcast_chunk(b"")
        print(f"[INFO] WAV stream ended")


def stream_mp3_file(filepath: str):
    """Read any binary audio file (MP3 etc.) and broadcast raw bytes."""
    stream_state["playing"] = True
    stream_state["mode"] = "file"
    stream_state["filename"] = os.path.basename(filepath)
    print(f"[INFO] Starting MP3 stream: {filepath}")
    CHUNK = 8192
    try:
        with open(filepath, "rb") as f:
            data = f.read(CHUNK)
            chunk_count = 0
            while data and stream_state["playing"]:
                broadcast_chunk(data)
                chunk_count += 1
                data = f.read(CHUNK)
                time.sleep(0.01)  # Reduced sleep for better streaming
            print(f"[INFO] MP3 stream complete: {chunk_count} chunks sent")
    except Exception as e:
        print(f"[ERROR] File stream: {e}")
        import traceback
        traceback.print_exc()
    finally:
        stream_state["playing"] = False
        stream_state["mode"] = "idle"
        stream_state["filename"] = ""
        broadcast_chunk(b"")
        print(f"[INFO] File stream ended")


def stream_microphone():
    """Capture microphone input and broadcast PCM audio (WAV-wrapped)."""
    if not PYAUDIO_AVAILABLE:
        print("[ERROR] pyaudio required for mic streaming.")
        return

    assert pyaudio is not None
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024

    pa = pyaudio.PyAudio()
    stream_state["playing"] = True
    stream_state["mode"] = "mic"
    stream_state["filename"] = "Microphone"
    mic = None

    try:
        mic = pa.open(format=FORMAT, channels=CHANNELS,
                      rate=RATE, input=True, frames_per_buffer=CHUNK)
        print("[INFO] Mic streaming started")
        while stream_state["playing"] and stream_state["mode"] == "mic":
            pcm = mic.read(CHUNK, exception_on_overflow=False)
            # Wrap raw PCM in a tiny WAV header so browsers can decode it
            buf = io.BytesIO()
            with wave.open(buf, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(pa.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(pcm)
            broadcast_chunk(buf.getvalue())
    except Exception as e:
        print(f"[ERROR] Mic stream: {e}")
    finally:
        if mic is not None:
            try:
                mic.stop_stream(); mic.close()
            except Exception:
                pass
        pa.terminate()
        stream_state["playing"] = False
        stream_state["mode"] = "idle"
        stream_state["filename"] = ""
        broadcast_chunk(b"")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the control dashboard."""
    try:
        with open("client.html", "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"[ERROR] Failed to load client.html: {e}")
        import traceback
        traceback.print_exc()
        return f"Error loading page: {e}", 500


@app.route("/audio-stream")
def audio_stream():
    """Stream audio to listener devices."""
    client_queue: queue.Queue = queue.Queue(maxsize=100)
    with clients_lock:
        clients.append(client_queue)
    print(f"[+] Client connected  ({len(clients)} total)")

    def generate():
        stream_ended = False
        try:
            while not stream_ended:
                try:
                    chunk = client_queue.get(timeout=60)
                    if chunk == b"":
                        print(f"[INFO] Stream ended signal received for client")
                        # Send termination signal multiple times to ensure client receives it
                        yield b""
                        stream_ended = True
                        break
                    if chunk:
                        yield chunk
                except queue.Empty:
                    # Keep connection alive with silence
                    pass
        except GeneratorExit:
            print(f"[INFO] Client generator exited")
        finally:
            with clients_lock:
                if client_queue in clients:
                    clients.remove(client_queue)
            print(f"[-] Client disconnected ({len(clients)} total)")

    return Response(generate(),
                    mimetype="application/octet-stream",
                    headers={"Cache-Control": "no-cache",
                             "X-Accel-Buffering": "no",
                             "Content-Type": "application/octet-stream"})


@app.route("/status")
def status():
    status_data = {**stream_state, "clients": len(clients)}
    if stream_state["playing"]:
        print(f"[STATUS] Mode: {status_data['mode']}, Playing: True, Clients: {status_data['clients']}")
    return jsonify(status_data)


@app.route("/play-file", methods=["POST"])
def play_file():
    if stream_state["playing"]:
        print("[INFO] Stopping current playback before starting new one")
        stream_state["playing"] = False
        time.sleep(0.3)

    data = request.get_json()
    path = data.get("path", "").strip()

    if not path or not os.path.isfile(path):
        error_msg = f"File not found: {path}"
        print(f"[ERROR] {error_msg}")
        return jsonify({"error": error_msg}), 400

    basename = os.path.basename(path)
    ext = os.path.splitext(path)[1].lower()
    fn = stream_wav_file if ext == ".wav" else stream_mp3_file
    print(f"[INFO] Queuing playback: {basename} (format: {ext})")
    threading.Thread(target=fn, args=(path,), daemon=True).start()
    return jsonify({"ok": True, "file": basename})


@app.route("/play-mic", methods=["POST"])
def play_mic():
    if not PYAUDIO_AVAILABLE:
        return jsonify({"error": "pyaudio not installed"}), 500
    if stream_state["playing"]:
        stream_state["playing"] = False
        time.sleep(0.3)
    threading.Thread(target=stream_microphone, daemon=True).start()
    return jsonify({"ok": True})


@app.route("/stop", methods=["POST"])
def stop():
    stream_state["playing"] = False
    return jsonify({"ok": True})


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import socket
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "127.0.0.1"

    print("=" * 52)
    print("  AudioShare Server")
    print("=" * 52)
    print(f"  Dashboard  : http://{local_ip}:5001")
    print(f"  Share this URL with listener devices on the same Wi-Fi")
    print("  Press Ctrl+C to stop")
    print("=" * 52)

    app.run(host="0.0.0.0", port=5001, threaded=True, debug=True, use_reloader=False)
