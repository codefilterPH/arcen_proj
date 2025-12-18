window.currentSchoolId = null; // 🌍 Global

function initStudentsModal(options = {}) {
  const modalSelector = options.modalSelector || "#studentsModal";
  const tableSelector = options.tableSelector || "#studentsTable";
  const paginationSelector = options.paginationSelector || "#paginationContainer";

  const $modal = $(modalSelector);
  const $tableBody = $(`${tableSelector} tbody`);
  const $pagination = $(paginationSelector);
  let currentSchoolId = null;

  // 🟦 When modal opens
  $modal.on("show.bs.modal", function (event) {
    const button = event.relatedTarget;
    let schoolId = $(button).data("school-id");
    let schoolName = $(button).data("school-name") || "School";

    if (!schoolId) {
      schoolId = $modal.data("school-id");
      schoolName = $modal.data("school-name") || schoolName;
    }

    window.currentSchoolId = schoolId;
    currentSchoolId = schoolId;

    if (!schoolId) {
      $tableBody.html(`<tr><td colspan="8" class="text-center text-danger">Missing school ID.</td></tr>`);
      return;
    }

    $("#studentsModalLabel").text(`Students Management — ${schoolName}`);
    $("#btnAddStudent").data("school-id", schoolId).data("school-name", schoolName);
    loadStudents(schoolId);
  });

  // 🔄 Refresh
  $("#btnRefreshStudents").on("click", () => {
    if (currentSchoolId) loadStudents(currentSchoolId);
  });

  // 🔍 Filters
  $("#filterSearch, #filterSchoolYear, #filterSemester, #filterFlight").on("change keyup", () => {
    if (currentSchoolId) loadStudents(currentSchoolId);
  });

  // 🔹 Load Students
  function loadStudents(schoolId, url = null) {
    const params = {
      search: $("#filterSearch").val() || "",
      school_year: $("#filterSchoolYear").val() || "",
      semester: $("#filterSemester").val() || "",
      flight: $("#filterFlight").val() || "",
    };

    const endpoint = url || `/api/schools/${schoolId}/students/?${$.param(params)}`;
    $tableBody.html(`<tr><td colspan="8" class="text-center py-3 text-muted">Loading...</td></tr>`);

    $.ajax({
      url: endpoint,
      method: "GET",
      headers: authHeaders(),
      success: (res) => {
        console.log("[LOAD STUDENTS]:", res);
        const students = res.results || [];
        if (!students.length) {
          $tableBody.html(`<tr><td colspan="8" class="text-center text-muted">No students found.</td></tr>`);
          buildPagination(res);
          return;
        }

        const rows = students.map((student) => `
          <tr data-student-id="${student.id}">
            <td><img src="${student.profile_image || '/static/img/users/avatars/default.png'}" class="student-photo"></td>
            <td><img src="${student.qr_image || '/static/img/qr_sample.png'}" class="qr-code"></td>
            <td>${student.full_name || "—"}</td>
            <td>${student.gender || "—"}</td>
            <td>${student.birth_date || "—"}</td>
            <td>${student.contact_number || "—"}</td>
            <td><span class="badge bg-success">${student.status || "Enrolled"}</span></td>
            <td class="text-center">
              <button class="btn btn-sm btn-danger btnRemoveStudent" title="Remove Student">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>`);

        $tableBody.html(rows.join(""));
        buildPagination(res);
      },
      error: (xhr) => {
        $tableBody.html(`<tr><td colspan="8" class="text-center text-danger">Error loading data (${xhr.status})</td></tr>`);
      },
    });
  }

  // 🧭 Pagination
// 🧭 Pagination (unique to Students Modal)
function buildPagination(res) {
  const $pagination = $("#paginationContainerStudents");
  $pagination.empty();

  const count = res.count || 0;
  const results = res.results || [];
  const totalPages = Math.ceil(count / (results.length || 10));

  if (totalPages <= 1) {
    $pagination.html(`<small class="text-muted">Showing ${count} record(s)</small>`);
    return;
  }

  // Determine current page
  let currentPage = 1;
  if (res.next) currentPage = parseInt(new URL(res.next, window.location.origin).searchParams.get("page")) - 1;
  else if (res.previous) currentPage = parseInt(new URL(res.previous, window.location.origin).searchParams.get("page")) + 1;

  let html = `
    <nav aria-label="Students pagination">
      <ul class="pagination pagination-students justify-content-center mb-0">
        <li class="page-item ${currentPage === 1 ? "disabled" : ""}">
          <button class="page-link" data-page="1">« First</button>
        </li>
        <li class="page-item ${currentPage === 1 ? "disabled" : ""}">
          <button class="page-link" data-page="${currentPage - 1}">‹ Prev</button>
        </li>
  `;

  const maxVisible = 5;
  let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
  let end = Math.min(totalPages, start + maxVisible - 1);
  if (end - start + 1 < maxVisible) start = Math.max(1, end - maxVisible + 1);

  for (let i = start; i <= end; i++) {
    html += `
      <li class="page-item ${i === currentPage ? "active" : ""}">
        <button class="page-link" data-page="${i}">${i}</button>
      </li>`;
  }

  html += `
        <li class="page-item ${currentPage === totalPages ? "disabled" : ""}">
          <button class="page-link" data-page="${currentPage + 1}">Next ›</button>
        </li>
        <li class="page-item ${currentPage === totalPages ? "disabled" : ""}">
          <button class="page-link" data-page="${totalPages}">Last »</button>
        </li>
      </ul>
    </nav>
    <small class="text-muted d-block mt-2 text-center">
      Page ${currentPage} of ${totalPages} — Showing ${results.length} of ${count} students
    </small>
  `;

  $pagination.html(html);
}

// ✅ Delegated click handler (unique)
$(document)
  .off("click", "#paginationContainerStudents .page-link")
  .on("click", "#paginationContainerStudents .page-link", function (e) {
    e.preventDefault();
    const $btn = $(this);
    const page = $btn.data("page");

    if (!page || $btn.parent().hasClass("disabled") || $btn.parent().hasClass("active")) {
      console.log("[STUDENTS PAGINATION] Ignored click — disabled or active button");
      return;
    }

    // Identify which button was clicked
    const label = $btn.text().trim();
    if (label.includes("Next")) console.log("[STUDENTS PAGINATION] ▶️ NEXT → Page:", page);
    else if (label.includes("Prev")) console.log("[STUDENTS PAGINATION] ◀️ PREV → Page:", page);
    else if (label.includes("First")) console.log("[STUDENTS PAGINATION] ⏮️ FIRST → Page:", page);
    else if (label.includes("Last")) console.log("[STUDENTS PAGINATION] ⏭️ LAST → Page:", page);
    else console.log(`[STUDENTS PAGINATION] 🔢 Number ${page} clicked`);

    const params = {
      search: $("#filterSearch").val() || "",
      school_year: $("#filterSchoolYear").val() || "",
      semester: $("#filterSemester").val() || "",
      flight: $("#filterFlight").val() || "",
      page: page,
    };

    const endpoint = `/api/schools/${window.currentSchoolId}/students/?${$.param(params)}`;
    console.log("[STUDENTS PAGINATION] Loading endpoint:", endpoint);

    loadStudents(window.currentSchoolId, endpoint);
    $("#studentsModal .modal-body").animate({ scrollTop: 0 }, 300);
  });

  // 🔁 External trigger
  window.reloadStudentsForSchool = (schoolId) => loadStudents(schoolId);
}
