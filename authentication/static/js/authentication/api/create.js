function generateApiKey(data) {
    var accessToken = localStorage.getItem('accessToken'); // Retrieve the access token
    var csrfToken = $('meta[name="csrf-token"]').attr('content'); // Get the CSRF token

    console.log('RECEIVED DATA: ', data);

    $.ajax({
        url: '/api/api-manage/api-keys-generate/', // The endpoint for generating an API key
        type: 'POST', // HTTP method
        data: JSON.stringify(data), // Convert data object to JSON string
        contentType: 'application/json; charset=utf-8', // Content type for JSON
        dataType: 'json', // Expected response type
        headers: {
            'Authorization': 'Bearer ' + accessToken, // Include access token in Authorization header
            'X-CSRFToken': csrfToken // Include CSRF token
        },
        success: function(response) {
            console.log('API Key generated successfully:', response);
            if (response && response.key) {
                success_message(`API Key generated: ${response.key}`); // Display success message
            } else {
                console.warn('No API Key returned in response.');
                success_message('API Key generated successfully, but no key returned.');
            }
            // Trigger the refresh button click after success
            $('#btn_refresh').click();
        },
        error: function(xhr, status, error) {
            console.error('Failed to generate API key:', status, error);

            // Ensure a consistent error response format
            var errorDetails = '';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorDetails = xhr.responseJSON.error;
            } else {
                errorDetails = xhr.responseText || 'An unknown error occurred.';
            }

            console.error('Error details:', errorDetails);
            error_message(`Failed to generate API key:\n${errorDetails}`); // Display error message
        }
    });
}
