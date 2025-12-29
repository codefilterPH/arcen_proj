// load-school-years.js
window.currentSchoolId = null; // 🌍 Global scope for active school ID

function initGetSchoolYear(options = {}) {
  console.log("[INIT] initGetSchoolYear called", options);

  const modalSelector = options.modalSelector || "#schoolYearModal";
  const tableSelector = options.tableSelector || "#schoolYearTable";
  const paginationSelector = options.paginationSelector || "#paginationContainer";

  const $modal = $(modalSelector);
  const $table = $(tableSelector);
  const $tableBody = $(`${tableSelector} tbody`);
  const $pagination = $(paginationSelector);

  console.log("[INIT] Modal found:", $modal.length);
  console.log("[INIT] Table found:", $table.length);

  let currentSchoolId = null;
  let searchTimeout = null;

  // ------------------------------------------------------------
  // 🟦 When modal opens
  // ------------------------------------------------------------
  $modal.on("show.bs.modal", function (event) {
    console.log("[MODAL] show.bs.modal triggered");

    const button = event.relatedTarget;
    console.log("[MODAL] Trigger button:", button);

    let schoolId = null;
    let schoolName = "School";

    if (button) {
      schoolId = $(button).data("school-id");
      schoolName = $(button).data("school-name") || "School";
    }

    console.log("[MODAL] Extracted schoolId:", schoolId);
    console.log("[MODAL] Extracted schoolName:", schoolName);

    if (!schoolId) {
      if (window.currentSchoolId) {
        console.warn(
          "[MODAL] No trigger schoolId, reusing cached:",
          window.currentSchoolId
        );
        schoolId = window.currentSchoolId;
        schoolName = "Current School";
      } else {
        console.error("[MODAL] ❌ No schoolId available");
        showToastSwal("Missing school ID when opening modal.", "error");
        $tableBody.html(
          `<tr><td colspan="5" class="text-center text-danger py-3">Missing school ID.</td></tr>`
        );
        return;
      }
    }

    // Store IDs
    window.currentSchoolId = schoolId;
    currentSchoolId = schoolId;

    console.log("[STATE] currentSchoolId set to:", currentSchoolId);

    // Update modal title
    $("#schoolYearModalLabel").text(
      `School Year Management — ${schoolName}`
    );

    console.log("[MODAL] Loading school years...");
    loadSchoolYears(currentSchoolId);
  });

  $tableBody.on("click", ".btnEditYear", function () {
    const yearId = $(this).data("year-id");

    console.log("[EDIT] Edit clicked for year:", yearId);

    openEditSchoolYearModal(yearId);
  });

  // ------------------------------------------------------------
  // 🔄 Refresh button
  // ------------------------------------------------------------
  $("#btnRefreshSchoolYear").on("click", function () {
    console.log("[ACTION] Refresh clicked");

    if (currentSchoolId) {
      loadSchoolYears(currentSchoolId);
    } else {
      console.warn("[ACTION] Refresh clicked but no school selected");
      showToastSwal("No school selected to refresh.", "error");
    }
  });

  // ------------------------------------------------------------
  // 🔍 Live Search
  // ------------------------------------------------------------
  $("#filterSchoolYearSearch").on("keyup", function () {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      console.log("[SEARCH] Triggered for school:", currentSchoolId);

      if (currentSchoolId) {
        loadSchoolYears(currentSchoolId);
      } else {
        console.warn("[SEARCH] Ignored — no school selected");
      }
    }, 400);
  });

  // ------------------------------------------------------------
  // 🔹 Load School Years from API
  // ------------------------------------------------------------
  function loadSchoolYears(schoolId, url = null) {
    console.log("[API] loadSchoolYears called with:", schoolId, url);

    if (!schoolId) {
      console.error("[API] ❌ Missing schoolId");
      showToastSwal("Missing school ID when loading data.", "error");
      return;
    }

    const search = $("#filterSchoolYearSearch").val() || "";
    const endpoint =
      url ||
      `/api/academic-years/${schoolId}/school-years/?search=${encodeURIComponent(
        search
      )}`;

    console.log("[API] Endpoint:", endpoint);

    $tableBody.html(
      `<tr><td colspan="5" class="text-center py-3 text-muted">Loading...</td></tr>`
    );

    $.ajax({
      url: endpoint,
      method: "GET",
      headers: authHeaders(),
      success: function (res) {
        console.log("[API] Response received:", res);

        const years = res.results || res;

        if (!years || !years.length) {
          console.warn("[API] No school years returned");
          $tableBody.html(
            `<tr><td colspan="5" class="text-center text-muted py-3">No academic years found.</td></tr>`
          );
          $pagination.empty();
          return;
        }

        const rows = years.map(item => `
  <tr data-year-id="${item.id}"
      data-start-date="${item.start_date_raw}"
      data-end-date="${item.end_date_raw}">
    <td>${item.name || "—"}</td>
    <td>${item.start_date || "—"}</td>
    <td>${item.end_date || "—"}</td>
    <td class="text-center">
      <button class="btn btn-sm btn-warning btnEditYear"
              data-year-id="${item.id}">
        <i class="fas fa-edit"></i>
      </button>
      <button class="btn btn-sm btn-danger btnDeleteYear"
              data-year-id="${item.id}">
        <i class="fas fa-trash"></i>
      </button>
    </td>
  </tr>
`);

        $tableBody.html(rows.join(""));
        buildPagination(res);
      },
      error: function (xhr) {
        console.error("[API] ❌ AJAX error", xhr.status, xhr.responseText);
        $tableBody.html(
          `<tr><td colspan="5" class="text-center text-danger py-3">Error loading data (${xhr.status})</td></tr>`
        );
        showToastSwal("Failed to fetch academic years.", "error");
      }
    });


  }

  // ------------------------------------------------------------
  // 🔹 Pagination
  // ------------------------------------------------------------
  function buildPagination(res) {
    console.log("[PAGINATION] Building pagination", res);

    $pagination.empty();
    if (!res.previous && !res.next) return;

    let html = `<div class="btn-group">`;
    if (res.previous)
      html += `<button class="btn btn-outline-secondary btn-sm" id="btnPrevPage">← Prev</button>`;
    if (res.next)
      html += `<button class="btn btn-outline-secondary btn-sm" id="btnNextPage">Next →</button>`;
    html += `</div>`;
    $pagination.html(html);

    $("#btnPrevPage").on("click", () => {
      console.log("[PAGINATION] Prev clicked");
      loadSchoolYears(currentSchoolId, res.previous);
    });

    $("#btnNextPage").on("click", () => {
      console.log("[PAGINATION] Next clicked");
      loadSchoolYears(currentSchoolId, res.next);
    });
  }

  // ------------------------------------------------------------
  // 🔄 External reload
  // ------------------------------------------------------------
  window.reloadSchoolYearsForSchool = (schoolId) => {
    console.log("[EXTERNAL] reloadSchoolYearsForSchool:", schoolId);
    loadSchoolYears(schoolId);
  };
}
function openEditSchoolYearModal(yearId) {
  if (!yearId) {
    console.error("[EDIT] Missing yearId");
    return;
  }

  const row = document.querySelector(`tr[data-year-id="${yearId}"]`);
  if (!row) {
    console.error("[EDIT] Row not found for year:", yearId);
    return;
  }

  // 🔹 Populate fields from table row
  document.getElementById("editYearId").value = yearId;
  document.getElementById("editYearName").value =
    row.children[0].innerText.trim();
  document.getElementById("editYearStart").value =
    row.dataset.startDate;   // YYYY-MM-DD
  document.getElementById("editYearEnd").value =
    row.dataset.endDate;     // YYYY-MM-DD


  // 🔹 Open modal (Bootstrap 5 way)
  const editModalEl = document.getElementById("editSchoolYearModal");
  const editModal = bootstrap.Modal.getOrCreateInstance(editModalEl);

  editModal.show();

  console.log("[EDIT] Edit modal opened");
}
