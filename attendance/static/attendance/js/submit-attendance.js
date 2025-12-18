function confirmAttendance() {
    const userId = window.scannedUserId;
    const status = $("#attendanceStatus").val();

    if (!userId) {
        error_message("❌ No scanned User ID found.");
        return;
    }

    const payload = {
        user_id: userId,
        status: status
    };

    console.log("📤 Sending attendance payload:", payload);

    $.ajax({
        url: "/api/attendance/submit/",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify(payload),
        headers: authHeaders(),   // 🔥 Your global header function
        success: function (response) {
            console.log("✅ Attendance saved:", response);

            success_message(`Attendance Confirmed<br>User ID: ${userId}<br>Status: ${status}`);

            // Optionally hide card
            $("#studentCard").fadeOut();
        },
        error: function (xhr) {
            console.error("❌ Attendance error:", xhr.responseJSON);

            const msg = xhr.responseJSON?.error || "Unknown error";
            error_message(`❌ ${msg}`);
        }
    });
}
