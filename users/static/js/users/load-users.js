function initializeUsersData() {
    console.log('Initializing Users data to table.');

    users_table = $('#usersTable').DataTable({
        responsive: true,
        serverSide: true,
        processing: true,   // ✅ enable spinner
        ajax: {
            url: '/api/users/get-users/',
            type: 'GET',
            xhrFields: {
                withCredentials: true   // ✅ send HttpOnly cookies
            },
            beforeSend: function(xhr) {
                var csrfToken = $('meta[name="csrf-token"]').attr('content');
                if (csrfToken) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            },
            dataSrc: function (json) {
                console.log('AJAX Response:', json);
                return json.data;
            },
            complete: function () {
                Pace.stop();
            },
        },
        columns: [
            { // Avatar
                data: 'profile_picture',
                title: "Avatar",
                render: function(data) {
                    return data
                        ? `<img src="${data}" alt="Profile Picture"
                                 style="width: 50px; height: 50px; border-radius: 50%;"
                                 onerror="this.onerror=null; this.src='/static/img/users/img_holder.png';">`
                        : `<img src="/static/img/users/img_holder.png" alt="No Profile"
                                 style="width: 50px; height: 50px; border-radius: 50%;">`;
                }
            },
            { // QR
                data: 'qr_code',
                title: "QR CODE",
                render: function(data) {
                    return data
                        ? `<img src="${data}" alt="QR CODE"
                                style="width: 50px; height: 50px; border-radius: 50%;">`
                        : `<img src="/static/img/users/img_holder.png" alt="No QR"
                                style="width: 50px; height: 50px; border-radius: 50%;">`;
                }
            },
            { data: 'fullname', title: "Full Name" },
            { // Active
                data: 'is_active',
                title: "Active Status",
                render: function(data) {
                    return data ? '<span class="badge bg-success">Active</span>'
                                : '<span class="badge bg-danger">Inactive</span>';
                }
            },
            { // Roles
                data: 'groups',
                title: "Roles",
                render: function(data) {
                    return Array.isArray(data) && data.length > 0 ? data.join(', ') : 'No roles';
                }
            },
            { data: 'organization_names', title: "Member of" },
            { // Last Active
                data: 'last_activity',
                title: "Last Active",
                render: function(data) {
                    return data ? new Date(data).toLocaleString() : 'Never';
                }
            },
            { // Actions
                data: null,
                title: "Actions",
                orderable: false,
                render: function(data, type, row) {
                    return `
                        <div class="btn-group" role="group">
                            <a href="/users/${row.user.id}/edit/" class="btn btn-sm btn-primary" title="Edit"><i class="fas fa-edit"></i></a>
                            <a href="/manage-users/${row.user.id}/activate/" class="btn btn-sm btn-success" title="Activate"><i class="fas fa-check-circle"></i></a>
                            <a href="/users/${row.user.id}/deactivate/" class="btn btn-sm btn-secondary" title="Deactivate"><i class="fas fa-ban"></i></a>
                            <a href="/users/${row.user.id}/unit/reset-password/" class="btn btn-sm btn-warning" title="Reset Password"><i class="fas fa-key"></i></a>
                            <a href="/users/${row.user.id}/assign-groups/" class="btn btn-sm btn-info" title="Add Role"><i class="fas fa-user-plus"></i></a>
                        </div>`;
                }
            }
        ],
        order: [[2, 'asc']], // ✅ Full Name
        columnDefs: [
            { targets: 0, width: '60px' },   // Avatar
            { targets: 1, width: '60px' },   // QR
            { targets: 2, width: '200px' },  // Full Name
            { targets: 3, width: '120px' },  // Active Status
            { targets: 4, width: '180px' },  // Roles
            { targets: 5, width: '200px' },  // Member of
            { targets: 6, width: '150px' },  // Last Active
            { targets: 7, width: '220px' }   // Actions
        ]
    });

    // Refresh button
    $('#btnRefreshUsers').off('click').on('click', function () {
        if ($.fn.DataTable.isDataTable('#usersTable')) {
            users_table.destroy();
            $('#usersTable tbody').empty();
        }
        initializeUsersData();
        console.log('Reloading table');
    });
}
