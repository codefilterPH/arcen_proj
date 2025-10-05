let html5QrCode = null;   // will hold the scanner instance

// Start the QR scanner only when modal is visible
function initQrScanner() {
  console.log("▶ Starting QR Scanner…");

  // Avoid re-creating if already active
  if (html5QrCode) return;

  html5QrCode = new Html5Qrcode("reader");

  html5QrCode.start(
    { facingMode: "environment" },       // use back camera on mobile
    { fps: 10, qrbox: 250 },              // scanner settings
    (decodedText) => {                    // success callback
      console.log("✅ Scanned:", decodedText);

      // Show result in UI
      document.getElementById("result").innerText = "✅ Scanned Result: " + decodedText;
      document.getElementById("studentId").innerText = decodedText;
      document.getElementById("studentName").innerText = "Juan Dela Cruz";
      document.getElementById("studentClass").innerText = "Grade 10 - Section A";
      document.getElementById("studentCard").style.display = "block";

      // Auto-stop after a successful scan
      stopQrScanner();
    },
    (error) => {
      // console.log("Scan error:", error);
    }
  ).catch(err => console.error("❌ Failed to start camera:", err));
}

// Stop the QR scanner when modal closes
function stopQrScanner() {
  if (html5QrCode) {
    html5QrCode.stop()
      .then(() => {
        html5QrCode.clear();
        html5QrCode = null;
        console.log("🛑 Scanner stopped.");
      })
      .catch(err => console.error("⚠️ Failed to stop scanner:", err));
  }
}

// Demo buttons
function confirmAttendance() {
  alert("✅ Attendance Confirmed!");
}
function cancelAttendance() {
  alert("❌ Attendance Cancelled.");
  document.getElementById("studentCard").style.display = "none";
}

// Expose to global scope
window.initQrScanner = initQrScanner;
window.stopQrScanner = stopQrScanner;
