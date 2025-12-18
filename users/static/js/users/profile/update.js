function updateUserData() {
  const csrfToken = $('meta[name="csrf-token"]').attr('content');
  const accessToken = localStorage.getItem('accessToken');

  const formData = {
    // ✅ Nest under "user" since serializer expects it
    user: {
      first_name: $('#first_name').val(),
      last_name: $('#last_name').val(),
      email: $('#email').val(),   // 👈 Added email
    },

    // Profile fields
    middle_name: $('#middle_name').val(),
    preferred_initial: $('#preferred_initial').val(),
    extension_name: $('#extension_name').val(),
    rank: $('#rank').val(),
    sub_svc: $('#sub_svc').val(),
    position: $('#position').val(),
    gender: $('#gender').val(),
    birth_date: $('#birth_date').val(),
    contact_number: $('#contact_number').val(),
    bio: $('#bio').val(),
    display_name_format: $('#display_name_format').val(),

    // ✅ Match serializer’s writable fields
    classification_id: $('#classification').val() || null,
    organizations: $('#organizations').val() || [],
    designation_ids: $('#designations').val() || [],
  };

  console.log("🚀 Submitting profile update:", formData);

  $.ajax({
    type: 'POST',
    url: '/api/user-profile/update-profile/',
    headers: {
      "Authorization": "Bearer " + accessToken,
      "X-CSRFToken": csrfToken,
      "Content-Type": "application/json"
    },
    data: JSON.stringify(formData),
    success: function(response) {
      console.log("✅ Profile updated:", response);
      showToastSwal("Profile updated successfully!", "success");
      setTimeout(() => window.location.href = "/profile/", 1000);
    },
    error: function(xhr) {
      console.error("❌ Error updating profile:", xhr);
      if (xhr.status === 400 && xhr.responseJSON) {
        $('#updateProfileForm .is-invalid').removeClass('is-invalid');
        $('#updateProfileForm .error-message').remove();
        const errors = xhr.responseJSON;
        for (const field in errors) {
          const $input = $(`#${field}`);
          if ($input.length) {
            $input.addClass("is-invalid");
            $input.after(`<div class="error-message text-danger">${errors[field][0]}</div>`);
          }
        }
        showToastSwal("Please check the highlighted fields.", "error");
      } else {
        showToastSwal("Something went wrong while updating your profile.", "error");
      }
    }
  });
}
