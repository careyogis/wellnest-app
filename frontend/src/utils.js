export function formatCurrency(amount, currency) {
  return new Intl.NumberFormat('en-In', {
    style: 'currency',
    currency: currency,
  }).format(amount)
}

export function dateFormatter(date) {
  let temp = new Date(date)
  return temp.toLocaleDateString('en-In', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}
