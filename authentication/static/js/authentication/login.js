function authenticateUser(username, password, remember_me) {
    console.log("Proceeding to user authentication");
    console.log("Username:", username);

    var csrfToken = $('meta[name="csrf-token"]').attr('content');

    $.ajax({
        url: '/api/auth/login/',   // Your login endpoint
        type: 'POST',
        contentType: 'application/json',
        xhrFields: { withCredentials: true }, // ✅ allow cookies from server
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        },
        data: JSON.stringify({
            username: username,
            password: password,
            remember_me: remember_me,
        }),
        success: function(response) {
            console.log("✅ Login successful");
            // ✅ No tokens saved manually, backend sets HttpOnly cookies
            window.location.href = '/';
        },
        error: function(xhr) {
            console.error("❌ Login failed:", xhr);
            var errorResponse = xhr.responseJSON;
            if (errorResponse) {
                var messages = [];

                if (errorResponse.detail) messages.push(errorResponse.detail);
                if (errorResponse.error) messages.push(errorResponse.error);
                if (errorResponse.username) messages.push(errorResponse.username);
                if (errorResponse.password) messages.push(errorResponse.password);

                if (messages.length > 0) {
                    error_message(messages.join('<br>'));
                } else {
                    error_message('An unexpected error occurred. Please try again.');
                }
            } else {
                error_message('An unexpected error occurred. Please try again.');
            }
        }
    });
}
