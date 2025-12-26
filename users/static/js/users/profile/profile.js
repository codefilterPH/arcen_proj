function setProfilePicture(profilePictureSrc, imageElementId, fallbackTextElementId) {
    const img = $("#" + imageElementId);
    const fallbackText = $("#" + fallbackTextElementId);

    //console.log("Setting profile picture...");

    // Set image or fallback text based on whether the profile picture exists
    if (profilePictureSrc) {
        // console.log("Profile picture source found: " + profilePictureSrc);
        img.attr("src", profilePictureSrc).show();
        fallbackText.hide();
    } else {
        //console.log("No profile picture found, showing fallback text.");
        img.hide();
        fallbackText.text("No profile picture uploaded").show();
    }

    // Set image dimensions and fit
    img.css({
        "width": "150px",
        "height": "150px",
        "object-fit": "cover"
    });

    // console.log("Profile picture settings applied: Image size set to 150x150px, object-fit set to cover.");
}

function setSignature(signatureSrc, signatureElementId, fallbackTextElementId) {
    const signatureImg = $("#" + signatureElementId);
    const noSignatureText = $("#" + fallbackTextElementId);

    // console.log("Setting signature...");

    if (signatureSrc) {
        //console.log("Signature found: " + signatureSrc);
        signatureImg.attr("src", signatureSrc).show();
        noSignatureText.hide();
    } else {
        // console.log("No signature found, showing fallback text.");
        signatureImg.hide();
        noSignatureText.show();
    }
}

function getProfile() {
    const accessToken = localStorage.getItem('accessToken');

    $.ajax({
        type: 'GET',
        url: '/api/user-profile/',
        beforeSend: function (xhr) {
            xhr.setRequestHeader('Authorization', 'Bearer ' + accessToken);
        },
        success: function (response) {

            if (!response || !response.results || !response.results.length) {
                console.warn('Empty profile response');
                return;
            }

            const userData = response.results[0];

            if (!userData.is_authenticated) {
                window.location.href = '/accounts/login/';
                return;
            }

            /* =========================
               BASIC PROFILE INFO
            ========================= */

            if ($('#name').length) {
                $('#name').html(`<strong>Full Name:</strong> ${userData.profile_str || '—'}`);
            }

            if ($('#username').length) {
                $('#username').text(userData.username || '—');
            }

            if ($('#position').length) {
                $('#position').html(`<strong>Position:</strong> ${userData.profile.position || '—'}`);
            }

            if ($('#bio').length) {
                $('#bio').text(userData.profile.bio || 'No bio provided');
            }

            if ($('#email').length) {
                $('#email').html(`<strong>Email:</strong> ${userData.email}`);
            }

            if ($('#dateJoined').length) {
                $('#dateJoined').html(`<strong>Joined:</strong> ${userData.date_joined}`);
            }

            /* =========================
               GENDER (SAFE)
            ========================= */
            if ($('#gender').length) {
                const gender = userData.profile.gender_display;
                console.log("GENDER: ", gender);
                let genderText = 'No Gender';

                if (gender === 'M') genderText = 'Male';
                if (gender === 'F') genderText = 'Female';

                $('#gender').html(`<strong>Gender:</strong> ${genderText}`);
            }

            /* =========================
               PROFILE PICTURE
            ========================= */
            setProfilePicture(
                userData.profile.profile_picture,
                'profilePic',
                'noProfilePicText'
            );

            /* =========================
               SIGNATURE
            ========================= */
            setSignature(
                userData.profile.signature,
                'signaturePic',
                'noSignatureText'
            );

            /* =========================
               FAMILY INFO (OPTIONAL / SAFE)
            ========================= */
            const family = userData.profile.family;

            if (family && family.id) {

                if ($('#family_id').length) {
                    $('#family_id').val(family.id);
                }

                if ($('#btnEditFamily').length) {
                    $('#btnEditFamily')
                        .attr('href', `/family/${family.id}/edit/`)
                        .show();
                }

                if ($('#btnCreateFamily').length) {
                    $('#btnCreateFamily').hide();
                }

                if ($('#btnAddMember').length) {
                    $('#btnAddMember')
                        .attr('href', `/family/${family.id}/member/add/`)
                        .show();
                }

                if ($('#containerMember').length) {
                    const memberList = $('#containerMember');
                    memberList.empty();

                    if (Array.isArray(family.members) && family.members.length) {
                        family.members.forEach(member => {
                            const avatar =
                                member.avatar_url ||
                                `/static/img/users/avatars/${member.default_avatar || 'default.png'}`;

                            memberList.append(`
                                <li class="list-group-item d-flex justify-content-between align-items-center">
                                    <div class="d-flex align-items-center">
                                        <img src="${avatar}" class="rounded-circle me-2" width="40" height="40">
                                        <div>
                                            <strong>${member.full_name}</strong><br>
                                            <small class="text-muted">${member.role || '—'}</small>
                                        </div>
                                    </div>
                                </li>
                            `);
                        });
                    } else {
                        memberList.html(
                            `<li class="list-group-item text-center text-muted">
                                No family members found.
                             </li>`
                        );
                    }
                }

            } else {
                if ($('#containerMember').length) {
                    $('#containerMember').html(
                        `<li class="list-group-item text-center text-muted">
                            No family created yet.
                         </li>`
                    );
                }

                if ($('#btnEditFamily').length) $('#btnEditFamily').hide();
                if ($('#btnCreateFamily').length) $('#btnCreateFamily').show();
                if ($('#btnAddMember').length) $('#btnAddMember').hide();
            }
        },
        error: function (xhr) {
            console.error('Profile load failed:', xhr);
            error_message('Failed to load profile');
        }
    });
}
