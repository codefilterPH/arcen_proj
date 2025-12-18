let userData = null;

function getUserProfile() {
    fetchWithRefresh('/api/user-profile/me/', {
        type: 'GET',
        contentType: 'application/json'
    }).done(function(response) {
        console.log('GET PROFILE RESPONSE: ', response);

        if (!response || response.error || response.is_authenticated === false) {
            console.warn("User not authenticated → redirecting.");
            window.location.href = '/accounts/login/';
            return;
        }

        userData = response;

        // ✅ Full name display
        if (userData.profile && userData.profile.fullname) {
            $('#userFullName').text(userData.profile.fullname);
            $('#sidebarName').text(userData.profile.fullname);
        }

        // ✅ Profile picture
        if (userData.profile && userData.profile.profile_picture) {
            $('#userProfilePicture')
                .attr('src', userData.profile.profile_picture)
                .attr('alt', userData.profile.fullname + "'s profile picture");

            $('#userProfilePictureChild')
                .attr('src', userData.profile.profile_picture)
                .attr('alt', userData.profile.fullname + "'s profile picture");
        } else {
            // fallback
            $('#userProfilePicture').attr('src', '/static/img/users/img_holder.png');
            $('#userProfilePictureChild').attr('src', '/static/img/users/img_holder.png');
        }

        // ✅ Show/hide elements by role/group
        revealElementsByGroup(userData);
    }).fail(function(xhr) {
        console.error("Profile fetch failed:", xhr.status, xhr.responseText);
        if (xhr.status === 401) {
            // Refresh failed → force login
            window.location.href = '/accounts/login/';
        } else {
            error_message('An error occurred while fetching profile.');
        }
    });
}
