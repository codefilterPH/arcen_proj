function error_message(message, showCancelButton = false) {
  return Swal.fire({
    title: 'Error',
    text: message,
    icon: 'error',
    confirmButtonText: 'Continue',
    showCancelButton: showCancelButton,
    cancelButtonText: 'Cancel',
    customClass: { popup: 'swal-highest-z' },
    didOpen: (popup) => {
      popup.style.zIndex = 99999;
      const backdrop = document.querySelector('.swal2-container');
      if (backdrop) backdrop.style.zIndex = 99998;
    }
  });
}

function success_message(title = 'Success', message, showCancelButton = false) {
  return Swal.fire({
    title: title,
    text: message,
    icon: 'success',
    confirmButtonText: 'Continue',
    showCancelButton: showCancelButton,
    cancelButtonText: 'Cancel',
    customClass: { popup: 'swal-highest-z' },
    didOpen: (popup) => {
      popup.style.zIndex = 99999;
      const backdrop = document.querySelector('.swal2-container');
      if (backdrop) backdrop.style.zIndex = 99998;
    }
  });
}

function question_message(message, showCancelButton = true, callback) {
  return Swal.fire({
    title: 'Question',
    text: message,
    icon: 'question',
    showCancelButton: showCancelButton,
    confirmButtonText: 'Continue',
    cancelButtonText: 'Cancel',
    customClass: { popup: 'swal-highest-z' },
    didOpen: (popup) => {
      popup.style.zIndex = 99999;
      const backdrop = document.querySelector('.swal2-container');
      if (backdrop) backdrop.style.zIndex = 99998;
    }
  }).then(callback);
}

function stop_message(message, showCancelButton = false) {
  return Swal.fire({
    title: 'Stop',
    text: message,
    icon: 'warning',
    confirmButtonText: 'Ok',
    showCancelButton: showCancelButton,
    cancelButtonText: 'Cancel',
    customClass: { popup: 'swal-highest-z' },
    didOpen: (popup) => {
      popup.style.zIndex = 99999;
      const backdrop = document.querySelector('.swal2-container');
      if (backdrop) backdrop.style.zIndex = 99998;
    }
  });
}

function showToastSwal(message, icon = 'error') {
  const validIcons = ['success', 'error', 'warning', 'info', 'question'];
  const iconMap = {
    danger: 'error',
    primary: 'info',
    secondary: 'info',
    dark: 'info',
    light: 'info'
  };

  if (!validIcons.includes(icon)) {
    icon = iconMap[icon] || 'info';
  }

  Swal.fire({
    toast: true,
    icon: icon,
    title: message,
    position: 'bottom-end',
    showConfirmButton: false,
    timer: 3000,
    timerProgressBar: true,
    customClass: { popup: 'swal-toast-zindex' },
    didOpen: (toast) => {
      toast.style.zIndex = 99999; // 🔝 Force toast above everything
    }
  });
}
