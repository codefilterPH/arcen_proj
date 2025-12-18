// ------------------------------------------------------------
// 🔹 API call to remove student (uses global authHeaders)
// ------------------------------------------------------------
function removeStudent(studentId, schoolId, $row) {
  if (!studentId || !schoolId) {
    console.error("❌ Missing required parameters for removeStudent()");
    showToastSwal("Missing student or school ID.", "error");
    return;
  }

  $.ajax({
    url: "/api/students/remove/",
    method: "POST",
    headers: authHeaders(), // ✅ uses global helper for CSRF + Bearer token
    contentType: "application/json",
    data: JSON.stringify({
      school_id: schoolId,
      student_ids: [studentId],
    }),

    beforeSend: function () {
      $row.addClass("opacity-50"); // subtle fade while deleting
    },

    success: function (res) {
      console.log("✅ Student removed:", res);

      // Smoothly remove row
      $row.fadeOut(300, function () {
        $(this).remove();
        if (!$("#studentsTable tbody tr").length) {
          $("#studentsTable tbody").html(`
            <tr><td colspan="8" class="text-center text-muted">No students found.</td></tr>
          `);
        }
      });

      showToastSwal(res.message || "Student removed successfully.", "success");
    },

    error: function (xhr) {
      console.error("❌ Failed to remove student:", xhr);
      const errorMsg = xhr.responseJSON?.detail || "Failed to remove student.";
      showToastSwal(errorMsg, "error");
      $row.removeClass("opacity-50");
    },
  });
}
