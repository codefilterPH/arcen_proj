function saveParticipants() {
    // 🧠 Validate selected participants
    if (selectedParticipants.length === 0) {
        $('#participantMessage')
            .removeClass('text-warning')
            .addClass('text-danger')
            .text('⚠️ No participants to save.');
        return;
    }

    // 🏫 Get school ID from modal
    const schoolId = $('#addParticipantModal').data('school-id');
    console.log('💾 Saving participants for school ID:', schoolId);

    if (!schoolId) {
        showToast('⚠️ No school selected.', 'danger');
        return;
    }

    // 🎓 Extract user IDs only
    const userIds = selectedParticipants.map(p => parseInt(p.id));

    // 🧱 Prepare payload
    const payload = JSON.stringify({
        school_id: schoolId,
        user_ids: userIds
    });

    // 🚀 Send API request
    $.ajax({
        url: '/api/students/add-bulk/',
        method: 'POST',
        headers: {
            ...authHeaders(), // ✅ merge your global auth + csrf headers
            'Content-Type': 'application/json'
        },
        data: payload,
        success: function (response) {
            console.log('✅ Server Response:', response);

            const created = response.created_count || 0;
            const skipped = response.skipped?.length || 0;

            showToast(
                `✅ ${created} students added. ${skipped > 0 ? skipped + ' skipped.' : ''}`,
                'success'
            );

            // 🔄 Reset and close modal
            selectedParticipants = [];
            $('#participantsTable tbody').empty();
            $('#participantSelect').val('').trigger('change');

        },
        error: function (xhr) {
            console.error('❌ Failed to save participants:', xhr.responseJSON || xhr);

            if (xhr.status === 403) {
                showToast('🚫 Forbidden — Please log in again.', 'danger');
            } else if (xhr.status === 400) {
                showToast('⚠️ Invalid data provided.', 'warning');
            } else {
                showToast('❌ Failed to save participants.', 'danger');
            }
        }
    });
}
