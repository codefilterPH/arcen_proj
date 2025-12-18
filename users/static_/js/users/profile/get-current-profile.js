function loadOrganizations(selectedIds = []) {
  $.ajax({
    url: '/api/organizations/',
    type: 'GET',
    headers: authHeaders(),
    success: function (data) {
      let $orgSelect = $('#organizations');
      $orgSelect.empty();

      let orgs = data.results || data;

      // Add placeholder
      $orgSelect.append(new Option('-- Select Organization(s) --', '', false, false));

      orgs.forEach(org => {
        $orgSelect.append(new Option(org.name, org.id));
      });

      if (selectedIds && selectedIds.length > 0) {
        $orgSelect.val(selectedIds).trigger('change');
      }

      if ($orgSelect.hasClass('select2')) {
        $orgSelect.select2({
          placeholder: "Select organization(s)",
          allowClear: true,
          width: '100%'
        });
      }
    },
    error: function (xhr) {
      console.error('❌ Failed to load organizations:', xhr.responseText || xhr.statusText);
    }
  });
}

function loadDesignations(selectedIds = []) {
  $.ajax({
    url: '/api/designations/',
    type: 'GET',
    headers: authHeaders(),
    success: function (data) {
      let $desigSelect = $('#designations');
      $desigSelect.empty();

      let designations = data.results || data;

      designations.forEach(d => {
        $desigSelect.append(new Option(d.name, d.id));
      });

      if (selectedIds && selectedIds.length > 0) {
        $desigSelect.val(selectedIds).trigger('change');
      }

      if ($desigSelect.hasClass('select2')) {
        $desigSelect.select2({
          placeholder: "Select designation(s)",
          allowClear: true,
          width: '100%'
        });
      }
    },
    error: function (xhr) {
      console.error('❌ Failed to load designations:', xhr.responseText || xhr.statusText);
    }
  });
}

function loadClassifications(selectedId = null) {
  $.ajax({
    url: '/api/classifications/',
    type: 'GET',
    headers: authHeaders(),
    success: function (data) {
      let $classSelect = $('#classification');
      $classSelect.empty();

      let classifications = data.results || data;

      // Add placeholder
      $classSelect.append(new Option('-- Select Classification --', '', false, false));

      classifications.forEach(c => {
        $classSelect.append(new Option(c.name, c.id));
      });

      if (selectedId) {
        $classSelect.val(selectedId).trigger('change');
      }

      if ($classSelect.hasClass('select2')) {
        $classSelect.select2({
          placeholder: "Select classification",
          allowClear: true,
          width: '100%'
        });
      }
    },
    error: function (xhr) {
      console.error('❌ Failed to load classifications:', xhr.responseText || xhr.statusText);
    }
  });
}

function populateGenderDropdown(currentGender) {
  var genderSelect = $('#gender');
  genderSelect.empty();

  var genderChoices = [
    { value: 'M', label: 'Male' },
    { value: 'F', label: 'Female' },
    { value: 'O', label: 'Other' },
    { value: 'N', label: 'Non-binary' },
    { value: 'X', label: 'Prefer not to say' },
  ];

  $.each(genderChoices, function(index, choice) {
    var option = new Option(choice.label, choice.value, false, choice.value === currentGender);
    genderSelect.append(option);
  });
}

function getUserData() {
  var accessToken = localStorage.getItem('accessToken');

  $.ajax({
    type: 'GET',
    url: '/api/user-profile/me/',
    beforeSend: function(xhr) {
      xhr.setRequestHeader('Authorization', 'Bearer ' + accessToken);
    },
    success: function(response) {
      // Fill basic fields
      $('#first_name').val(response.first_name);
      $('#last_name').val(response.last_name);
      $('#email').val(response.email);  // ✅ Added Email preload
      $('#preferred_initial').val(response.profile.preferred_initial);
      $('#middle_name').val(response.profile.middle_name);
      $('#extension_name').val(response.profile.extension_name);
      $('#rank').val(response.profile.rank);
      $('#sub_svc').val(response.profile.sub_svc);
      $('#position').val(response.profile.position);
      $('#bio').val(response.profile.bio);
      $('#contact_number').val(response.profile.contact_number);
      $('#birth_date').val(response.profile.birth_date);

      // Gender
      populateGenderDropdown(response.profile.gender);

      // ✅ Organizations
      loadOrganizations(response.profile.organization_ids);

      // ✅ Designations → map IDs
      let designationIds = (response.profile.designations || []).map(d => d.id || d);
      loadDesignations(designationIds);

      // ✅ Classification → single object or ID
      let classificationId = response.profile.classification?.id || response.profile.classification || null;
      loadClassifications(classificationId);
    },
    error: function(response) {
      console.error('Error fetching user profile data:', response);
    }
  });
}
