function getSchoolProfile(slug) {
    const $modal = $('#schoolProfileModal');
    const $logo  = $('#schoolLogoPreview');

    // Reset UI
    $modal.find('.school-name').text('Loading…');
    $modal.find('.school-address').text('—');
    $modal.find('.school-slug').text('—');
    $modal.find('.school-created').text('—');
    $modal.find('.school-updated').text('—');

    // Reset image
    $logo
        .off('error')
        .attr('src', '/static/img/no_logo.png');

    fetchWithRefresh(`/api/schools/by-slug/${slug}/`, {
        type: 'GET',
        contentType: 'application/json'
    })
    .done(function (school) {

        $modal.find('.school-name').text(school.name);
        $modal.find('.school-address').text(
            school.address || 'Address not provided'
        );
        $modal.find('.school-slug').text(school.slug);
        $modal.find('.school-created').text(formatDate(school.created_at));
        $modal.find('.school-updated').text(formatDate(school.updated_at));

        if (!school.logo) {
            return;
        }

        const img = document.getElementById('schoolLogoPreview');
        if (!img) {
            return;
        }

        // Normalize image URL (no cache busting)
        let logoUrl = school.logo;

        if (logoUrl.startsWith('media/')) {
            logoUrl = '/' + logoUrl;
        }

        if (!logoUrl.startsWith('http')) {
            logoUrl = window.location.origin + logoUrl;
        }

        img.removeAttribute('src');
        img.src = logoUrl;
    })
    .fail(function (xhr) {
        error_message('Failed to load school profile.');
    });
}

function formatDate(dateStr) {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleString();
}
