function initializeEditSchoolForm() {
    $("#editSchoolForm").on("submit", function (e) {
        e.preventDefault(); // 🧱 stop browser from posting to "/"

        const form = this;
        const formData = new FormData(form);
        const schoolId = $(form).attr("data-school-id");

        if (!schoolId) {
            console.error("❌ Missing school ID for edit.");
            error_message("No school selected to edit.");
            return;
        }

        $.ajax({
            url: `/api/schools/${schoolId}/`,
            method: "PATCH",
            headers: authHeaders(),     // ✅ include Authorization + CSRF
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                console.log("✅ School updated:", response);
                success_message("School updated successfully!");
                $("#btnCloseEditModal").click();
                $("#btnRefresh").click();
            },
            error: function (xhr) {
                console.error("❌ Failed to update school:", xhr);

                const err = xhr.responseJSON;
                if (err) {
                    let messages = [];
                    if (err.name) messages.push("Name: " + err.name.join(", "));
                    if (err.address) messages.push("Address: " + err.address.join(", "));
                    if (err.logo) messages.push("Logo: " + err.logo.join(", "));
                    error_message(messages.join("<br>"));
                } else {
                    error_message("An unexpected error occurred while updating the school.");
                }
            },
        });
    });
}
