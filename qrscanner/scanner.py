import cv2
from pyzbar import pyzbar


class QRCodeScanner:
    """
    Reusable QR Code scanner using OpenCV + pyzbar.
    """

    def __init__(
        self,
        camera_index: int = 0,
        window_name: str = "QR Code Scanner (Press Q to Quit)",
        auto_exit_on_scan: bool = False,
    ):
        self.camera_index = camera_index
        self.window_name = window_name
        self.auto_exit_on_scan = auto_exit_on_scan
        self.cap = None

    # --------------------------------------------------
    # Camera Initialization
    # --------------------------------------------------
    def open_camera(self):
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            raise RuntimeError("❌ Unable to access the camera")

        print(f"📷 Camera {self.camera_index} opened successfully.")

    # --------------------------------------------------
    # QR Detection
    # --------------------------------------------------
    def detect_qr_codes(self, frame):
        return pyzbar.decode(frame)

    # --------------------------------------------------
    # Draw QR Bounding Box
    # --------------------------------------------------
    def draw_qr_overlay(self, frame, qr):
        x, y, w, h = qr.rect
        data = qr.data.decode("utf-8")
        qr_type = qr.type

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        label = f"{qr_type}: {data}"
        cv2.putText(
            frame,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

        return data

    # --------------------------------------------------
    # Main Loop
    # --------------------------------------------------
    def start(self):
        self.open_camera()
        print("🔍 Scanning for QR codes...")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("⚠️ Failed to read camera frame.")
                break

            qr_codes = self.detect_qr_codes(frame)

            for qr in qr_codes:
                data = self.draw_qr_overlay(frame, qr)
                print(f"✅ QR Detected: {data}")

                if self.auto_exit_on_scan:
                    self.cleanup()
                    return data

            cv2.imshow(self.window_name, frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.cleanup()

    # --------------------------------------------------
    # Cleanup
    # --------------------------------------------------
    def cleanup(self):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("🛑 Camera released. Scanner stopped.")


# ------------------------------------------------------
# USAGE
# ------------------------------------------------------
if __name__ == "__main__":
    # Try 1 or 2 if back camera is not detected
    scanner = QRCodeScanner(
        camera_index=0,
        auto_exit_on_scan=False  # Set True to stop after first QR
    )
    scanner.start()
