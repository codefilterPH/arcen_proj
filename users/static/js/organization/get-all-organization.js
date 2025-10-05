function loadOrganizations() {
  $.ajax({
    url: '/api/organizations/',
    type: 'GET',
    headers: authHeaders(),
    success: function (data) {
      let $orgSelect = $('#organizations');
      $orgSelect.empty(); // clear existing

      // If paginated, use data.results, else use data
      let orgs = data.results || data;

      orgs.forEach(org => {
        $orgSelect.append(new Option(org.name, org.id));
      });

      // Re-init Select2 if needed
      if ($orgSelect.hasClass('select2')) {
        $orgSelect.trigger('change');
      }
    },
    error: function (xhr) {
      console.error('❌ Failed to load organizations:', xhr.responseText || xhr.statusText);
    }
  });
}
