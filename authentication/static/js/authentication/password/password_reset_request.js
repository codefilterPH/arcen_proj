function handleSendEmail() {
    const username = $('#id_username').val().trim();
    const email = $('#id_email').val().trim();
    const csrfToken = $('meta[name="csrf-token"]').attr('content');
    // var accessToken = localStorage.getItem('accessToken');


    if (!username) {
        $('#usernameError').text('Username is required.').show();
        $('#id_username').addClass('invalid-input');
        return;
    }

    if (!email || !/^[a-zA-Z0-9._%+-]+@gmail\.com$/.test(email)) {
        $('#emailError').text('Only a valid Gmail address is allowed.').show();
        $('#id_email').addClass('invalid-input');
        return;
    }

    console.log("Sending password reset request for:", username, email);

    $.ajax({
        url: '/api/password-reset/request/',
        type: 'POST',
        contentType: 'application/json',
        beforeSend: function (xhr) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
            // xhr.setRequestHeader('Authorization', 'Bearer ' + accessToken);
        },
        data: JSON.stringify({ username: username, email: email }),
        success: function (response) {
            console.log('✅ Reset email sent:', response);
            showToast("Password reset email sent. Please check your inbox.", "success");
        },
        error: function (xhr) {
            const errorResponse = xhr.responseJSON;
            let messages = [];

            if (errorResponse) {
                if (errorResponse.detail) messages.push(errorResponse.detail);
                if (errorResponse.error) messages.push(errorResponse.error);
                if (errorResponse.username) messages.push("Username: " + errorResponse.username);
                if (errorResponse.email) messages.push("Email: " + errorResponse.email);
            }

            if (messages.length > 0) {
                showToast(messages.join("\n"), "danger");
            } else {
                showToast("An unexpected error occurred. Please try again.", "danger");
            }
        }
    });
}
