import cv2
import csv
import time
from datetime import datetime
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode

CSV_FILE = "scan_results.csv"
DUPLICATE_WINDOW = 2


class ScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR & Barcode Scanner")
        self.root.resizable(False, False)

        self.cap = None
        self.running = False
        self.scan_count = 0
        self.last_scan_times = {}

        self._build_ui()
        self._init_csv()

    def _build_ui(self):
        # Camera feed panel
        self.camera_label = Label(self.root, bg='black', width=640, height=480)
        self.camera_label.grid(row=0, column=0, padx=10, pady=10)

        # Right panel — scan history
        right_frame = Frame(self.root)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky='ns')

        Label(right_frame, text="Scan History", font=('Arial', 12, 'bold')).pack(anchor='w')

        self.history_list = Listbox(right_frame, width=32, height=22, font=('Courier', 9))
        scrollbar = Scrollbar(right_frame, orient=VERTICAL, command=self.history_list.yview)
        self.history_list.config(yscrollcommand=scrollbar.set)
        self.history_list.pack(side=LEFT, fill=BOTH)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Bottom controls
        bottom_frame = Frame(self.root)
        bottom_frame.grid(row=1, column=0, columnspan=2, pady=8)

        self.start_btn = Button(
            bottom_frame, text="Start Camera", width=14,
            bg='green', fg='white', font=('Arial', 10, 'bold'),
            command=self.toggle_camera
        )
        self.start_btn.pack(side=LEFT, padx=6)

        Button(
            bottom_frame, text="Scan Image File", width=14,
            command=self.scan_image
        ).pack(side=LEFT, padx=6)

        self.count_label = Label(bottom_frame, text="Scanned: 0", font=('Arial', 10))
        self.count_label.pack(side=LEFT, padx=20)

        Button(
            bottom_frame, text="Clear History", width=12,
            command=self.clear_history
        ).pack(side=LEFT, padx=6)

    def _init_csv(self):
        with open(CSV_FILE, 'w', newline='') as f:
            csv.writer(f).writerow(['Timestamp', 'Type', 'Data'])

    def toggle_camera(self):
        if self.running:
            self.running = False
            self.start_btn.config(text="Start Camera", bg='green')
            if self.cap:
                self.cap.release()
                self.cap = None
        else:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Could not open webcam.")
                return
            self.running = True
            self.start_btn.config(text="Stop Camera", bg='red')
            self._update_frame()

    def _update_frame(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if ret:
            now = time.time()

            for code in decode(frame):
                code_data = code.data.decode('utf-8')
                code_type = code.type
                color = (0, 255, 0) if code_type == 'QRCODE' else (255, 0, 0)

                x, y, w, h = code.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
                cv2.putText(frame, f"{code_type}: {code_data[:20]}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                if now - self.last_scan_times.get(code_data, 0) >= DUPLICATE_WINDOW:
                    self.last_scan_times[code_data] = now
                    self._log_scan(code_type, code_data)

            cv2.putText(frame, f"Scanned: {self.scan_count}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            self._show_frame(frame)

        self.root.after(10, self._update_frame)

    def scan_image(self):
        path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not path:
            return

        frame = cv2.imread(path)
        if frame is None:
            messagebox.showerror("Error", "Could not load image.")
            return

        detected_codes = decode(frame)
        if not detected_codes:
            messagebox.showinfo("Result", "No codes detected in this image.")
        else:
            for code in detected_codes:
                code_data = code.data.decode('utf-8')
                code_type = code.type
                color = (0, 255, 0) if code_type == 'QRCODE' else (255, 0, 0)

                x, y, w, h = code.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
                cv2.putText(frame, f"{code_type}: {code_data[:20]}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                self._log_scan(code_type, code_data)

        self._show_frame(frame)

    def _show_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = img.resize((640, 480))
        photo = ImageTk.PhotoImage(img)
        self.camera_label.config(image=photo)
        self.camera_label.image = photo

    def _log_scan(self, code_type, code_data):
        self.scan_count += 1
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.history_list.insert(0, f"[{code_type}]  {code_data[:28]}")
        self.count_label.config(text=f"Scanned: {self.scan_count}")

        with open(CSV_FILE, 'a', newline='') as f:
            csv.writer(f).writerow([timestamp, code_type, code_data])

        print(f"[{timestamp}] [{code_type}]: {code_data}")

    def clear_history(self):
        self.history_list.delete(0, END)
        self.scan_count = 0
        self.count_label.config(text="Scanned: 0")
        self.last_scan_times.clear()
        self._init_csv()


if __name__ == "__main__":
    root = Tk()
    app = ScannerApp(root)
    root.mainloop()
