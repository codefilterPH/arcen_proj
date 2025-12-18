// ------------------------------------------------------------
// ➕ Handle Add School Year Submission
// ------------------------------------------------------------
$("#addSchoolYearForm").on("submit", function (e) {
  e.preventDefault();

  const schoolId = window.currentSchoolId; // ✅ get the active school id
  if (!schoolId) {
    showToastSwal("No school selected. Please open from a school.", "error");
    return;
  }

  const formData = Object.fromEntries(new FormData(this).entries());
  const endpoint = `/api/academic-years/${schoolId}/add-year/`;

  $.ajax({
    url: endpoint,
    method: "POST",
    headers: authHeaders(),
    contentType: "application/json",
    data: JSON.stringify(formData),
    beforeSend: () => {
      $("#addSchoolYearForm button[type=submit]")
        .prop("disabled", true)
        .html('<i class="fas fa-spinner fa-spin me-1"></i> Saving...');
    },
    success: (res) => {

      showToastSwal("Academic year added successfully.", "success");
      $("#addSchoolYearForm")[0].reset();
      if (schoolId) reloadSchoolYearsForSchool(schoolId);
      $("#btnCloseAddSY").click();
    },
    error: (xhr) => {
      console.error("❌ Add failed:", xhr.responseText);
      showToastSwal("Failed to add academic year.", "error");
    },
    complete: () => {
      $("#addSchoolYearForm button[type=submit]")
        .prop("disabled", false)
        .html('<i class="fas fa-save me-1"></i> Save');
    }
  });
});
