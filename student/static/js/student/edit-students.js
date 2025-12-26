/**
 * Safely trim strings.
 * Returns empty string for non-strings (null, undefined, arrays, objects).
 */
function safeTrim(val) {
  return typeof val === "string" ? val.trim() : "";
}

/**
 * Clear all validation errors in the form
 */
function clearFormErrors($form) {
  $form.find(".is-invalid").removeClass("is-invalid");
  $form.find(".invalid-feedback").remove();
}

/**
 * Mark a field as invalid with a message
 */
function markInvalid(fieldId, message) {
  const $field = $("#" + fieldId);
  if (!$field.length) return;

  $field.addClass("is-invalid");

  if (!$field.next(".invalid-feedback").length) {
    $field.after(
      `<div class="invalid-feedback">${message}</div>`
    );
  }
}

/**
 * Fields that are REQUIRED to submit the form
 * key = input/select id
 * value = error message
 */
const REQUIRED_FIELDS = {
  first_name: "First name is required.",
  last_name: "Last name is required.",
};

function validateRequiredFields(payload, $form) {
  let hasError = false;

  Object.entries(REQUIRED_FIELDS).forEach(([fieldId, message]) => {
    const value = payload[fieldId];

    if (!value) {
      markInvalid(fieldId, message);
      hasError = true;
    }
  });

  if (hasError) {
    showToastSwal("Please fill in all required fields.", "error");
    scrollToFirstError($form);
  }

  return !hasError;
}

/**
 * Scroll to first invalid field
 */
function scrollToFirstError($form) {
  const $first = $form.find(".is-invalid").first();
  if ($first.length) {
    $first[0].scrollIntoView({ behavior: "smooth", block: "center" });
    $first.focus();
  }
}

function updateStudentProfile() {
  if (!window.currentStudentId) {
    console.error("No student selected.");
    return;
  }

  const $form = $("#editStudentForm");
  const $submitBtn = $form.find("button.btn-primary");

  if ($submitBtn.prop("disabled")) return;

  clearFormErrors($form);

  const payload = {
    enrollment_status: $("#enrollment_status").val(),
    is_active: $("#is_active").val() === "true",

    first_name: safeTrim($("#first_name").val()),
    last_name: safeTrim($("#last_name").val()),
    email: safeTrim($("#student_email").val()),

    middle_name: safeTrim($("#middle_name").val()) || null,
    preferred_initial: safeTrim($("#preferred_initial").val()) || null,
    extension_name: safeTrim($("#extension_name").val()) || null,

    gender: $("#gender").val() || null,
    birth_date: $("#birth_date").val() || null,
    contact_number: safeTrim($("#contact_number").val()) || null,

    classification: $("#classification").val() || null,
    designations: $("#designations").val() || [],
    display_name_format: $("#display_name_format").val(),
  };


  /* =========================
     CLIENT-SIDE REQUIRED CHECKS
  ========================= */
  let hasError = false;

  if (!payload.first_name) {
    markInvalid("first_name", "First name is required.");
    hasError = true;
  }

  if (!payload.last_name) {
    markInvalid("last_name", "Last name is required.");
    hasError = true;
  }

  if (hasError) {
    showToastSwal("Please fix the highlighted fields.", "error");
    scrollToFirstError($form);
    return;
  }

  console.log("PAYLOAD: ", payload);

  const endpoint = `/api/students/update-student-profile/${window.currentStudentId}/`;

  $submitBtn.prop("disabled", true).addClass("disabled");

  $.ajax({
    url: endpoint,
    method: "PATCH",
    headers: {
      ...authHeaders(),
      "Content-Type": "application/json",
    },
    data: JSON.stringify(payload),

    success: function () {
      showToastSwal("Student profile updated successfully.", "success");
    },

    error: function (xhr) {
      clearFormErrors($form);

      if (xhr.responseJSON) {
        /*
         DRF ERROR FORMAT HANDLING
         Example:
         {
           "first_name": ["This field is required."],
           "email": ["Enter a valid email."]
         }
        */
        Object.entries(xhr.responseJSON).forEach(([field, messages]) => {
          const message = Array.isArray(messages)
            ? messages[0]
            : messages;

          // Map serializer field → input id (same names here)
          markInvalid(field, message);
        });

        showToastSwal("Please fix the highlighted fields.", "error");
        scrollToFirstError($form);
      } else {
        showToastSwal("Failed to update student profile.", "error");
      }
    },

    complete: function () {
      $submitBtn.prop("disabled", false).removeClass("disabled");
    },
  });
}
