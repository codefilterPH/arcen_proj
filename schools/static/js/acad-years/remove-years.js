// ============================================================
// 🗑️ DELETE SCHOOL YEAR (using callback-based question_message)
// ============================================================
$("#schoolYearTable").on("click", ".btnDeleteYear", function () {
  const $row = $(this).closest("tr");
  const yearId = $row.data("year-id");

  if (!yearId) {
    error_message("Missing school year ID.");
    return;
  }

  // 🟨 Ask for confirmation — uses callback instead of .then()
  question_message("Are you sure you want to delete this school year?", function(isConfirmed) {
    if (!isConfirmed) {
      console.log("❎ School year deletion canceled by the user.");
      return;
    }

    // 🟢 Proceed with deletion
    $.ajax({
      url: `/api/academic-years/${yearId}/remove/`,
      type: "DELETE",
      headers: authHeaders(),
      beforeSend: function () {
        $row.css("opacity", "0.6");
      },
      success: function () {
        $row.fadeOut(300, () => $row.remove());
        success_message("School year deleted successfully.");
        if (window.currentSchoolId) reloadSchoolYearsForSchool(window.currentSchoolId);
      },
      error: function (xhr) {
        console.error("❌ Delete failed:", xhr);
        error_message("An error occurred while deleting the school year.");
        $row.css("opacity", "1");
      }
    });
  });
});
