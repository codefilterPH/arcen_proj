let html5QrCode = null;
window.scannedUserData = {};
window.scannedUserId = null;

// ------------------------------
// 🚀 START SCANNER
// ------------------------------
function initQrScanner() {
    console.log("▶ Starting QR Scanner…");

    if (html5QrCode) return;

    html5QrCode = new Html5Qrcode("reader");

    html5QrCode.start(
        // ✔ FIRST ARGUMENT: only ONE key allowed
        { facingMode: "environment" },

        // ✔ SECOND ARGUMENT: all scanner settings here
        {
            fps: 15,
            qrbox: { width: 300, height: 300 },
            aspectRatio: 1.0,

            // 🔥 Autofocus + Autoexposure + Autozoom (valid here)
            experimentalFeatures: {
                useBarCodeDetectorIfSupported: true,
                autoZoom: true
            },

            videoConstraints: {
                focusMode: "continuous",
                exposureMode: "continuous"
            }
        },

        // SUCCESS CALLBACK
        (decodedText) => {
            console.log("✅ QR FOUND:", decodedText);
            handleDecodedQR(decodedText);
        },

        // ERROR CALLBACK
        (err) => {
            // silent scan errors
        }

    ).catch(err => {
        console.error("❌ Failed to start camera:", err);
    });
}



// ------------------------------
// 🔍 HANDLE DECODED QR
// ------------------------------
function handleDecodedQR(decodedText) {
    let data = null;

    try {
        data = JSON.parse(decodedText);
    } catch (e) {
        document.getElementById("result").innerText = "❌ Invalid QR Format!";
        return;
    }

    window.scannedUserData = data;
    window.scannedUserId = data.user_id;

    // Update UI
    document.getElementById("result").innerText = `✅ Scanned: ${data.name}`;
    document.getElementById("studentName").innerText = data.name || "—";
    document.getElementById("studentRank").innerText = data.rank || "—";
    document.getElementById("studentClass").innerText = data.classification || "—";
    document.getElementById("studentContact").innerText = data.contact_number || "—";

    document.getElementById("studentAddress").innerText =
        [data.address, data.city, data.province].filter(Boolean).join(", ") || "—";


    if (data.profile_picture) {
        document.getElementById("studentPhoto").src = data.profile_picture;
    }

    document.getElementById("studentCard").style.display = "block";

    stopQrScanner();
}



// ------------------------------
// 🛑 STOP SCANNER
// ------------------------------
function stopQrScanner() {
    if (html5QrCode) {
        html5QrCode.stop()
            .then(() => {
                html5QrCode.clear();
                html5QrCode = null;
            })
            .catch(err => console.error("⚠️ Could not stop scanner:", err));
    }
}


// ------------------------------
// ❌ CANCEL
// ------------------------------
function cancelAttendance() {
    alert("❌ Attendance Cancelled.");
    document.getElementById("studentCard").style.display = "none";
}



// MAKE FUNCTIONS PUBLIC
window.initQrScanner = initQrScanner;
window.stopQrScanner = stopQrScanner;
window.confirmAttendance = confirmAttendance;
window.cancelAttendance = cancelAttendance;
