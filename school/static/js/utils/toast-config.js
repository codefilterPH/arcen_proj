// Function to show toast notification
function showToast(message, type) {
  var toastContainer = document.getElementById('toast-container');

  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    toastContainer.style.zIndex = 9999;
    document.body.appendChild(toastContainer);
  }

  var toast = document.createElement('div');
  toast.classList.add('toast', 'align-items-center', 'text-white', 'bg-' + type, 'border-0');
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'assertive');
  toast.setAttribute('aria-atomic', 'true');

  var toastHeader = document.createElement('div');
  toastHeader.classList.add('d-flex', 'justify-content-between', 'align-items-center', 'p-2');

  var toastTitle = document.createElement('strong');
  toastTitle.classList.add('me-auto');
  toastTitle.textContent = 'Notification';

  var closeButton = document.createElement('button');
  closeButton.setAttribute('type', 'button');
  closeButton.classList.add('btn-close', 'btn-close-white', 'me-2', 'm-auto');
  closeButton.setAttribute('data-bs-dismiss', 'toast');
  closeButton.setAttribute('aria-label', 'Close');

  toastHeader.appendChild(toastTitle);
  toastHeader.appendChild(closeButton);

  var toastBody = document.createElement('div');
  toastBody.classList.add('toast-body');
  toastBody.textContent = message;

  toast.appendChild(toastHeader);
  toast.appendChild(toastBody);

  toastContainer.appendChild(toast);

  var toastElement = new bootstrap.Toast(toast, {
    delay: 5000,
    animation: true,
  });

  toastElement.show();

  toast.addEventListener('hidden.bs.toast', function () {
    toast.remove();
  });
}