let html5QrCode = null;
let availableCameras = [];

window.scannedUserData = {};
window.scannedUserId = null;

// --------------------------------
// INIT — list cameras only
// --------------------------------
async function initQrScanner() {
    if (html5QrCode) return;

    try {
        // 🔐 STEP 1: Ask permission safely (NO Html5Qrcode yet)
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });

        // Immediately stop tracks (permission stays granted)
        stream.getTracks().forEach(t => t.stop());

        // 🔍 STEP 2: Enumerate cameras (labels now visible)
        const cameras = await Html5Qrcode.getCameras();

        if (!cameras.length) {
            alert("No cameras found.");
            return;
        }

        populateCameraSelector(cameras);
        document.getElementById("cameraChooser").style.display = "block";

        // ✅ STEP 3: Create scanner only AFTER permission
        html5QrCode = new Html5Qrcode("reader");

    } catch (err) {
        console.error("Camera permission denied or failed:", err);
    }
}

// --------------------------------
// Populate selector
// --------------------------------
function populateCameraSelector(cameras) {
    const select = document.getElementById("cameraSelect");
    select.innerHTML = "";

    cameras.forEach((cam, index) => {
        const opt = document.createElement("option");
        opt.value = cam.id;
        opt.text = cam.label || `Camera ${index + 1}`;

        if (cam.label && /back|rear|environment/i.test(cam.label)) {
            opt.selected = true;
        }

        select.appendChild(opt);
    });
}

// --------------------------------
// Start selected camera
// --------------------------------
async function startSelectedCamera() {
    const cameraId = document.getElementById("cameraSelect").value;

    if (!cameraId) {
        alert("Please select a camera.");
        return;
    }

    document.getElementById("cameraChooser").style.display = "none";

    try {
        await html5QrCode.start(
            cameraId,
            {
                fps: 15,
                qrbox: { width: 300, height: 300 },
                aspectRatio: 1.0,
                experimentalFeatures: {
                    useBarCodeDetectorIfSupported: true
                },
                videoConstraints: {
                    focusMode: "continuous",
                    exposureMode: "continuous"
                }
            },
            onScanSuccess,
            () => {}
        );
    } catch (err) {
        console.error("Failed to start scanner:", err);
    }
}

// --------------------------------
// Scan success
// --------------------------------
function onScanSuccess(decodedText) {
    handleDecodedQR(decodedText);
}

// --------------------------------
// Handle decoded QR
// --------------------------------
function handleDecodedQR(decodedText) {
    let data;

    try {
        data = JSON.parse(decodedText);
    } catch {
        document.getElementById("result").innerText = "Invalid QR format";
        return;
    }

    window.scannedUserData = data;
    window.scannedUserId = data.user_id;

    document.getElementById("result").innerText = `Scanned: ${data.name}`;
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

// --------------------------------
// Stop scanner
// --------------------------------
function stopQrScanner() {
    if (html5QrCode) {
        html5QrCode.stop()
            .then(() => {
                html5QrCode.clear();
                html5QrCode = null;
            })
            .catch(() => {});
    }
}

// --------------------------------
// Cancel
// --------------------------------
function cancelAttendance() {
    document.getElementById("studentCard").style.display = "none";
}

// Expose globals
window.initQrScanner = initQrScanner;
window.startSelectedCamera = startSelectedCamera;
window.stopQrScanner = stopQrScanner;
window.cancelAttendance = cancelAttendance;
