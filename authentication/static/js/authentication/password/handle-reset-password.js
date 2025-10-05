function handleResetPassword() {
  const newPassword = $('#new_password').val().trim();
  const confirmPassword = $('#confirm_password').val().trim();
  const uid = new URLSearchParams(window.location.search).get('uid');
  const token = new URLSearchParams(window.location.search).get('token');  // optional if you want to include it
  const csrfToken = $('meta[name="csrf-token"]').attr('content');

  if (!newPassword || !confirmPassword) {
    showToast("All password fields are required.", "danger");
    return;
  }

  if (newPassword !== confirmPassword) {
    showToast("Passwords do not match.", "danger");
    return;
  }

  console.log("Resetting password for UID:", uid);

  $.ajax({
    url: '/api/password-reset/reset/',
    type: 'POST',
    contentType: 'application/json',
    beforeSend: function (xhr) {
      if (csrfToken) {
        xhr.setRequestHeader('X-CSRFToken', csrfToken);
      }
    },
    data: JSON.stringify({
      uid: uid,
      new_password: newPassword,
      confirm_password: confirmPassword
    }),
    success: function (response) {
      console.log("✅ Password reset successful:", response);
      showToast("Your password has been updated successfully!", "success");

      // Optionally redirect after success
      setTimeout(function () {
        window.location.href = '/accounts/login/';
      }, 2000);
    },
    error: function (xhr) {
      const errorResponse = xhr.responseJSON;
      let messages = [];

      if (errorResponse) {
        if (errorResponse.detail) messages.push(errorResponse.detail);
        if (errorResponse.error) messages.push(errorResponse.error);
        if (errorResponse.new_password) messages.push("Password: " + errorResponse.new_password);
        if (errorResponse.confirm_password) messages.push("Confirm: " + errorResponse.confirm_password);
      }

      if (messages.length > 0) {
        showToast(messages.join("\n"), "danger");
      } else {
        showToast("An unexpected error occurred. Please try again.", "danger");
      }
    }
  });
}
