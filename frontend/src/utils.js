export function formatCurrency(amount, currency) {
    return new Intl.NumberFormat('en-In', {style: 'currency', currency: currency}).format(amount)
}