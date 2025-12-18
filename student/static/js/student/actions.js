// =====================================================
// actions.js — Handles Add Participant Modal behavior
// =====================================================

// Global array to store selected participants
let selectedParticipants = [];
let hasLoadedUsers = false;
let previousModal = null; // track the previous modal (studentsModal)

// 🟦 When "Add Student" button (in Students Modal) is clicked
$(document).on("click", "#btnAddStudent", function () {
  const schoolId = $(this).data("school-id");
  const schoolName = $(this).data("school-name") || "School";

  console.log("🎓 Opening Add Participant Modal for School ID:", schoolId);

  // Remember the Students Modal (so we can reopen it later)
  previousModal = $("#studentsModal");

  // Attach data to Add Participant Modal
  $("#addParticipantModal")
    .data("school-id", schoolId)
    .data("school-name", schoolName);

  // Update header
  $("#addParticipantModalLabel").text(`Add Student — ${schoolName}`);

  // Hide previous modal first, then show Add Participant modal
  previousModal.modal("hide");
  $("#addParticipantModal").modal("show");
});

// 🟨 When Add Participant Modal is shown
$("#addParticipantModal").on("shown.bs.modal", function () {
  const schoolId = $(this).data("school-id");
  console.log("📘 Add Participant Modal - School ID:", schoolId);

  // 🔹 Reset loading state each time a new school opens the modal
  hasLoadedUsers = false;

  // Load users specific to this school
  loadUsersForSchool(schoolId);
});

// 🟥 When Add Participant Modal closes, reopen Students Modal
$("#addParticipantModal").on("hidden.bs.modal", function () {
  const schoolId = $(this).data("school-id");
  console.log("🚪 Closed Add Participant Modal — returning to Students Modal for ID:", schoolId);

  if (previousModal && previousModal.length) {
    previousModal.modal("show");
  }
});

// 🔹 Add user to table
$(document).on("click", "#btnAddToTable", function () {
  const userId = $("#participantSelect").val();
  const userName = $("#participantSelect option:selected").text();

  if (!userId) {
    $("#participantMessage")
      .removeClass("text-warning")
      .addClass("text-danger")
      .text("⚠️ Please select a user to add.");
    return;
  }

  // prevent duplicates
  const exists = selectedParticipants.some((p) => p.id === userId);
  if (exists) {
    $("#participantMessage")
      .removeClass("text-danger")
      .addClass("text-warning")
      .text("⚠️ This user is already added.");
    return;
  }

  // add new participant
  selectedParticipants.push({ id: userId, name: userName });
  const rowCount = $("#participantsTable tbody tr").length + 1;

  const newRow = `
    <tr data-id="${userId}">
      <td class="text-center">${rowCount}</td>
      <td>${userName}</td>
      <td class="text-center">
        <button class="btn btn-sm btn-danger btnRemoveParticipant">
          <i class="fas fa-trash"></i>
        </button>
      </td>
    </tr>
  `;

  $("#participantsTable tbody").append(newRow);
  $("#participantMessage").text("");
  console.log(`✅ Added: ${userName}`);
});

// 🔹 Remove user from table
$(document).on("click", ".btnRemoveParticipant", function () {
  const $row = $(this).closest("tr");
  const userId = $row.data("id");

  selectedParticipants = selectedParticipants.filter((p) => p.id !== String(userId));
  $row.remove();

  // reorder numbering
  $("#participantsTable tbody tr").each(function (index) {
    $(this).find("td:first").text(index + 1);
  });

  console.log(`🗑️ Removed participant ID: ${userId}`);
});

// 🔹 Save all participants (calls global saveParticipants from add-students.js)
$(document).on("click", "#btnSaveAllParticipants", function () {
  console.log("💾 Saving all participants...");
  saveParticipants();
});


// =====================================================
// 🏫 Load users specific to a school
// =====================================================
function loadUsersForSchool(schoolId, page = 1) {
  if (hasLoadedUsers) {
    console.log("🔹 Users already loaded for this school, skipping fetch.");
    return;
  }

  if (!schoolId) {
    console.warn("⚠️ Missing school ID — cannot load users.");
    $("#participantMessage")
      .removeClass("text-warning")
      .addClass("text-danger")
      .text("⚠️ No school selected. Cannot load users.");
    return;
  }

  console.log(`📡 Loading users for school ID ${schoolId}...`);

  $("#spinnerParticipant").show();
  $("#participantSelect").hide();
  $("#participantMessage").text("");

  fetchWithRefresh(`/api/users-list/?school_id=${schoolId}&page=${page}&page_size=50`, {
    type: "GET",
    contentType: "application/json",
  })
    .done(function (response) {
      console.log("🔹 USERS LOADED:", response);

      const data = response.results || [];

      if (data.length === 0) {
        $("#participantMessage")
          .removeClass("text-danger")
          .addClass("text-warning")
          .text("⚠️ No users found for this school.");
        $("#participantSelect").empty();
        return;
      }

      // Populate dropdown
      const $dropdown = $("#participantSelect");
      $dropdown.empty();
      $dropdown.append('<option value="">-- Select User --</option>');

      data.forEach(function (user) {
        $dropdown.append(
          $("<option>", { value: user.id }).text(user.full_name)
        );
      });

      hasLoadedUsers = true;
    })
    .fail(function (xhr) {
      console.error("❌ Load users failed:", xhr.status, xhr.responseText);
      $("#participantMessage")
        .removeClass("text-warning")
        .addClass("text-danger")
        .text("❌ Failed to fetch users. Please try again later.");
    })
    .always(function () {
      $("#spinnerParticipant").hide();
      $("#participantSelect").show();
    });
}

// ------------------------------------------------------------
// 🔹 Remove a Student (click handler with SweetAlert confirmation)
// ------------------------------------------------------------
$(document).on("click", ".btnRemoveStudent", function () {
    const $row = $(this).closest("tr");
    const studentId = $row.data("student-id");   // ✅ define it here
    const schoolId = window.currentSchoolId;     // ✅ global from load-students.js

    if (!studentId || !schoolId) {
        showToastSwal("⚠️ Missing student or school ID.", "error");
        return;
    }

    // 🧠 SweetAlert2 confirmation dialog
    question_message("Are you sure you want to remove this student?", function (isConfirmed) {
        if (isConfirmed) {
            removeStudent(studentId, schoolId, $row);  // ✅ call your removal function
        }
    });
});

