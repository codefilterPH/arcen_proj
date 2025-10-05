function initializeApiKeys() {
    console.log('Initializing API keys data to table.');
    let apiKeyTable;
    var accessToken = localStorage.getItem('accessToken');
    var csrfToken = $('meta[name="csrf-token"]').attr('content');
    var url = `/api/api-manage/api-keys-list/?is_active=true`;
    console.log('URL: ', url);

    // Define the DataTable
    apiKeyTable = $('#apiKeyTable').DataTable({
        responsive: true,
        serverSide: true,
        processing: true,
        ajax: {
            url: url,
            type: 'GET',
            beforeSend: function (xhr) {
                // Show loading spinner before making the Ajax request
                Pace.restart(); // Show the loading icon before the request is sent
                xhr.setRequestHeader('X-CSRFToken', csrfToken);
                xhr.setRequestHeader('Authorization', 'Bearer ' + accessToken);
            },
            complete: function () {
                // Hide loading spinner after the Ajax request is complete
                Pace.stop();
            },
        },
        columns: [
            { data: 'name', title: "Name", className: 'text-left' },
            { data: 'key', title: "Key", className: 'text-left' },
            { data: 'is_active', title: "Active", className: 'text-center',
                render: function (data) {
                    return data ? 'Yes' : 'No';
                }
            },
            { data: 'expires_at', title: "Expires At", className: 'text-center' },
            { data: 'allowed_ip_address', title: "Allowed IP Address", className: 'text-center' },
            { data: 'allowed_domain', title: "Allowed Domain", className: 'text-center' },
            {
                data: 'actions',
                orderable: false,
                render: function (data, type, row) {
                    // Define the HTML for the action buttons
                    var editButton = `
                        <a href="/auth/api-manage/${row.id}/update/" type="button" class="btn btn-sm btn-info edit-btn mr-1" data-id="${row.id}">
                            <i class="fas fa-edit"></i> Update
                        </a>
                    `;

                    var deleteButton = `
                        <button type="button" id="btnAPIDelete" class="btn btn-sm btn-danger delete-btn mr-1" data-id="${row.id}">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    `;

                    var copyButton = `
                        <button type="button" id="btnAPICopy" class="btn btn-sm btn-secondary copy-btn" data-key="${row.key}" title="Copy API Key">
                            <i class="fas fa-copy"></i> Copy
                        </button>
                    `;

                    // Always show buttons to the user
                    return `<div class="btn-group" style="white-space:nowrap">
                        ${editButton} ${deleteButton} ${copyButton}
                    </div>`;
                }
            }
        ],
        order: [[0, 'desc']],
        language: {
            emptyTable: "No API keys available. Please check back later."
        },
    });

    // Trigger DataTable reinitialization when the button is clicked
    $('#btn_refresh').off('click').on('click', function () {
        if ($.fn.DataTable.isDataTable('#apiKeyTable')) {
            apiKeyTable.destroy(); // Destroy the current instance of DataTable
            $('#apiKeyTable tbody').empty();
        }
        initializeApiKeys(); // Reinitialize and assign it back
        console.log('Reloading table');
    });

    // Add click event for copy button
    $('#apiKeyTable').on('click', '.copy-btn', function () {
        var apiKey = $(this).data('key');
        navigator.clipboard.writeText(apiKey).then(() => {
            success_message('API key copied to clipboard!');
        }).catch(err => {
            console.error('Could not copy text: ', err);
        });
    });
}
