function authHeaders() {
  const accessToken = localStorage.getItem('accessToken');
  const csrfToken =
    $('meta[name="csrf-token"]').attr('content') ||
    $('meta[name="csrfmiddlewaretoken"]').attr('content') ||
    (document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)')?.pop()
      ? decodeURIComponent(RegExp.$2)
      : null);

  const headers = { 'X-Requested-With': 'XMLHttpRequest' };
  if (accessToken) headers['Authorization'] = `Bearer ${accessToken}`;
  if (csrfToken)   headers['X-CSRFToken']   = csrfToken;
  return headers;
}
