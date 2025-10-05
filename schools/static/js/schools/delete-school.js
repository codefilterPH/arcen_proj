function deleteSchool(schoolId, schoolName) {
    const csrfToken = $("input[name='csrfmiddlewaretoken']").val();
    const safeName = schoolName || "this school";

    if (!schoolId) {
        console.error("❌ Missing school ID for deletion.");
        error_message("Invalid school ID.");
        return;
    }

    // 🔸 Ask for confirmation
    question_message(`
            Are you sure you want to delete ${safeName}. This action cannot be undone
    `).then((result) => {
        if (result.isConfirmed) {
            console.log(`⚙️ Deleting school ID: ${schoolId}`);

            fetchWithRefresh(`/api/schools/${schoolId}/`, {
                type: "DELETE",
                headers: { "X-CSRFToken": csrfToken },
            })
                .done(function (response) {
                    console.log("✅ School deleted:", response);
                    success_message(`School <strong>${safeName}</strong> deleted successfully!`);
                    loadSchoolsGrid(); // refresh school list/grid
                })
                .fail(function (xhr) {
                    console.error("❌ Failed to delete school:", xhr.status, xhr.responseText);
                    const errMsg = xhr.responseJSON?.detail || "An error occurred while deleting the school.";
                    error_message(errMsg);
                });
        } else {
            console.log("🟡 School deletion canceled by user.");
        }
    });
}
