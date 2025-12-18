
function loadUsers(page = 1) {
    if (hasLoadedUsers) {
        console.log('🔹 Users already loaded, skipping fetch.');
        return;  // Skip loading if users have already been loaded
    }

    $('#spinnerParticipant').show();
    $('#participantSelect').hide();
    $('#participantMessage').text('');

    fetchWithRefresh(`/api/users-list/?page=${page}&page_size=50`, {
        type: 'GET',
        contentType: 'application/json'
    })
    .done(function(response) {
        console.log('🔹 USERS LOADED:', response);

        const data = response.results || [];

        if (data.length === 0) {
            $('#participantMessage')
                .removeClass('text-danger')
                .addClass('text-warning')
                .text('⚠️ No users found.');
            $('#participantSelect').empty();
            return;
        }

        // Populate the dropdown
        const $dropdown = $('#participantSelect');
        $dropdown.empty();
        $dropdown.append('<option value="">-- Select User --</option>');

        data.forEach(function(user) {
            $dropdown.append(
                $('<option>', { value: user.id }).text(user.full_name)
            );
        });

        // Mark users as loaded
        hasLoadedUsers = true;

        // Optionally, you can show a success message here if needed
        // $('#participantMessage').text('✅ Users loaded successfully.');
    })
    .fail(function(xhr) {
        console.error('❌ Load users failed:', xhr.status, xhr.responseText);
        $('#participantMessage')
            .removeClass('text-warning')
            .addClass('text-danger')
            .text('❌ Failed to fetch users. Please try again later.');
    })
    .always(function() {
        $('#spinnerParticipant').hide();
        $('#participantSelect').show();
    });
}
