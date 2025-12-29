function fetchWithRefresh(url, options = {}) {
    return $.ajax({
        url: url,
        xhrFields: { withCredentials: true },
        ...options
    }).fail(function (xhr) {
        if (xhr.status === 401) {
            console.warn("401 → attempting refresh");

            return $.ajax({
                url: '/api/auth/refresh/',
                method: 'POST',
                xhrFields: { withCredentials: true },
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            }).then(function () {
                // Retry original request
                return $.ajax({
                    url: url,
                    xhrFields: { withCredentials: true },
                    ...options
                });
            }).fail(function () {
                window.location.href = '/accounts/login/';
            });
        }

        if (xhr.status === 403) {
            window.location.href = '/accounts/login/';
        }
    });
}
