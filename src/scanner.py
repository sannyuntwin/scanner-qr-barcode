import cv2
import csv
import sys
import time
from datetime import datetime
from pyzbar.pyzbar import decode

DUPLICATE_WINDOW = 2  # seconds before same code can be re-scanned
CSV_FILE = "scan_results.csv"

with open(CSV_FILE, 'w', newline='') as f:
    csv.writer(f).writerow(['Timestamp', 'Type', 'Data'])


def draw_and_log(frame, code, log=True):
    code_data = code.data.decode('utf-8')
    code_type = code.type
    color = (0, 255, 0) if code_type == 'QRCODE' else (255, 0, 0)

    x, y, w, h = code.rect
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
    cv2.putText(frame, f"{code_type}: {code_data[:20]}", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    if log:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Detected [{code_type}]: {code_data}")
        with open(CSV_FILE, 'a', newline='') as f:
            csv.writer(f).writerow([timestamp, code_type, code_data])

    return code_data


# --- Image file mode ---
if len(sys.argv) > 1:
    image_path = sys.argv[1]
    frame = cv2.imread(image_path)

    if frame is None:
        print(f"Error: Could not load image '{image_path}'")
        sys.exit(1)

    detected_codes = decode(frame)

    if not detected_codes:
        print("No codes detected in image.")
    else:
        for code in detected_codes:
            draw_and_log(frame, code)

    cv2.imshow('Code Scanner - Image', frame)
    print("Press any key to close.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    sys.exit(0)


# --- Webcam mode ---
video_capture = cv2.VideoCapture(0)
last_scan_times = {}
scan_count = 0

print("Barcode & QR Code Scanner Started.")
print("Hold a code up to the camera. Press 'q' to quit.")
print(f"Results saved to: {CSV_FILE}")

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to grab frame. Exiting...")
        break

    detected_codes = decode(frame)
    now = time.time()

    for code in detected_codes:
        code_data = code.data.decode('utf-8')
        should_log = now - last_scan_times.get(code_data, 0) >= DUPLICATE_WINDOW

        draw_and_log(frame, code, log=should_log)

        if should_log:
            scan_count += 1
            last_scan_times[code_data] = now

    cv2.putText(frame, f"Scanned: {scan_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow('Code Scanner', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
print(f"\nSession complete. Total scans: {scan_count}. Results saved to {CSV_FILE}")
