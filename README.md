# QR & Barcode Scanner

A real-time QR code and barcode scanner built with Python and OpenCV. Supports live webcam scanning, image file scanning, a GUI interface, and automatic CSV logging.

---

## Features

- **Live webcam scanning** — detects QR codes and barcodes in real time
- **Image file scanning** — scan from any `.jpg`, `.png`, or `.bmp` file
- **Color-coded detection** — green box for QR codes, blue box for barcodes
- **Duplicate prevention** — same code won't re-log within 2 seconds
- **CSV logging** — every scan saved with timestamp, type, and value
- **GUI interface** — tkinter window with scan history, start/stop, and file picker
- **Terminal/CLI mode** — lightweight version for quick use

---

## Demo

### GUI Mode
> Start the camera, hold a code up to the webcam — detected codes appear in the history panel with a color-coded box drawn around them.

### Terminal Mode
```
Barcode & QR Code Scanner Started.
Hold a code up to the camera. Press 'q' to quit.
[2024-01-15 10:23:01] Detected [CODE128]: php476089
[2024-01-15 10:23:04] Detected [QRCODE]: https://example.com
```

---

## Tech Stack

| Library | Purpose |
|---|---|
| `opencv-python` | Camera capture, image processing, drawing overlays |
| `pyzbar` | Barcode and QR code decoding (ZBar engine) |
| `Pillow` | Converting OpenCV frames for tkinter display |
| `tkinter` | GUI framework (built into Python) |

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/sannyuntwin/qr-barcode-scanner.git
cd qr-barcode-scanner
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

> **Windows note:** `pyzbar` requires the ZBar DLL. If you get an import error, run:
> ```bash
> pip install pyzbar[scripts]
> ```

---

## Usage

### GUI Mode
```bash
python src/gui.py
```

### Terminal Mode — Webcam
```bash
python src/scanner.py
```

### Terminal Mode — Image File
```bash
python src/scanner.py path/to/image.jpg
```

---

## Output

Each session creates a `scan_results.csv` file:

```
Timestamp,Type,Data
2024-01-15 10:23:01,CODE128,php476089
2024-01-15 10:23:04,QRCODE,https://example.com
```

---

## Project Structure

```
qr-barcode-scanner/
├── src/
│   ├── scanner.py      # Terminal/CLI scanner
│   └── gui.py          # GUI scanner
├── requirements.txt
└── README.md
```

---

## How It Works

```
[ Webcam / Image ] → [ OpenCV Frame ] → [ pyzbar Decode ] → [ Draw Overlay ] → [ Log to CSV ]
```

1. **Capture** — OpenCV reads frames from the webcam or loads an image file
2. **Decode** — pyzbar scans each frame for known barcode/QR patterns
3. **Overlay** — bounding box and label drawn directly on the frame
4. **Log** — decoded value saved to CSV with timestamp

---

## Supported Code Types

- QR Code
- CODE128, CODE39, CODE93
- EAN-13, EAN-8, UPC-A
- PDF417, DataMatrix, and more (via ZBar)
# scanner-qr-barcode
