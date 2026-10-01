/**
 * String similarity and matching algorithms for field-by-field comparison
 */

/**
 * Calculates Levenshtein Distance between two strings
 */
export function levenshteinDistance(a: string, b: string): number {
  const matrix: number[][] = [];

  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i];
  }

  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1, // substitution
          Math.min(
            matrix[i][j - 1] + 1, // insertion
            matrix[i - 1][j] + 1  // deletion
          )
        );
      }
    }
  }

  return matrix[b.length][a.length];
}

/**
 * Similarity ratio between 0.0 and 1.0 (100.0%)
 */
export function stringSimilarity(str1: string, str2: string): number {
  if (!str1 || !str2) return 0;
  const s1 = str1.trim().toLowerCase();
  const s2 = str2.trim().toLowerCase();
  if (s1 === s2) return 1.0;

  const maxLength = Math.max(s1.length, s2.length);
  if (maxLength === 0) return 1.0;

  const distance = levenshteinDistance(s1, s2);
  return Math.max(0, (maxLength - distance) / maxLength);
}

/**
 * Compares two domain names (e.g. "rrb-gov.in" vs "rrb.gov.in")
 */
export function compareDomains(domain1: string, domain2: string): {
  similarity: number;
  isSubdomain: boolean;
  isTyposquatted: boolean;
} {
  if (!domain1 || !domain2) return { similarity: 0, isSubdomain: false, isTyposquatted: false };
  const d1 = domain1.replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0].toLowerCase();
  const d2 = domain2.replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0].toLowerCase();

  if (d1 === d2) return { similarity: 1.0, isSubdomain: false, isTyposquatted: false };

  const isSubdomain = d1.endsWith('.' + d2) || d2.endsWith('.' + d1);
  const sim = stringSimilarity(d1, d2);
  const isTyposquatted = sim > 0.75 && !isSubdomain;

  return { similarity: sim, isSubdomain, isTyposquatted };
}

/**
 * Normalizes phone numbers for standard E.164 comparison
 */
export function normalizePhone(phone: string): string {
  if (!phone) return '';
  return phone.replace(/[^\d+]/g, '');
}

/**
 * Compares phone numbers
 */
export function comparePhones(phone1: string, phone2: string): number {
  const p1 = normalizePhone(phone1);
  const p2 = normalizePhone(phone2);
  if (!p1 || !p2) return 0;
  if (p1 === p2) return 1.0;
  if (p1.endsWith(p2.slice(-10)) || p2.endsWith(p1.slice(-10))) return 0.9;
  return stringSimilarity(p1, p2);
}

/**
 * Normalizes UPI Handles (e.g. "rrbjobs@ybl" -> "rrbjobs@ybl")
 */
export function normalizeUPI(upi: string): string {
  if (!upi) return '';
  return upi.trim().toLowerCase();
}

/**
 * Compares UPI details
 */
export function compareUPIs(upi1: string, upi2: string): number {
  const u1 = normalizeUPI(upi1);
  const u2 = normalizeUPI(upi2);
  if (!u1 || !u2) return 0;
  if (u1 === u2) return 1.0;
  
  const [handle1] = u1.split('@');
  const [handle2] = u2.split('@');
  if (handle1 && handle2 && handle1 === handle2) return 0.85; // Same handle, different bank suffix

  return stringSimilarity(u1, u2);
}

/**
 * Checks if a domain belongs to an official Indian government TLD (.gov.in, .nic.in, etc.)
 */
export function isOfficialGovDomain(domain: string): boolean {
  if (!domain) return false;
  const d = domain.toLowerCase();
  return d.endsWith('.gov.in') || d.endsWith('.nic.in') || d.endsWith('.mil.in');
}
