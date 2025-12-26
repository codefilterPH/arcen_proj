/* =====================================================
   Helpers
===================================================== */

/**
 * Gmail-only validator
 */
function validateGmail(email) {
  if (!email) return false;
  return /^[a-zA-Z0-9._%+-]+@gmail\.com$/i.test(email.trim());
}

/**
 * Normalize PH phone numbers
 * Accepts:
 *   09XXXXXXXXX   → +639XXXXXXXXX
 *   +639XXXXXXXXX → stays
 */
function normalizePHPhone(raw) {
  if (!raw) return null;

  let phone = raw.replace(/[^\d+]/g, '');

  if (/^09\d{9}$/.test(phone)) {
    return '+63' + phone.substring(1);
  }

  if (/^\+639\d{9}$/.test(phone)) {
    return phone;
  }

  return null;
}

/**
 * Mark input invalid with message
 */
function markInvalid(id, message) {
  const $input = $('#' + id);
  if ($input.length) {
    $input.addClass('is-invalid');
    $input.after(
      `<div class="error-message text-danger small">${message}</div>`
    );
  }
}

/* =====================================================
   Update Profile
===================================================== */

function updateUserData() {
  const csrfToken = $('meta[name="csrf-token"]').attr('content');
  const accessToken = localStorage.getItem('accessToken');

  let hasError = false;

  // Reset previous errors
  $('#updateProfileForm .is-invalid').removeClass('is-invalid');
  $('#updateProfileForm .error-message').remove();

  /* ===============================
     Required fields
  =============================== */
  ['first_name_edit', 'last_name_edit', 'email_edit'].forEach(id => {
    const $input = $('#' + id);
    if (!$input.val().trim()) {
      markInvalid(id, 'This field is required.');
      hasError = true;
    }
  });

  /* ===============================
     Gmail validation
  =============================== */
  const emailVal = $('#email_edit').val().trim();
  if (emailVal && !validateGmail(emailVal)) {
    markInvalid('email_edit', 'Gmail address only (@gmail.com).');
    hasError = true;
  }

  /* ===============================
     Phone validation + normalize
  =============================== */
  const normalizedPhone = normalizePHPhone(
    $('#contact_number_edit').val()
  );

  if (!normalizedPhone) {
    markInvalid(
      'contact_number_edit',
      'Use 09XXXXXXXXX or +639XXXXXXXXX'
    );
    hasError = true;
  } else {
    $('#contact_number_edit').val(normalizedPhone);
  }

  if (hasError) {
    showToastSwal('Please check the highlighted fields.', 'error');
    return;
  }

  /* ===============================
     Payload
  =============================== */
  const formData = {
    user: {
      first_name: $('#first_name_edit').val(),
      last_name: $('#last_name_edit').val(),
      email: $('#email_edit').val(),
    },

    middle_name: $('#middle_name_edit').val(),
    preferred_initial: $('#preferred_initial_edit').val(),
    extension_name: $('#extension_name_edit').val(),
    rank: $('#rank_edit').val(),
    sub_svc: $('#sub_svc_edit').val(),
    position: $('#position_edit').val(),
    gender: $('#gender_edit').val(),
    birth_date: $('#birth_date_edit').val(),
    contact_number: normalizedPhone,
    bio: $('#bio_edit').val(),
    display_name_format: $('#display_name_format_edit').val(),

    classification_id: $('#classification_edit').val() || null,
    organizations: $('#organizations_edit').val() || [],
    designation_ids: $('#designations_edit').val() || [],
  };

  console.log('🚀 Submitting profile update:', formData);

  /* ===============================
     AJAX
  =============================== */
  $.ajax({
    type: 'POST',
    url: '/api/user-profile/update-profile/',
    headers: {
      Authorization: 'Bearer ' + accessToken,
      'X-CSRFToken': csrfToken,
      'Content-Type': 'application/json',
    },
    data: JSON.stringify(formData),

    success: function (response) {
      console.log('✅ Profile updated:', response);
      showToastSwal('Profile updated successfully!', 'success');

      // Refresh preview
      if (typeof getProfile === 'function') {
        getProfile();
      }

      // Switch back to preview mode
      $('#profileEditColumn').addClass('d-none');
      $('#profileViewColumn').removeClass('d-none');
    },

    error: function (xhr) {
      console.error('❌ Error updating profile:', xhr);

      if (xhr.status === 400 && xhr.responseJSON) {
        const errors = xhr.responseJSON;

        // Profile-level errors
        for (const field in errors) {
          if (field === 'user') continue;
          const message = Array.isArray(errors[field])
            ? errors[field][0]
            : errors[field];
          markInvalid(field + '_edit', message);
        }

        // Nested user errors
        if (errors.user) {
          for (const field in errors.user) {
            const message = Array.isArray(errors.user[field])
              ? errors.user[field][0]
              : errors.user[field];
            markInvalid(field + '_edit', message);
          }
        }

        showToastSwal('Please check the highlighted fields.', 'error');
      } else {
        showToastSwal(
          'Something went wrong while updating your profile.',
          'error'
        );
      }
    },
  });
}

/* =====================================================
   Bind submit
===================================================== */
$(document).on('submit', '#updateProfileForm', function (e) {
  e.preventDefault();
  updateUserData();
});
