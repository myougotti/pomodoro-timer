"""Run this once to generate icon and alarm assets. Requires Pillow."""
import os
import struct
import wave
import math
from PIL import Image, ImageDraw

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def create_icon():
    """Create a tomato-style pomodoro icon."""
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Tomato body
    draw.ellipse([30, 50, size - 30, size - 20], fill="#e74c3c", outline="#c0392b", width=3)

    # Highlight
    draw.ellipse([70, 80, 140, 130], fill="#ec7063")

    # Stem
    draw.rectangle([118, 20, 138, 60], fill="#27ae60")

    # Leaf
    draw.ellipse([138, 25, 185, 55], fill="#2ecc71")

    # Save PNG for tray
    png_path = os.path.join(ASSETS_DIR, "icon.png")
    img_64 = img.resize((64, 64), Image.LANCZOS)
    img_64.save(png_path)

    # Save ICO for window
    ico_path = os.path.join(ASSETS_DIR, "icon.ico")
    img.save(ico_path, format="ICO", sizes=[(256, 256), (64, 64), (48, 48), (32, 32), (16, 16)])

    print(f"Created: {png_path}")
    print(f"Created: {ico_path}")


def create_alarm_sound():
    """Create a simple chime alarm .wav file."""
    sample_rate = 44100
    duration = 1.5  # seconds
    num_samples = int(sample_rate * duration)

    samples = []
    # Three ascending tones
    freqs = [(523, 0.0, 0.4), (659, 0.4, 0.8), (784, 0.8, 1.3)]
    for freq, start, end in freqs:
        start_sample = int(start * sample_rate)
        end_sample = int(end * sample_rate)
        for i in range(num_samples):
            if start_sample <= i < end_sample:
                t = (i - start_sample) / sample_rate
                envelope = min(1.0, (end - start - t) * 5) * min(1.0, t * 20)
                value = envelope * 0.4 * math.sin(2 * math.pi * freq * t)
            else:
                value = 0
            if i < len(samples):
                samples[i] += value
            else:
                samples.append(value)

    # Normalize and convert to 16-bit
    max_val = max(abs(s) for s in samples) or 1
    raw = b"".join(struct.pack("<h", int(s / max_val * 32000)) for s in samples)

    wav_path = os.path.join(ASSETS_DIR, "alarm.wav")
    with wave.open(wav_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(raw)

    print(f"Created: {wav_path}")


if __name__ == "__main__":
    create_icon()
    create_alarm_sound()
    print("Assets generated successfully!")
