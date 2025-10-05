// Function to log out the user (cookie-based, no localStorage)
function logoutUser() {
    var csrfToken = $('meta[name="csrf-token"]').attr('content');

    $.ajax({
        url: '/api/auth/logout/',  // Django logout API endpoint
        type: 'POST',
        contentType: 'application/json',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        },
        // ✅ No need to send refresh token — backend reads from cookie
        data: JSON.stringify({}),
        success: function(response) {
            console.log('✅ Logged out successfully:', response);

            // No tokens in localStorage anymore → just redirect
            window.location.href = '/';
        },
        error: function(xhr, textStatus, errorThrown) {
            console.error('❌ Error during logout:', xhr.responseText || errorThrown);
        }
    });
}
