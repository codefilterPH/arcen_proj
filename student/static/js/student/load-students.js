// ===============================
// Students Modal with Pagination
// ===============================

window.currentSchoolId = null; // 🌍 Global

// ===============================
// Student Status → Badge Mapper
// ===============================
function getStudentStatusBadge(student) {
  // Hard override if inactive
  if (student.is_active === false) {
    return {
      class: "bg-secondary",
      label: "Inactive"
    };
  }

  const map = {
    pending: {
      class: "bg-warning text-dark",
      label: "Pending"
    },
    enrolled: {
      class: "bg-success",
      label: "Enrolled"
    },
    on_leave: {
      class: "bg-info text-dark",
      label: "On Leave"
    },
    graduated: {
      class: "bg-primary",
      label: "Graduated"
    },
    transferred: {
      class: "bg-dark",
      label: "Transferred"
    },
    dropped: {
      class: "bg-danger",
      label: "Dropped"
    }
  };

  return map[student.enrollment_status] || {
    class: "bg-secondary",
    label: student.enrollment_status || "Unknown"
  };
}

function initStudentsModal(options = {}) {
  const modalSelector = options.modalSelector || "#studentsModal";
  const tableSelector = options.tableSelector || "#studentsTable";

  const $modal = $(modalSelector);
  const $tableBody = $(`${tableSelector} tbody`);
  const $pagination = $("#paginationContainerStudents");

  let currentSchoolId = null;
  let currentPage = 1;

  // ===============================
  // MODAL OPEN
  // ===============================
  $modal.on("show.bs.modal", function (event) {
    const button = event.relatedTarget;
    let schoolId = $(button).data("school-id");
    let schoolName = $(button).data("school-name") || "School";

    if (!schoolId) {
      schoolId = $modal.data("school-id");
      schoolName = $modal.data("school-name") || schoolName;
    }

    if (!schoolId) {
      $tableBody.html(
        `<tr><td colspan="8" class="text-center text-danger">Missing school ID.</td></tr>`
      );
      return;
    }

    window.currentSchoolId = schoolId;
    currentSchoolId = schoolId;
    currentPage = 1;

    $("#studentsModalLabel").text(`Students Management — ${schoolName}`);
    $("#btnAddStudent")
      .data("school-id", schoolId)
      .data("school-name", schoolName);

    loadStudents(currentSchoolId, currentPage);
  });

  // ===============================
  // REFRESH BUTTON
  // ===============================
  $("#btnRefreshStudents").on("click", () => {
    if (currentSchoolId) {
      loadStudents(currentSchoolId, currentPage);
    }
  });

  // ===============================
  // FILTERS
  // ===============================
  $("#filterSearch, #filterSchoolYear, #filterSemester, #filterFlight")
    .on("change keyup", () => {
      if (currentSchoolId) {
        currentPage = 1;
        loadStudents(currentSchoolId, currentPage);
      }
    });

  // ===============================
  // LOAD STUDENTS
  // ===============================
  function loadStudents(schoolId, page = 1) {
    currentPage = page;

    const params = {
      page,
      search: $("#filterSearch").val() || "",
      school_year: $("#filterSchoolYear").val() || "",
      semester: $("#filterSemester").val() || "",
      flight: $("#filterFlight").val() || "",
    };

    const endpoint =
      `/api/students/schools/${schoolId}/students/?${$.param(params)}`;

    $tableBody.html(
      `<tr><td colspan="8" class="text-center py-3 text-muted">Loading...</td></tr>`
    );

    $.ajax({
      url: endpoint,
      method: "GET",
      headers: authHeaders(),
      success: function (res) {
        const students = res.results || [];

        if (!students.length) {
          $tableBody.html(
            `<tr><td colspan="8" class="text-center text-muted">No students found.</td></tr>`
          );
          buildPagination(res);
          return;
        }

        const rows = students.map((student) => {
  const badge = getStudentStatusBadge(student);

  return `
    <tr data-student-id="${student.id}">

      <!-- Profile -->
      <td class="text-center">
        <img src="${student.profile_image || "/static/img/users/avatars/default.png"}"
             class="student-photo rounded-circle"
             style="width:40px;height:40px;object-fit:cover;">
      </td>

      <!-- QR -->
      <td class="text-center">
        <img src="${student.qr_image || "/static/img/qr_sample.png"}"
             class="qr-code"
             style="width:40px;height:40px;">
      </td>

      <!-- Full Name -->
      <td class="fw-semibold">
        ${student.full_name || "—"}
      </td>

      <!-- Enrollment Status -->
      <td class="text-center">
        <span class="badge ${badge.class}">
          ${badge.label}
        </span>
        ${
          student.enrolled_at
            ? `<small class="text-muted d-block">
                 ${dayjs(student.enrolled_at).format("MMM D, YYYY")}
               </small>`
            : ""
        }
      </td>

      <!-- Active Status -->
      <td class="text-center">
        ${
          student.is_active
            ? `<span class="badge bg-success">Active</span>`
            : `<span class="badge bg-secondary">Inactive</span>`
        }
      </td>

      <!-- Gender -->
      <td class="text-center">
        ${student.gender || "—"}
      </td>

      <!-- Contact -->
      <td>
        ${student.contact_number || "—"}
      </td>

      <!-- Actions -->
      <td class="text-center" style="white-space:nowrap;">
        <button class="btn btn-sm btn-outline-primary btnDownloadQR"
                data-qr-url="${student.qr_image}"
                data-student-id="${student.id}"
                title="Download QR Code">
          <i class="fas fa-qrcode"></i>
        </button>

        <button class="btn btn-sm btn-outline-secondary btnEditStudent"
                data-student-id="${student.id}"
                title="Edit Student"
                data-bs-toggle="modal"
                data-bs-target="#editStudentModal">
          <i class="fas fa-edit"></i>
        </button>

        <button class="btn btn-sm btn-outline-success btnUploadStudentFile"
                data-student-id="${student.id}"
                title="Upload File">
          <i class="fas fa-upload"></i>
        </button>

        <button class="btn btn-sm btn-outline-danger btnRemoveStudent"
                data-student-id="${student.id}"
                title="Remove Student">
          <i class="fas fa-trash"></i>
        </button>
      </td>

    </tr>
  `;
});

        $tableBody.html(rows.join(""));
        buildPagination(res);
      },
      error: function (xhr) {
        $tableBody.html(
          `<tr><td colspan="8" class="text-center text-danger">
            Error loading data (${xhr.status})
          </td></tr>`
        );
      },
    });
  }

  // ===============================
  // PAGINATION BUILDER
  // ===============================
  function buildPagination(res) {
    $pagination.empty();

    const count = res.count || 0;
    const pageSize = res.results?.length || 10;
    const totalPages = Math.ceil(count / pageSize);

    if (totalPages <= 1) {
      $pagination.html(
        `<small class="text-muted">Showing ${count} record(s)</small>`
      );
      return;
    }

    let html = `
      <nav aria-label="Students pagination">
        <ul class="pagination pagination-students justify-content-center mb-0">
          <li class="page-item ${currentPage === 1 ? "disabled" : ""}">
            <button class="page-link" data-page="${currentPage - 1}">‹ Prev</button>
          </li>
    `;

    const maxVisible = 5;
    let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);

    for (let i = start; i <= end; i++) {
      html += `
        <li class="page-item ${i === currentPage ? "active" : ""}">
          <button class="page-link" data-page="${i}">${i}</button>
        </li>
      `;
    }

    html += `
          <li class="page-item ${currentPage === totalPages ? "disabled" : ""}">
            <button class="page-link" data-page="${currentPage + 1}">Next ›</button>
          </li>
        </ul>
      </nav>
      <small class="text-muted d-block mt-2 text-center">
        Page ${currentPage} of ${totalPages} — Showing ${res.results.length} of ${count} students
      </small>
    `;

    $pagination.html(html);
  }

  // ===============================
  // PAGINATION CLICK HANDLER
  // ===============================
  $(document).on("click", ".pagination-students .page-link", function () {
    const page = parseInt($(this).data("page"));
    if (!page || page < 1 || page === currentPage) return;
    loadStudents(currentSchoolId, page);
  });

  // ===============================
  // EXTERNAL RELOAD HOOK
  // ===============================
  window.reloadStudentsForSchool = function (schoolId) {
    currentSchoolId = schoolId;
    currentPage = 1;
    loadStudents(schoolId, currentPage);
  };
}
