const canvas = document.getElementById('signature-pad');
const ctx = canvas.getContext('2d');
let drawing = false;

function resizeCanvas() {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
}

function startDrawing(event) {
    drawing = true;
    ctx.beginPath();
    ctx.moveTo(event.offsetX, event.offsetY);
}

function draw(event) {
    if (!drawing) return;
    ctx.lineTo(event.offsetX, event.offsetY);
    ctx.stroke();
}

function stopDrawing() {
    drawing = false;
}

function clearSignature() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function saveSignature() {
    const dataURL = canvas.toDataURL();
    console.log("Signature Saved:", dataURL);
    csrfToken = $('meta[name="csrf-token"]').attr('content');
    var accessToken = localStorage.getItem('accessToken');
    $.ajax({
        url: '/api/user-profile/upload-signature/',
        type: 'POST',
        contentType: 'application/json',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
            xhr.setRequestHeader('Authorization', 'Bearer ' + accessToken);
        },
        data: JSON.stringify({signature: dataURL}),
        success: function(response) {
            if(response.stop) {
                stop_message(response.stop);
            }
            console.log('Response: ', response.message);
            success_message(response.message);

            getUserData();

            signaturePic.focus();
        },
        error: function(xhr, textStatus, errorThrown) {
            console.error('Error answer submission:', errorThrown);
        }
    });
}

window.addEventListener('resize', resizeCanvas);
canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDrawing);
canvas.addEventListener('mouseout', stopDrawing);

resizeCanvas(); // Initialize canvas size