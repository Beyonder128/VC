# AudioShare — Multi-Earphone Wi-Fi Audio Streamer

Stream music or microphone audio from one device to 2+ earphones
simultaneously over your local Wi-Fi network.

---

## How It Works

```
[Phone/PC running server.py]
        |
        |  Wi-Fi (same network)
        |
   ┌────┴─────┐
   ▼          ▼
[Device 1]  [Device 2]
(Browser)   (Browser)
🎧 Earphone  🎧 Earphone
```

The server streams audio over HTTP. Each listener device opens the web
dashboard in a browser and taps "Start Listening" — no app install needed.

---

## Setup

### Option A — PC / Laptop (easiest)

1. Install Python 3.8+
2. Install dependencies:
   ```
   pip install flask pyaudio
   ```
3. Put `server.py` and `client.html` in the same folder
4. Run:
   ```
   python server.py
   ```
5. Note the IP shown (e.g. `http://192.168.1.5:5000`)

### Option B — Android via Termux

1. Install [Termux](https://f-droid.org/packages/com.termux/) from F-Droid
2. Open Termux and run:
   ```
   pkg update && pkg upgrade
   pkg install python portaudio
   pip install flask pyaudio
   ```
3. Copy `server.py` and `client.html` to Termux home:
   ```
   cp /sdcard/Download/server.py ~/
   cp /sdcard/Download/client.html ~/
   ```
4. Run:
   ```
   python server.py
   ```
5. Note the IP address shown in the output

> **Note**: On Android, microphone access in Termux may need
> `termux-microphone-record` or the Termux:API add-on.

---

## Usage

### Broadcaster (the device with the music)

1. Open `http://<server-ip>:5000` in a browser
2. Choose **FILE** or **MIC** mode
3. **FILE mode**: Enter the full path to an MP3 or WAV file and press PLAY
4. **MIC mode**: Press START MIC BROADCAST to stream live microphone input
5. Press STOP BROADCAST to end the stream

### Listeners (earphone devices)

1. Connect each device to the **same Wi-Fi network** as the server
2. Open `http://<server-ip>:5000` in the browser
3. Plug in / connect your earphones
4. Scroll down to **Listener Mode** and tap **START LISTENING**
5. Adjust the local volume slider as needed

---

## File Paths

Common paths by platform:

| Platform | Example Path |
|---|---|
| Android (Termux) | `/sdcard/Music/song.mp3` |
| macOS | `/Users/yourname/Music/song.wav` |
| Windows | `C:/Users/yourname/Music/song.mp3` |
| Linux | `/home/yourname/Music/song.wav` |

---

## Supported Formats

| Format | Supported |
|---|---|
| MP3 | ✅ (streamed as raw bytes) |
| WAV | ✅ (native) |
| AAC / M4A | ✅ (streamed as raw bytes, browser decodes) |
| FLAC | ⚠️ (browser support varies) |
| Microphone | ✅ (pyaudio required) |

---

## Troubleshooting

**"Server unreachable" in browser**
- Make sure all devices are on the same Wi-Fi network
- Check that port 5000 isn't blocked by a firewall
- Try `http://127.0.0.1:5000` on the server device itself

**Mic streaming not working**
- Run `pip install pyaudio` (or `pkg install portaudio && pip install pyaudio` in Termux)
- On Android, grant Termux microphone permission in Android Settings

**Audio choppy / lagging**
- Move closer to the Wi-Fi router
- Use a 5GHz Wi-Fi network if available
- Reduce the number of simultaneous listeners

**File not found error**
- Double-check the full file path
- On Android, ensure Termux has storage permission:
  `termux-setup-storage`

---

## Extending to More Listeners

The current setup supports unlimited listeners — just open the URL on
more devices. The `clients` list in `server.py` grows automatically.
You can also add password protection by adding Flask-Login or a simple
token check to the `/audio-stream` route.
