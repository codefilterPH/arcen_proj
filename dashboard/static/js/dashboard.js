function initAttendanceChart(present, absent) {
  const ctx = document.getElementById('attendanceChart');

  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['Present', 'Absent'],
      datasets: [{
        label: 'Attendance',
        data: [present, absent],
        backgroundColor: ['#28a745', '#dc3545'],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  });
}
