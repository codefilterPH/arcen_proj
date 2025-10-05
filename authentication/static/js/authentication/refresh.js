function fetchWithRefresh(url, options = {}) {
    return $.ajax({
        url: url,
        xhrFields: { withCredentials: true },
        ...options
    }).fail(function(xhr) {
        // Handle expired session or forbidden
        if (xhr.status === 401 || xhr.status === 403) {
            console.warn(`Access ${xhr.status} → refreshing or redirecting...`);

            // Attempt token refresh only if it's a 401 (Unauthorized)
            if (xhr.status === 401) {
                return $.post({
                    url: '/api/auth/refresh/',
                    xhrFields: { withCredentials: true }
                }).then(() => {
                    // Retry the original request after refresh
                    return $.ajax({
                        url: url,
                        xhrFields: { withCredentials: true },
                        ...options
                    });
                }).fail(() => {
                    // Refresh failed → force login
                    window.location.href = '/accounts/login/';
                });
            } else {
                // 403 → no permission or expired session, go to login
                window.location.href = '/accounts/login/';
            }
        }
    });
}
