function loadStudentProfile(studentId) {
  $.ajax({
    url: `/api/students/get-student-profile/${studentId}/`,
    type: "GET",
    headers: authHeaders(),

    success: function (data) {
      console.log("✅ Student profile loaded:", data);

      /* =========================
         LEFT PANEL (PROFILE)
      ========================= */

      // Full name (already formatted server-side)
      $("#studentFullName").text(
        (data.full_name || "—").toUpperCase()
      );

      $("#student_id").text(data.student_id || "—");

      // Status badge
      $("#studentStatusBadge")
        .text(data.is_active ? "ACTIVE" : "INACTIVE")
        .removeClass("bg-success bg-secondary")
        .addClass(data.is_active ? "bg-success" : "bg-secondary");

      // Profile image
      if (data.profile_image) {
        $("#studentProfilePic").attr("src", data.profile_image);
      }

      // QR image (already data URL)
      if (data.qr_image) {
        $("#studentQrCode")
          .attr("src", data.qr_image)
          .removeClass("d-inline")
          .addClass("d-block mx-auto");
      }

      /* =========================
         FORM FIELDS
      ========================= */

      // Enrollment
      $("#enrollment_status").val(data.enrollment_status);
      $("#is_active").val(String(data.is_active));

      // Identity snapshot (NOT auth_user)
      $("#first_name").val(data.first_name || "");
      $("#last_name").val(data.last_name || "");
      $("#email").val(data.email || "");

      $("#middle_name").val(data.middle_name || "");
      $("#preferred_initial").val(data.preferred_initial || "");
      $("#extension_name").val(data.extension_name || "");

      $("#gender").val(data.gender || "");
      $("#birth_date").val(data.birth_date || "");
      $("#contact_number").val(data.contact_number || "");
      $("#display_name_format").val(data.display_name_format || "title");

      // Classification (FK id)
      if (data.classification) {
        $("#classification").val(data.classification);
      } else {
        $("#classification").val("");
      }

      // Designations (M2M ids)
      if (Array.isArray(data.designations)) {
        $("#designations")
          .val(data.designations)
          .trigger("change");
      } else {
        $("#designations").val([]).trigger("change");
      }
    },

    error: function (xhr) {
      console.error("❌ Failed to load student profile", xhr);
      showToastSwal("Failed to load student profile.", "error");
    }
  });
}
