import { InputType } from '../../types';

export interface ProcessedInput {
  title: string;
  rawText: string;
  inputType: InputType;
  fileUrl?: string;
  sourceUrl?: string;
}

export function processInput(input: {
  type: InputType;
  content?: string;
  file?: { filename: string; path: string; mimetype: string };
  url?: string;
}): ProcessedInput {
  if (input.type === 'URL' && input.url) {
    return {
      title: `Recruitment URL Scan: ${input.url}`,
      rawText: `Recruitment Notice scanned from Web Portal: ${input.url}. Claimed Ministry/Department job hiring for 2026. Application Fee ₹500 via UPI. Contact: support@recruitment-desk.com`,
      inputType: 'URL',
      sourceUrl: input.url
    };
  }

  if ((input.type === 'PDF' || input.type === 'IMAGE') && input.file) {
    return {
      title: `Uploaded Document Scan: ${input.file.filename}`,
      rawText: `OFFICIAL RECRUITMENT NOTIFICATION 2026\nMinistry of Defence - Direct Recruitment Drive\nNotification Ref: MOD/2026/145\nDesignation: Junior Security Guard & Administrative Officer\nVacancies: 1,450 Posts\nSalary: ₹35,000 - ₹55,000 per month\nApplication Fee: ₹500 (Pay via UPI: defence123@upi)\nOfficial Portal: http://defence-recruitment.com\nContact Email: recruitment@defence-gov.com\nHelpdesk Phone: +91 98765 43210\nLast Date to Apply: 30th September 2026`,
      inputType: input.type,
      fileUrl: `/uploads/${input.file.filename}`
    };
  }

  // TEXT
  const textContent = input.content || 'Sample Recruitment Offer Text';
  const firstLine = textContent.split('\n')[0].substring(0, 50);

  return {
    title: firstLine.length > 5 ? firstLine : 'Recruitment Offer Notice',
    rawText: textContent,
    inputType: 'TEXT'
  };
}
