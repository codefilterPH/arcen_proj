// ============================================================
// ✏️ EDIT SCHOOL YEAR HANDLER
// ============================================================
function initializeEditSchoolYearForm() {

  // 🟦 When modal opens → fill fields
  $("#editSchoolYearModal").on("show.bs.modal", function (event) {
    const button = $(event.relatedTarget); // Button that triggered the modal

    const yearId = button.data("year-id");
    const yearName = button.data("year-name");
    const startDate = button.data("year-start");
    const endDate = button.data("year-end");
    const schoolId = button.data("school-id"); // ✅ keep reference to the school

    // 🧩 Save globally for later use when reopening list
    if (schoolId) window.currentSchoolId = schoolId;

    $("#editYearId").val(yearId);
    $("#editYearName").val(yearName);
    $("#editYearStart").val(startDate);
    $("#editYearEnd").val(endDate);

    console.log("[EDIT YEAR] Opened for Year ID:", yearId, "School ID:", schoolId);
  });

  // 🟩 Handle form submission
  $("#editSchoolYearForm").on("submit", function (e) {
    e.preventDefault();

    const yearId = $("#editYearId").val();
    const data = {
      name: $("#editYearName").val(),
      start_date: $("#editYearStart").val(),
      end_date: $("#editYearEnd").val()
    };

    question_message("Are you sure you want to update this school year?", function(isConfirmed) {
      if (!isConfirmed) return;

      $.ajax({
        url: `/api/academic-years/${yearId}/update/`,
        type: "PUT",
        headers: authHeaders(),
        contentType: "application/json",
        data: JSON.stringify(data),

        beforeSend: function () {
          $("#editSchoolYearForm button[type=submit]")
            .prop("disabled", true)
            .html('<i class="fas fa-spinner fa-spin me-1"></i> Saving...');
        },

        success: function (response) {
          console.log("✅ School year updated:", response);
          success_message("School year updated successfully.");

          // ✅ Attach a one-time listener before hiding
          $("#editSchoolYearModal")
            .off("hidden.bs.modal.reopenList")
            .on("hidden.bs.modal.reopenList", function () {
              console.log("[MODAL] Edit School Year closed — reopening list for school:", window.currentSchoolId);

              // Reopen School Year list modal
              $("#schoolYearModal").modal("show");

              // 🌀 Reload data if function available
              if (window.currentSchoolId && typeof reloadSchoolYearsForSchool === "function") {
                setTimeout(() => {
                  console.log("[MODAL] Reloading school years for ID:", window.currentSchoolId);
                  reloadSchoolYearsForSchool(window.currentSchoolId);
                }, 400);
              }

              // Prevent duplicate binding
              $(this).off("hidden.bs.modal.reopenList");
            });

          // 🔹 Hide edit modal (this triggers above event)
          $("#editSchoolYearModal").modal("hide");
        },

        error: function (xhr) {
          console.error("❌ Update failed:", xhr);
          error_message("Failed to update school year. Please try again.");
        },

        complete: function () {
          $("#editSchoolYearForm button[type=submit]")
            .prop("disabled", false)
            .html('<i class="fas fa-save me-1"></i> Update Year');
        }
      });
    });
  });
}
