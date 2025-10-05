function setProfilePicture(profilePictureSrc, imageElementId, fallbackTextElementId) {
    const img = $("#" + imageElementId);
    const fallbackText = $("#" + fallbackTextElementId);

    console.log("Setting profile picture...");

    // Set image or fallback text based on whether the profile picture exists
    if (profilePictureSrc) {
        console.log("Profile picture source found: " + profilePictureSrc);
        img.attr("src", profilePictureSrc).show();
        fallbackText.hide();
    } else {
        console.log("No profile picture found, showing fallback text.");
        img.hide();
        fallbackText.text("No profile picture uploaded").show();
    }

    // Set image dimensions and fit
    img.css({
        "width": "150px",
        "height": "150px",
        "object-fit": "cover"
    });

    console.log("Profile picture settings applied: Image size set to 150x150px, object-fit set to cover.");
}

function setSignature(signatureSrc, signatureElementId, fallbackTextElementId) {
    const signatureImg = $("#" + signatureElementId);
    const noSignatureText = $("#" + fallbackTextElementId);

    console.log("Setting signature...");

    if (signatureSrc) {
        console.log("Signature found: " + signatureSrc);
        signatureImg.attr("src", signatureSrc).show();
        noSignatureText.hide();
    } else {
        console.log("No signature found, showing fallback text.");
        signatureImg.hide();
        noSignatureText.show();
    }
}

function getProfile() {
    var accessToken = localStorage.getItem('accessToken');
    console.log("Access token fetched from localStorage: " + accessToken);

    $.ajax({
        type: 'GET',
        url: '/api/user-profile/',  // Ensure this URL is correct
        beforeSend: function(xhr) {
            xhr.setRequestHeader('Authorization', 'Bearer ' + accessToken);
            console.log("Authorization header set: Bearer " + accessToken);
        },
        success: function(response) {
            console.log('GET PROFILE RESPONSE: ', response);

            // Check if response contains the user data
            if (response.length > 0) {
                const userData = response.results[0];
                console.log('USER DATA: ', userData);

                if (userData.is_authenticated === true) {
                    $("#name").html("<strong>Full Name:</strong> " + (userData.profile_str || "Not provided"));
                    $("#preferred_initial").html("<strong>Preferred Initial:</strong> " + (userData.profile.preferred_initial_display || "Not provided"));
                    $("#username").html(userData.username || "No username");
                    $("#position").html(userData.profile.position || "No position");
                    $("#bio").html(userData.profile.bio || "No bio provided");

                    // Gender logic
                    $("#gender").html(function() {
                        const genderText = userData.profile.gender_display;
                        console.log("Gender text: ", genderText);

                        if (genderText === 'M' || genderText === 'm') {
                            return "<strong>Gender:</strong> Male";
                        } else if (genderText === 'F' || genderText === 'f') {
                            return "<strong>Gender:</strong> Female";
                        } else {
                            return "<strong>Gender:</strong> No Gender";
                        }
                    });

                    $("#email").html("<strong>Email:</strong> " + userData.email);
                    $("#dateJoined").html("<strong>Joined:</strong> " + userData.date_joined);

                    // Profile Picture
                    const profilePictureSrc = userData.profile.profile_picture;
                    console.log('Profile picture path: ', profilePictureSrc);
                    setProfilePicture(profilePictureSrc, "profilePic", "noProfilePicText");

                    // Signature
                    const signature = userData.profile.signature;
                    console.log('Signature: ', signature);
                    setSignature(signature, "signaturePic", "noSignatureText");

                    // Family Information
                    const family = userData.profile.family;
                    console.log('Family data: ', family);
                    const memberList = $("#containerMember");
                    const addMemberBtn = $("#btnAddMember");

                    if (family && family.id) {
                        console.log('Family ID found: ' + family.id);
                        $('#family_id').val(family.id);

                        // Set the edit button's href dynamically
                        const editUrl = `/family/${family.id}/edit/`;
                        $('#btnEditFamily').attr('href', editUrl).show();
                        $('#btnCreateFamily').hide();

                        // Show Add Member button
                        const addMemberUrl = `/family/${family.id}/member/add/`;
                        addMemberBtn.attr('href', addMemberUrl).show();

                        // Fill in the family info table
                        $(".card-body table tbody").html(`
                            <tr><th scope="row">Family Name</th><td>${family.name || '—'}</td></tr>
                            <tr><th scope="row">Description</th><td>${family.description || '—'}</td></tr>
                            <tr><th scope="row">Created By</th><td>${family.is_owner ? 'You' : 'Not Available'}</td></tr>
                            <tr><th scope="row">Created At</th><td>${family.created_at || '—'}</td></tr>
                        `);

                        // Populate member list
                        memberList.empty();
                        if (Array.isArray(family.members) && family.members.length > 0) {
                            family.members.forEach(member => {
                                const avatarUrl = member.avatar_url || `/static/img/users/avatars/${member.default_avatar || 'default.png'}`;
                                memberList.append(`
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        <div class="d-flex align-items-center">
                                            <img src="${avatarUrl}" class="rounded-circle me-3 mr-1" alt="Avatar" width="40" height="40">
                                            <div>
                                                <strong>${member.full_name}</strong><br>
                                                <small class="text-muted">${member.role || 'No role'}</small>
                                            </div>
                                        </div>
                                        <div class="d-flex gap-1">
                                            <a href="/family/member/${member.id}/edit/" class="btn btn-sm btn-outline-primary mr-1" title="Edit Member">
                                                <i class="fas fa-edit"></i>
                                            </a>
                                            <form method="post" action="/family/member/${member.id}/remove/">{% csrf_token %}
                                                <button type="submit" class="btn btn-sm btn-outline-danger" title="Remove Member">
                                                    <i class="fas fa-user-minus"></i>
                                                </button>
                                            </form>
                                        </div>
                                    </li>
                                `);
                            });
                        } else {
                            memberList.html(`<li class="list-group-item text-center text-muted">No family members found.</li>`);
                        }

                    } else {
                        console.log('No family found, showing default message.');
                        // No family
                        $('#btnEditFamily').hide();
                        $('#btnCreateFamily').show();
                        addMemberBtn.hide();

                        memberList.html(`<li class="list-group-item text-center text-muted">No family created yet.</li>`);
                        $(".card-body table tbody").html(`
                            <tr><th scope="row" colspan="2" class="text-center text-muted">No family data available</th></tr>
                        `);
                    }

                } else {
                    console.log("User not authenticated.");
                    $('#page-top').html('<p>User is not authenticated</p>');
                }
            } else {
                console.log('Invalid response format or empty data.');
                $('#page-top').html('<p>Invalid response format or empty data</p>');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error fetching user profile data:', error);

            if (xhr.responseJSON && xhr.responseJSON.detail) {
                error_message(xhr.responseJSON.detail);
            } else {
                error_message("An unknown error occurred.");
            }
        }
    });
}
