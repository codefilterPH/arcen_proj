$(document).ready(function () {
    $('#profilePicUpload').change(function (event) {
        event.preventDefault(); // Prevent default behavior, if applicable

        // Retrieve file and tokens
        const file = event.target.files[0];
        var csrfToken = $('meta[name="csrf-token"]').attr('content');
        var accessToken = localStorage.getItem('accessToken');

        // Validate file type
        const validTypes = ['image/jpeg', 'image/png', 'image/svg+xml'];
        if (!file || !validTypes.includes(file.type)) {
            error_message('Please upload a valid image file (JPG, PNG, or SVG).');
            return;
        }

        // Prepare the FormData
        const formData = new FormData();
        formData.append('profile_picture', file);

        // Start loader (optional)
        Pace.restart();

        // Perform the AJAX request
        $.ajax({
            url: '/api/user-profile/upload-profile-picture/', // Update this endpoint as needed
            type: 'POST',
            beforeSend: function (xhr) {
                // Set CSRF and Authorization headers
                if (csrfToken) xhr.setRequestHeader('X-CSRFToken', csrfToken);
                if (accessToken) xhr.setRequestHeader('Authorization', 'Bearer ' + accessToken);
            },
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                // Handle successful response
                const imageUrl = response.profile_picture_url; // Adjust based on API response
                $('#profilePic').attr('src', imageUrl);
                success_message('Profile picture updated successfully!', 'Your new profile picture has been uploaded.');
            },
            error: function (xhr, status, error) {
                console.error('Error uploading profile picture:', xhr);

                // Handle validation or server-side errors
                if (xhr.status === 400) {
                    const errors = xhr.responseJSON || {};
                    for (const field in errors) {
                        const inputField = $(`#${field}`);
                        inputField.addClass('is-invalid');
                        inputField.after(`<div class="error-message text-danger">${errors[field][0]}</div>`);
                    }
                } else {
                    const errorMessage = xhr.responseJSON?.detail || 'An error occurred while uploading.';
                    error_message(errorMessage);
                }
            },
            complete: function () {
                // Stop loader (optional)
                Pace.stop();
            }
        });
    });
});
