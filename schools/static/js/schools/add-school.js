function initializeAddSchoolForm() {
    $("#addSchoolForm").on("submit", function (e) {
        e.preventDefault();

        let form = this;
        let formData = new FormData(form);

        fetchWithRefresh('/api/schools/', {
            type: 'POST',
            data: formData,
            processData: false,   // ✅ required for FormData
            contentType: false,   // ✅ let browser set multipart/form-data
        }).done(function (response) {
            console.log("✅ School created:", response);

            // Success message
            showToastSwal("School added successfully!", "success    ");
            // Close modal
            location.reload();  

        }).fail(function (xhr) {
            console.error("❌ Failed to create school:", xhr.status, xhr.responseText);

            let errorResponse = xhr.responseJSON;
            if (errorResponse) {
                let messages = [];
                if (errorResponse.name) messages.push("Name: " + errorResponse.name.join(", "));
                if (errorResponse.address) messages.push("Address: " + errorResponse.address.join(", "));
                if (errorResponse.logo) messages.push("Logo: " + errorResponse.logo.join(", "));

                error_message(messages.join("<br>"));
            } else {
                error_message("An unexpected error occurred while creating the school.");
            }
        });
    });
}