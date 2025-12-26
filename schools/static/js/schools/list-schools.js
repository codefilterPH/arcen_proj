// Load and render schools
function loadSchools(page = 1, search = "") {
    fetchWithRefresh(`/api/schools/?page=${page}&search=${encodeURIComponent(search)}`, {
        type: "GET",
        contentType: "application/json"
    }).done(function(response) {
        console.log("Schools:", response);

        let $grid = $("#schoolsGrid");
        $grid.empty();

        if (!response.results || response.results.length === 0) {
            $grid.append(`<p class="text-muted">No schools found.</p>`);
            $("#schoolsPagination").empty();
            return;
        }

        // Render cards
        response.results.forEach(school => {
            let logo = school.logo_url ? school.logo_url : "/static/img/img_holder.png";
            let card = `
              <div class="col-md-4 mb-4 school-card" data-name="${school.name.toLowerCase()}" data-archived="false">
                <div class="card shadow-sm h-100">
                  <div class="card-body d-flex flex-column justify-content-between">
                    <div class="d-flex justify-content-center align-items-center mb-3" style="height:100px;">
                      <img src="${logo}" alt="${school.name}" style="max-height:80px;"
                           onerror="this.onerror=null;this.src='/static/img/img_holder.png';">
                    </div>
                    <h5 class="text-dark text-center">${school.name}</h5>
                    <p class="text-muted text-center">${school.address || "No address provided."}</p>
                    <div class="row g-2 mt-3">
                      <div class="col-6 col-sm-3">
                        <button
                           class="btn btn-sm btn-info w-100 btn-profile"
                           //<a href="/schools/${school.slug}/profile/"
                           data-slug="${school.slug}"
                           data-bs-toggle="modal"
                           data-bs-target="#schoolProfileModal"
                           title="Profile">
                          <i class="fas fa-id-badge"></i>
                        </button>
                      </div>

                      <!-- 🧑‍🎓 Students Button -->
                          <div class="col-6 col-sm-3">
                            <a href="#"
                               class="btn btn-sm btn-primary w-100 btn-students"
                               title="View Students"
                               data-bs-toggle="modal"
                               data-bs-target="#studentsModal"
                               data-school-id="${school.id}"
                               data-school-name="${school.name}">
                              <i class="fas fa-user-graduate"></i>
                            </a>
                      </div>

                      <div class="col-6 col-sm-3">
                          <a href="#"
                             class="btn btn-sm btn-dark w-100 text-white"
                             title="Manage Academic Year"
                             data-school-id="${school.id}"
                             data-school-name="${school.name}"
                             data-bs-toggle="modal"
                             data-bs-target="#schoolYearModal">
                            <i class="fas fa-calendar-alt"></i>
                          </a>
                      </div>

                      <div class="col-6 col-sm-3">
                          <a class="btn btn-sm btn-success w-100 btn-metric"
                             title="Metrics"
                             data-bs-toggle="modal"
                             data-bs-target="#attendanceDashboardModal"
                             data-school="${school.name}"
                             data-year="2024–2025">
                            <i class="fas fa-chart-bar"></i>
                          </a>
                      </div>

                      <div class="col-6 col-sm-3">
                        <a href="#"
                           class="btn btn-sm btn-warning w-100 text-white btn-edit-school"
                           title="Edit School"
                           data-bs-toggle="modal"
                           data-bs-target="#editSchoolModal"
                           data-id="${school.id}"
                           data-name="${school.name}"
                           data-address="${school.address || ''}"
                           data-logo="${school.logo || ''}">
                          <i class="fas fa-edit"></i>
                        </a>
                      </div>
                      <div class="col-6 col-sm-3">
                          <a href="#" class="btn btn-sm btn-danger w-100 text-white"
                               title="Delete"
                               onclick="deleteSchool(${school.id}, '${school.name}')">
                              <i class="fas fa-trash"></i>
                          </a>
                      </div>

                    </div>
                  </div>
                </div>
              </div>
            `;

            $grid.append(card);
        });

        // Render pagination
        renderPagination(response.count, page, search);
    }).fail(function(xhr) {
        console.error("Error loading schools:", xhr.responseText);
        error_message("Failed to load schools.");
    });
}

// Pagination renderer
function renderPagination(total, currentPage, search) {
    let pageSize = 6; // same as backend
    let totalPages = Math.ceil(total / pageSize);

    let $pagination = $("#schoolsPagination");
    $pagination.empty();

    if (totalPages <= 1) return;

    for (let i = 1; i <= totalPages; i++) {
        let activeClass = i === currentPage ? "active" : "";
        $pagination.append(`
            <li class="page-item ${activeClass}">
                <a class="page-link" href="#" data-page="${i}" data-search="${search}">${i}</a>
            </li>
        `);
    }

    // Pagination click
    $pagination.find("a").on("click", function(e) {
        e.preventDefault();
        let page = parseInt($(this).data("page"));
        let search = $(this).data("search");
        loadSchools(page, search);
    });
}


