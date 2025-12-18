// load-school-years.js
window.currentSchoolId = null; // 🌍 Global scope for active school ID

function initGetSchoolYear(options = {}) {
  const modalSelector = options.modalSelector || "#schoolYearModal";
  const tableSelector = options.tableSelector || "#schoolYearTable";
  const paginationSelector = options.paginationSelector || "#paginationContainer";

  const $modal = $(modalSelector);
  const $table = $(tableSelector);
  const $tableBody = $(`${tableSelector} tbody`);
  const $pagination = $(paginationSelector);

  let currentSchoolId = null;
  let searchTimeout = null;

  // ------------------------------------------------------------
  // 🟦 When modal opens
  // ------------------------------------------------------------
  $modal.on("show.bs.modal", function (event) {
    const button = event.relatedTarget; // The button that triggered the modal
    let schoolId = null;
    let schoolName = "School";

    if (button) {
      // ✅ Retrieve data attributes from the clicked button
      schoolId = $(button).data("school-id");
      schoolName = $(button).data("school-name") || "School";
    }

    if (!schoolId) {
      // 🧩 Try to reuse last known ID
      if (window.currentSchoolId) {
        console.warn("[SCHOOL YEAR] No trigger button found — reusing cached school ID:", window.currentSchoolId);
        schoolId = window.currentSchoolId;
        schoolName = "Current School";
      } else {
        showToastSwal("Missing school ID when opening modal.", "error");
        $tableBody.html(`<tr><td colspan="5" class="text-center text-danger py-3">Missing school ID.</td></tr>`);
        return;
      }
    }


    // ✅ Store globally
    window.currentSchoolId = schoolId;
    currentSchoolId = schoolId;

    // Update modal title
    $("#schoolYearModalLabel").text(`School Year Management — ${schoolName}`);

    // Load data
    loadSchoolYears(currentSchoolId);
  });

  // 🔄 Refresh button
  $("#btnRefreshSchoolYear").on("click", function () {
    if (currentSchoolId) loadSchoolYears(currentSchoolId);
    else showToastSwal("No school selected to refresh.", "error");
  });

  // 🔍 Live Search (with debounce)
  $("#filterSchoolYearSearch").on("keyup", function () {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      if (currentSchoolId) loadSchoolYears(currentSchoolId);
    }, 400);
  });

  // ------------------------------------------------------------
  // 🔹 Load School Years from API
  // ------------------------------------------------------------
  function loadSchoolYears(schoolId, url = null) {
    if (!schoolId) {
      showToastSwal("Missing school ID when loading data.", "error");
      return;
    }

    const search = $("#filterSchoolYearSearch").val() || "";
    const endpoint = url || `/api/academic-years/${schoolId}/school-years/?search=${encodeURIComponent(search)}`;

    $tableBody.html(`<tr><td colspan="5" class="text-center py-3 text-muted">Loading...</td></tr>`);

    $.ajax({
      url: endpoint,
      method: "GET",
      headers: authHeaders(), // ✅ global token helper
      success: function (res) {
        const years = res.results || res;
        if (!years.length) {
          $tableBody.html(`<tr><td colspan="5" class="text-center text-muted py-3">No academic years found.</td></tr>`);
          $pagination.empty();
          return;
        }

        const rows = years.map(item => `
          <tr data-year-id="${item.id}">
            <td>${item.name || "—"}</td>
            <td>${item.start_date || "—"}</td>
            <td>${item.end_date || "—"}</td>
            <td class="text-center">
              <button
                class="btn btn-sm btn-warning btnEditYear me-1"
                title="Edit Academic Year"
                data-bs-toggle="modal"
                data-bs-target="#editSchoolYearModal"
                data-year-id="${item.id}"
                data-year-name="${item.name || ""}"
                data-year-start="${item.start_date || ""}"
                data-year-end="${item.end_date || ""}">
                <i class="fas fa-edit"></i>
              </button>

              <button
                class="btn btn-sm btn-danger btnDeleteYear"
                title="Delete Academic Year"
                data-year-id="${item.id}"
                data-year-name="${item.name || ""}">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        `);

        $tableBody.html(rows.join(""));
        buildPagination(res);
      },
      error: function (xhr) {
        console.error("❌ Error fetching school years:", xhr);
        $tableBody.html(`<tr><td colspan="5" class="text-center text-danger py-3">Error loading data (${xhr.status})</td></tr>`);
        showToastSwal("Failed to fetch academic years. Please try again.", "error");
      }
    });
  }

  // ------------------------------------------------------------
  // 🔹 Pagination Controls
  // ------------------------------------------------------------
  function buildPagination(res) {
    $pagination.empty();
    if (!res.previous && !res.next) return;

    let html = `<div class="btn-group">`;
    if (res.previous) html += `<button class="btn btn-outline-secondary btn-sm" id="btnPrevPage">← Prev</button>`;
    if (res.next) html += `<button class="btn btn-outline-secondary btn-sm" id="btnNextPage">Next →</button>`;
    html += `</div>`;
    $pagination.html(html);

    $("#btnPrevPage").on("click", () => loadSchoolYears(currentSchoolId, res.previous));
    $("#btnNextPage").on("click", () => loadSchoolYears(currentSchoolId, res.next));
  }

  // ------------------------------------------------------------
  // 🔄 External trigger (reload from outside)
  // ------------------------------------------------------------
  window.reloadSchoolYearsForSchool = (schoolId) => loadSchoolYears(schoolId);
}
