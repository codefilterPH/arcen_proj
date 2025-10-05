// Trigger Delete Action
function DeleteApiKey(apiKeyId) {
    var accessToken = localStorage.getItem('accessToken'); // Retrieve the access token
    var csrfToken = $('meta[name="csrf-token"]').attr('content'); // Get the CSRF token

    // Use the question_message function for confirmation
    question_message('Are you sure you want to delete this API key?').then((result) => {
        // If the user clicked "Continue"
        if (result.isConfirmed) {
            $.ajax({
                url: `/api/api-manage/${apiKeyId}/api-keys-delete/`,  // API DELETE URL
                type: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Authorization': 'Bearer ' + accessToken
                },
                success: function(response) {
                    if (response) {
                        success_message(response.message);
                    }
                    $('#btn_refresh').click(); // Refresh button click event
                },
                error: function(xhr, status, error) {
                    Swal.fire('Error!', 'An error occurred while deleting the API Key.', 'error');
                }
            });
        } else {
            console.log("API key deletion canceled by the user.");
        }
    });

}