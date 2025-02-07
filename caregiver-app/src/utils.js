export function formatCurrency(amount, currency) {
  return new Intl.NumberFormat('en-In', {
    style: 'currency',
    currency: currency,
  }).format(amount);
}

export function longDateFormatter(date) {
  let temp = new Date(date);
  return temp.toLocaleDateString('en-In', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
}

export function shortDateFormatter(date) {
  let temp = new Date(date);
  return temp.toLocaleDateString('en-In', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

export function dayFormatter(date) {
  let temp = new Date(date);
  return temp.toLocaleDateString('en-In', {
    weekday: 'long',
  });
}

export function getAge(dateString) {
  let today = new Date();
  let birthDate = new Date(dateString);
  let age = today.getFullYear() - birthDate.getFullYear();
  let m = today.getMonth() - birthDate.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  return age;
}

export function getCurrentFormattedTime() {
  const now = new Date();
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');

  return `${hours}:${minutes}:${seconds}`;
  // // return statement in case of TaskAccordian
  // return `${hours}:${minutes}`;
}

export function getCurrentFormattedDate() {
  const now = new Date();
  const day = String(now.getDate()).padStart(2, '0');
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const year = now.getFullYear();

  return `${year}-${month}-${day}`;
}

export function formatCurrentDateTime() {
  return `${getCurrentFormattedDate()} ${getCurrentFormattedTime()}`;
}

export function isDateInRange(startTime, endTime) {
  // Convert input format 'YYYY-MM-DD HH:mm:ss' to 'YYYY-MM-DDTHH:mm:ss'
  const formatDateTime = (dateTimeStr) => dateTimeStr.replace(' ', 'T');

  // Create a formatter for IST timezone
  const istFormatter = new Intl.DateTimeFormat('en-US', {
    timeZone: 'Asia/Kolkata',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });

  // Get current time in IST
  const now = new Date();
  const parts = istFormatter.formatToParts(now);

  // Build current IST time from parts
  const currentIST = new Date(
    `${parts.find((p) => p.type === 'year').value}-${parts.find((p) => p.type === 'month').value}-${parts.find((p) => p.type === 'day').value}T${parts.find((p) => p.type === 'hour').value}:${parts.find((p) => p.type === 'minute').value}:${parts.find((p) => p.type === 'second').value}`
  );

  // Convert start and end times to Date objects using the formatted string
  const start = new Date(formatDateTime(startTime));
  const end = new Date(formatDateTime(endTime));

  // Check if current time is within the window
  return currentIST >= start && currentIST <= end;
}
