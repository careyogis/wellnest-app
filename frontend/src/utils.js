export function formatCurrency(amount, currency) {
  return new Intl.NumberFormat('en-In', {
    style: 'currency',
    currency: currency,
  }).format(amount)
}

export function longDateFormatter(date) {
  let temp = new Date(date)
  return temp.toLocaleDateString('en-In', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

export function shortDateFormatter(date) {
  let temp = new Date(date)
  return temp.toLocaleDateString('en-In', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export function dayFormatter(date) {
  let temp = new Date(date)
  return temp.toLocaleDateString('en-In', {
    weekday: 'long',
  })
}

export function getAge(dateString) {
  let today = new Date()
  let birthDate = new Date(dateString)
  let age = today.getFullYear() - birthDate.getFullYear()
  let m = today.getMonth() - birthDate.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  return age
}
