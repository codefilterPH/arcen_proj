// 🔥 One merged handler (no separate getMyQR())

$('#usersTable').on('click', '.btn-show-qr', function () {
    const profileId = $(this).data('profile-id');

    Pace.restart();

    $.ajax({
        url: `/api/users/${profileId}/qr/`,
        method: "GET",
        headers: authHeaders(),
        xhrFields: { withCredentials: true },

        success: function (res) {
            // Insert QR to modal
            $('#qrModalImage').attr('src', `data:image/png;base64,${res.qr_base64}`);
            $('#qrModalName').text(res.full_name || 'User');

            // Bootstrap modal auto opens because of data-bs-toggle + data-bs-target
        },

        error: function (err) {
            console.error("QR Fetch Failed:", err);
            alert("Failed to load QR code.");
        },

        complete: function () {
            Pace.stop();
        }
    });
});

// Download QR Code as PNG
$('#btnDownloadQR').on('click', function () {
    const imgSrc = $('#qrModalImage').attr('src');

    if (!imgSrc) {
        alert("No QR code to download.");
        return;
    }

    // Create fake link to trigger download
    const link = document.createElement('a');
    link.href = imgSrc;
    link.download = `QR_Code_${Date.now()}.png`;
    link.click();
});
