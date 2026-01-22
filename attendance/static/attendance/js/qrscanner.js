/* ============================================================
 * QR SCANNER MODULE (Mobile-Safe, Toggle Enabled)
 * Uses html5-qrcode
 * ============================================================ */

let html5QrCode = null;
let currentFacingMode = "environment"; // environment = back, user = front
let isScannerRunning = false;

// Exposed scanned data
window.scannedUserData = {};
window.scannedUserId = null;

/* ============================================================
 * INIT SCANNER (permission + instance only)
 * ============================================================ */
async function initQrScanner() {
    if (html5QrCode) {
        console.warn("[QR] Scanner already initialized");
        return;
    }

    try {
        console.log("[QR] Requesting camera permission (environment preferred)");

        // IMPORTANT: first getUserMedia decides camera on mobile
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: { ideal: "environment" } }
        });

        // Stop immediately – permission is enough
        stream.getTracks().forEach(track => track.stop());

        html5QrCode = new Html5Qrcode("reader");

        document.getElementById("result").innerText =
            "Camera ready. Start scanning or switch camera.";

        console.log("[QR] Scanner initialized successfully");

    } catch (err) {
        console.error("[QR] Camera permission failed:", err);
    }
}

/* ============================================================
 * START SCANNER (uses currentFacingMode)
 * ============================================================ */
async function startScanner() {
    if (!html5QrCode) {
        console.warn("[QR] startScanner called before init");
        return;
    }

    if (isScannerRunning) {
        console.warn("[QR] Scanner already running");
        return;
    }

    console.log(`[QR] Starting scanner (facingMode=${currentFacingMode})`);

    try {
        await html5QrCode.start(
            { facingMode: currentFacingMode },
            {
                fps: 15,
                qrbox: { width: 300, height: 300 },
                aspectRatio: 1.0,
                experimentalFeatures: {
                    useBarCodeDetectorIfSupported: true
                }
            },
            onScanSuccess,
            () => {} // ignore scan failures
        );

        isScannerRunning = true;
        console.log("[QR] Scanner started");

    } catch (err) {
        console.error("[QR] Failed to start scanner:", err);
    }
}

/* ============================================================
 * TOGGLE CAMERA (Front <-> Back)
 * ============================================================ */
async function toggleCamera() {
    if (!html5QrCode) {
        console.warn("[QR] toggleCamera called before init");
        return;
    }

    currentFacingMode =
        currentFacingMode === "environment" ? "user" : "environment";

    console.log(`[QR] Switching camera → ${currentFacingMode}`);

    try {
        if (isScannerRunning) {
            await html5QrCode.stop();
            isScannerRunning = false;
            console.log("[QR] Scanner stopped for camera switch");
        }

        await startScanner();

    } catch (err) {
        console.error("[QR] Failed to toggle camera:", err);
    }
}

/* ============================================================
 * SCAN SUCCESS CALLBACK
 * ============================================================ */
function onScanSuccess(decodedText) {
    console.log("[QR] Raw decoded text:", decodedText);

    let data;
    try {
        data = JSON.parse(decodedText);
    } catch (err) {
        console.error("[QR] Invalid QR JSON format", err);
        document.getElementById("result").innerText = "Invalid QR format";
        return;
    }

    console.log("[QR] Parsed QR payload:", data);

    // Validate required fields (matches UserProfile.generate_qr_code)
    const requiredFields = ["user_id", "name", "rank", "classification"];

    for (const field of requiredFields) {
        if (!(field in data)) {
            console.error(`[QR] Missing required field: ${field}`);
            document.getElementById("result").innerText =
                "QR code missing required data";
            return;
        }
    }

    window.scannedUserData = data;
    window.scannedUserId = data.user_id;

    console.log("[QR] User ID:", data.user_id);
    console.log("[QR] Name:", data.name);
    console.log("[QR] Rank:", data.rank);
    console.log("[QR] Classification:", data.classification);

    handleDecodedQR(data);
}

/* ============================================================
 * HANDLE DECODED QR (UI POPULATION)
 * ============================================================ */
function handleDecodedQR(data) {
    document.getElementById("result").innerText =
        `Scanned: ${data.name}`;

    document.getElementById("studentName").innerText =
        data.name || "—";
    document.getElementById("studentRank").innerText =
        data.rank || "—";
    document.getElementById("studentClass").innerText =
        data.classification || "—";
    document.getElementById("studentContact").innerText =
        data.contact_number || "—";
    document.getElementById("studentAddress").innerText =
        [data.address, data.city, data.province]
            .filter(Boolean)
            .join(", ") || "—";

    if (data.profile_picture) {
        document.getElementById("studentPhoto").src =
            data.profile_picture;
    }

    document.getElementById("studentCard").style.display = "block";

    console.log("[QR] UI updated, stopping scanner");
    stopQrScanner();
}

/* ============================================================
 * STOP SCANNER (FULL CLEANUP)
 * ============================================================ */
function stopQrScanner() {
    if (!html5QrCode) return;

    html5QrCode.stop()
        .then(() => {
            html5QrCode.clear();
            html5QrCode = null;
            isScannerRunning = false;
            console.log("[QR] Scanner fully stopped and cleared");
        })
        .catch(err => {
            console.warn("[QR] Error stopping scanner:", err);
        });
}

/* ============================================================
 * CANCEL ATTENDANCE (UI ONLY)
 * ============================================================ */
function cancelAttendance() {
    console.log("[QR] Attendance cancelled by user");
    document.getElementById("studentCard").style.display = "none";
}

/* ============================================================
 * EXPOSE GLOBALS
 * ============================================================ */
window.initQrScanner = initQrScanner;
window.startScanner = startScanner;
window.toggleCamera = toggleCamera;
window.stopQrScanner = stopQrScanner;
window.cancelAttendance = cancelAttendance;
