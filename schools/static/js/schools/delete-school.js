function deleteSchool(schoolId, schoolName) {
    const csrfToken = $("input[name='csrfmiddlewaretoken']").val();
    const safeName = schoolName || "this school";

    if (!schoolId) {
        console.error("❌ Missing school ID for deletion.");
        error_message("Invalid school ID.");
        return;
    }

    question_message(
        `Are you sure you want to delete ${safeName}. This action cannot be undone.`,
        true,
        function (result) {

            if (!result || !result.isConfirmed) {
                console.log("🟡 School deletion cancelled");
                return;
            }

            console.log(`⚙️ Deleting school ID: ${schoolId}`);

            fetchWithRefresh(`/api/schools/${schoolId}/`, {
                type: "DELETE",
                headers: { "X-CSRFToken": csrfToken },
            })
            .done(() => {
                console.log("✅ School deleted");
                showToastSwal(
                    `School <strong>${safeName}</strong> deleted successfully!`
                , "success");
                $("#btnRefresh").click();
            })
            .fail((xhr) => {
                console.error("❌ Delete failed:", xhr.status, xhr.responseText);
                error_message(
                    xhr.responseJSON?.detail ||
                    "An error occurred while deleting the school."
                );
            });
        }
    );
}
