/**
 * Formats a number as currency (USD)
 * @param value - The numeric value to format
 * @returns Formatted currency string
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

/**
 * Formats a number as a percentage
 * @param value - The numeric value to format (e.g., 0.15 for 15%)
 * @returns Formatted percentage string
 */
export function formatPercent(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

/**
 * Determines the tier classification based on a survival score
 * @param score - The survival score (0-100)
 * @returns Tier classification string
 */
export function getTierFromScore(score: number): string {
  if (score >= 80) {
    return 'S';
  } else if (score >= 65) {
    return 'A';
  } else if (score >= 50) {
    return 'B';
  } else if (score >= 35) {
    return 'C';
  } else if (score >= 20) {
    return 'D';
  } else {
    return 'F';
  }
}
