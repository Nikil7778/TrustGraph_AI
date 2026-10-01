import { ExtractedEntities } from '../../types';

export interface ExtractedFieldDetail<T> {
  value: T;
  confidence: number; // Percentage 0 - 100
  source: string;
}

export interface DetailedExtractionResult {
  entities: ExtractedEntities;
  fieldDetails: Record<string, ExtractedFieldDetail<any>>;
  isValidRecruitmentNotice: boolean;
}

export function extractEvidence(rawText: string): DetailedExtractionResult {
  const text = rawText || '';

  // Regex extractors & rule parsing
  const emailMatch = text.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/i);
  const phoneMatch = text.match(/(\+91[\s-]?)?[6-9]\d{9}/);
  const urlMatch = text.match(/(https?:\/\/[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(gov\.in|nic\.in|com|in|co\.in|org|net))/i);
  const feeMatch = text.match(/(?:application\s+fee|fee)\s*[:\-]?\s*(?:₹\s*)?([\d,]+)/i)
    || text.match(/₹\s?([\d,]+)|Rs\.?\s?([\d,]+)/i);
  const notifMatch = text.match(/(CEN|MOD|SSC|RRB|UPSC|JOB|REF)[/\-_A-Z0-9]{3,20}/i);

  // Check organizational keywords
  let orgName: string | null = null;
  if (/railway|rrb/i.test(text)) orgName = 'Railway Recruitment Board (RRB)';
  else if (/ssc|staff selection/i.test(text)) orgName = 'Staff Selection Commission (SSC)';
  else if (/upsc|public service/i.test(text)) orgName = 'Union Public Service Commission (UPSC)';
  else if (/defence|mod/i.test(text)) orgName = 'Ministry of Defence';
  else if (/post office|india post/i.test(text)) orgName = 'India Post Office';
  else if (/isro/i.test(text)) orgName = 'Indian Space Research Organisation (ISRO)';
  else if (/drdo/i.test(text)) orgName = 'Defence Research and Development Organisation (DRDO)';
  else if (/sbi|bank/i.test(text)) orgName = 'State Bank of India (SBI)';

  const email = emailMatch ? emailMatch[0] : null;
  const phone = phoneMatch ? phoneMatch[0] : null;

  // Real UPI VPA matcher (explicit UPI handles or preceded by UPI keywords)
  const upiExplicitMatch = text.match(/(?:upi|vpa|pay\s*to|pay\s*via)[:\s]*([a-zA-Z0-9._-]+@[a-zA-Z0-9]+)/i);
  const upiHandleMatch = text.match(/([a-zA-Z0-9._-]+@(upi|okaxis|okhdfcbank|paytm|ybl|axl|sbi|postbank|icici|barodampay|pnb|kotak|apl|ptaxis|freecharge))/i);

  let upi: string | null = null;
  if (upiExplicitMatch) {
    upi = upiExplicitMatch[1];
  } else if (upiHandleMatch) {
    upi = upiHandleMatch[0];
  }

  // Ensure extracted UPI is not a substring prefix of the email address
  if (upi && email && email.toLowerCase().startsWith(upi.toLowerCase())) {
    upi = null;
  }

  const website = urlMatch ? urlMatch[0] : null;
  const notifId = notifMatch ? notifMatch[0] : null;
  const fee = feeMatch ? parseInt((feeMatch[1] || feeMatch[2]).replace(/,/g, ''), 10) : null;

  // Detect job designation
  const jobMatch = text.match(/(designation|post|vacancy|role|position)[:\s]+([^\n.,;]+)/i);
  const designation = jobMatch ? jobMatch[2].trim() : (text.match(/recruit|hiring|officer|guard|clerk|engineer|staff/i) ? 'Recruitment Vacancy' : null);

  const isRecruitmentRelated = Boolean(
    orgName || email || phone || upi || website || notifId || fee !== null || designation ||
    /recruitment|vacancy|apply|salary|fee|notification|candidate|interview|job|hiring/i.test(text)
  );

  const entities: ExtractedEntities = {
    organization: orgName || 'Unspecified / Unknown Organization',
    notificationId: notifId || 'Not Provided',
    website: website || 'Not Provided',
    email: email || 'Not Provided',
    phone: phone || 'Not Provided',
    upiDetails: upi || 'Not Provided',
    qrCode: upi ? 'suspicious_qr_payload_encoded' : 'None',
    logo: orgName ? `${orgName} Logo/Emblem` : 'Unidentified Emblem',
    publishDate: 'N/A',
    lastDateToApply: 'N/A',
    jobDetails: {
      designation: designation || 'Unspecified Position',
      totalVacancies: null,
      salaryRange: 'N/A'
    },
    applicationFee: fee,
    otherInformation: isRecruitmentRelated ? ['Extracted from submitted text parameters.'] : ['No recruitment characteristics detected in input text.']
  };

  const fieldDetails: Record<string, ExtractedFieldDetail<any>> = {};

  fieldDetails.organization = {
    value: orgName || 'Not Identified in Input',
    confidence: orgName ? 92 : 0,
    source: orgName ? 'NLP Organization Entity Matcher' : 'Entity Extractor'
  };
  fieldDetails.notificationId = {
    value: notifId || 'Not Provided in Input',
    confidence: notifId ? 95 : 0,
    source: 'Regex Pattern Matcher'
  };
  fieldDetails.website = {
    value: website || 'Not Provided in Input',
    confidence: website ? 94 : 0,
    source: 'Domain Extractor'
  };
  fieldDetails.email = {
    value: email || 'Not Provided in Input',
    confidence: email ? 96 : 0,
    source: 'Contact Extractor'
  };
  fieldDetails.phone = {
    value: phone || 'Not Provided in Input',
    confidence: phone ? 92 : 0,
    source: 'Phone Extractor'
  };
  fieldDetails.upiDetails = {
    value: upi || 'Not Provided in Input',
    confidence: upi ? 91 : 0,
    source: 'VPA Payment Extractor'
  };
  fieldDetails.applicationFee = {
    value: fee !== null ? `₹${fee}` : 'Not Mentioned in Input',
    confidence: fee !== null ? 95 : 0,
    source: 'Payment Terms Parser'
  };

  return {
    entities,
    fieldDetails,
    isValidRecruitmentNotice: isRecruitmentRelated
  };
}

