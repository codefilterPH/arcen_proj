function error_message(message, showCancelButton = false) {
    return Swal.fire({
        title: 'Error',
        text: message,
        icon: 'error',
        confirmButtonText: 'Continue',
        showCancelButton: showCancelButton,
        cancelButtonText: 'Cancel'
    });
}

function success_message(title = 'Success', message, showCancelButton = false) {
    return Swal.fire({
        title: title,
        text: message,
        icon: 'success',
        confirmButtonText: 'Continue',
        showCancelButton: showCancelButton,
        cancelButtonText: 'Cancel'
    });
}

function warning_message(message, showCancelButton = false) {
    return Swal.fire({
        title: 'Warning',
        text: message,
        icon: 'warning',
        confirmButtonText: 'Ok',
        showCancelButton: showCancelButton,
        cancelButtonText: 'Cancel'
    });
}

function info_message(message, showCancelButton = false) {
    return Swal.fire({
        title: 'Information',
        text: message,
        icon: 'info',
        confirmButtonText: 'Got it',
        showCancelButton: showCancelButton,
        cancelButtonText: 'Cancel'
    });
}

function question_message(message, callback, showCancelButton = true) {
    Swal.fire({
        title: 'Question',
        text: message,
        icon: 'question',
        showCancelButton: showCancelButton,
        confirmButtonText: 'Continue',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (callback) {
            callback(result.isConfirmed);
        }
    });
}

function stop_message(message, showCancelButton = false) {
    return Swal.fire({
        title: 'Stop',
        text: message,
        icon: 'warning',
        confirmButtonText: 'Ok',
        showCancelButton: showCancelButton,
        cancelButtonText: 'Cancel'
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
        position: 'bottom-end', // 👈 Bottom right corner
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true
    });
}

/* SAMPLE USAGE
error_message('Something went wrong!');
success_message('Data saved successfully!');
warning_message('This action is irreversible!');
info_message('New update available.');
question_message('Are you sure you want to continue?', (result) => {
    if (result) {
        console.log('User clicked Continue');
    } else {
        console.log('User clicked Cancel');
    }
});
stop_message('You are not allowed to proceed!');
*/
