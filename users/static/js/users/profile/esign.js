const canvas = document.getElementById('signature-pad');
const ctx = canvas.getContext('2d');

let drawing = false;

/* ==============================
   Canvas setup (HD / Retina safe)
================================ */
function resizeCanvas() {
    const ratio = Math.max(window.devicePixelRatio || 1, 1);
    const rect = canvas.getBoundingClientRect();

    canvas.width = rect.width * ratio;
    canvas.height = rect.height * ratio;

    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);

    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#1e40af'; // clean professional blue

}

/* ==============================
   Helpers
================================ */
function getPosition(event) {
    const rect = canvas.getBoundingClientRect();

    if (event.touches && event.touches[0]) {
        return {
            x: event.touches[0].clientX - rect.left,
            y: event.touches[0].clientY - rect.top
        };
    }

    return {
        x: event.offsetX,
        y: event.offsetY
    };
}

/* ==============================
   Drawing handlers
================================ */
function startDrawing(event) {
    event.preventDefault();
    drawing = true;

    const pos = getPosition(event);
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
}

function draw(event) {
    if (!drawing) return;
    event.preventDefault();

    const pos = getPosition(event);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
}

function stopDrawing(event) {
    event?.preventDefault();
    drawing = false;
}

/* ==============================
   Controls
================================ */
function clearSignature() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function saveSignature() {
    const dataURL = canvas.toDataURL('image/png');

    const csrfToken = $('meta[name="csrf-token"]').attr('content');
    const accessToken = localStorage.getItem('accessToken');

    $.ajax({
        url: '/api/user-profile/upload-signature/',
        type: 'POST',
        contentType: 'application/json',
        beforeSend: function (xhr) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
            xhr.setRequestHeader('Authorization', 'Bearer ' + accessToken);
        },
        data: JSON.stringify({ signature: dataURL }),
        success: function (response) {
            showToastSwal(response.message || 'Signature saved', 'success');
            getProfile(); // refresh profile
        },
        error: function (xhr) {
            console.error('Signature upload failed:', xhr.responseText);
            showToastSwal('Failed to save signature', 'error');
        }
    });
}

/* ==============================
   Event bindings
================================ */
window.addEventListener('resize', resizeCanvas);

// Mouse
canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDrawing);
canvas.addEventListener('mouseout', stopDrawing);

// Touch (MOBILE FIX)
canvas.addEventListener('touchstart', startDrawing, { passive: false });
canvas.addEventListener('touchmove', draw, { passive: false });
canvas.addEventListener('touchend', stopDrawing);
canvas.addEventListener('touchcancel', stopDrawing);

// Init
resizeCanvas();
