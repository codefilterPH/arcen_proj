// ===============================
// Available Students (Select2 AJAX)
// ===============================

function initAvailableStudentsSelect() {
    const schoolId = window.currentSchoolId;

    if (!schoolId) return;

    const $select = $('#participantSelect');

    // Destroy previous instance safely
    if ($select.hasClass('select2-hidden-accessible')) {
        $select.select2('destroy');
    }

    $select.select2({
        theme: 'bootstrap-5',
        dropdownParent: $('#addParticipantModal'), // REQUIRED for modals
        placeholder: 'Search student...',
        allowClear: true,
        width: '100%',
        minimumInputLength: 1,

        ajax: {
            url: `/api/students/schools/${schoolId}/available/`,
            dataType: 'json',
            delay: 300,
            headers: authHeaders(),

            data: function (params) {
                return {
                    search: params.term || '',
                    page: params.page || 1,
                    page_size: 10
                };
            },

            processResults: function (data, params) {
                params.page = params.page || 1;

                return {
                    results: data.results.map(u => ({
                        id: u.id,
                        text: u.full_name || u.username
                    })),
                    pagination: {
                        more: Boolean(data.next)
                    }
                };
            },

            cache: true
        }
    });
}
