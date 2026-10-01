import axios from 'axios';
import type { AnalysisRecordItem, ExplainableResultDashboard, InputType } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  withCredentials: true
});

client.interceptors.response.use(response => response, error => {
  const url = String(error.config?.url || '');
  if (error.response?.status === 401 && !/\/auth\/(login|signup|register|check-username)/.test(url)) {
    window.dispatchEvent(new Event('jobguard:session-expired'));
  }
  return Promise.reject(error);
});

// Authentication APIs
export async function loginUser(username: string, password: string) {
  const res = await client.post('/auth/login', { username, password });
  return res.data;
}

export async function registerUser(username: string, password: string) {
  const res = await client.post('/auth/signup', { username, password });
  return res.data;
}

export async function checkUsername(username: string) {
  const res = await client.get(`/auth/check-username/${encodeURIComponent(username)}`);
  return res.data as { available: boolean; reason?: string };
}

export async function logoutUser() {
  await client.post('/auth/logout');
}

export async function fetchCurrentUser() {
  const res = await client.get('/auth/me');
  return res.data;
}

export async function fetchAdminDashboard() {
  const res = await client.get('/admin/dashboard');
  return res.data;
}

export async function fetchAdminUsers(params?: { page?: number; limit?: number }) {
  const res = await client.get('/admin/users', { params });
  return res.data;
}

export async function fetchAdminAnalyses(params?: { page?: number; limit?: number }) {
  const res = await client.get('/admin/analyses', { params });
  return res.data;
}

export async function fetchAdminFingerprints() {
  const res = await client.get('/admin/fingerprints');
  return res.data;
}

// User-Specific History APIs
export async function fetchUserHistory(params?: {
  limit?: number;
  page?: number;
  search?: string;
  riskLevel?: string;
}): Promise<{ records: any[]; total: number; page: number; limit: number; totalPages: number }> {
  const res = await client.get('/history', { params });
  return res.data;
}

export async function fetchHistoryById(id: string): Promise<any> {
  const res = await client.get(`/history/${id}`);
  return res.data;
}

export async function deleteHistoryRecord(id: string): Promise<any> {
  const res = await client.delete(`/history/${id}`);
  return res.data;
}

export async function fetchAdminHistory(params?: { limit?: number; page?: number; filterUserId?: string }): Promise<any> {
  const res = await client.get('/admin/history', { params });
  return res.data;
}

export async function submitNewAnalysis(params: {
  type: InputType;
  content?: string;
  file?: File;
  url?: string;
}): Promise<{ recordId: string; dashboard: ExplainableResultDashboard; pipelineSteps: any }> {
  const formData = new FormData();
  formData.append('type', params.type);
  if (params.content) formData.append('content', params.content);
  if (params.url) formData.append('url', params.url);
  if (params.file) formData.append('file', params.file);

  const res = await client.post('/analysis/create', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

  return res.data.data;
}

export async function fetchAnalysisHistory(): Promise<AnalysisRecordItem[]> {
  const res = await client.get('/history?limit=6');
  return res.data.records || [];
}

export async function fetchThreatIntelligence(): Promise<any[]> {
  try {
    const res = await client.get('/threat-intelligence');
    return res.data.data;
  } catch (error) {
    return getMockThreatIntelList();
  }
}

export async function fetchOfficialRegistry(): Promise<any[]> {
  try {
    const res = await client.get('/official-registry');
    return res.data.data;
  } catch (error) {
    return getMockOfficialRegistry();
  }
}

export async function fetchWeights(): Promise<any> {
  try {
    const res = await client.get('/settings/weights');
    return res.data.data;
  } catch (error) {
    return {
      organizationWeight: 15.0,
      emailWeight: 15.0,
      phoneWeight: 15.0,
      upiWeight: 20.0,
      websiteWeight: 15.0,
      qrWeight: 10.0,
      logoWeight: 4.0,
      notificationIdWeight: 3.0,
      dateWeight: 3.0
    };
  }
}

export async function saveWeights(weights: any): Promise<any> {
  try {
    const res = await client.put('/settings/weights', weights);
    return res.data.data;
  } catch (error) {
    return weights;
  }
}

// Client Fallback Data Generator
export function mockAnalysisFallback(params: any) {
  const isScam = !params.content?.includes('ssc.gov.in');

  const mockDna = {
    dnaId: `RDNA-7F3A-9C2D-${Math.random().toString(36).substring(2, 6).toUpperCase()}`,
    canonicalHash: '0x89a7b3c2d4e5f6a1b2c3d4e5',
    createdAt: new Date().toISOString(),
    normalizedAttributes: {
      organization: { raw: 'Ministry of Defence', normalized: 'MINISTRY OF DEFENCE', alias: 'MOD' },
      notificationId: { raw: 'MOD/2026/145', normalized: 'MOD/2026/145' },
      website: { raw: 'defence-recruitment.com', normalizedDomain: 'defence-recruitment.com', isGovDomain: false },
      email: { raw: 'recruitment@defence-gov.com', domain: 'defence-gov.com', isFreeProvider: false },
      phone: { raw: '+91 98765 43210', normalized: '+919876543210' },
      payment: { upiId: 'defence123@upi', applicationFee: 500, paymentGateway: 'UPI Direct', isPrivateUpi: true },
      media: { qrCodeData: 'suspicious_qr_payload_encoded', logoHash: 'emblem_phash_89a7b' },
      timeline: { publishDate: '2026-08-15', lastDateToApply: '2026-09-30' },
      jobMetadata: { designation: 'Junior Security Guard / Office Assistant', totalVacancies: 1450, salaryRange: '₹35,000 - ₹55,000 / month' }
    },
    fingerprintHash: 'hash_89a7b3c2'
  };

  const mockFieldMatches = [
    { fieldName: 'Organization', weight: 15, claimedValue: 'Ministry of Defence', matchedValue: 'Ministry of Defence', matchType: 'EXACT', similarityScore: 100.0, contributionToTotal: 15.0 },
    { fieldName: 'Email', weight: 15, claimedValue: 'recruitment@defence-gov.com', matchedValue: 'recruitment@defence-gov.com', matchType: 'EXACT', similarityScore: 100.0, contributionToTotal: 15.0 },
    { fieldName: 'Phone', weight: 15, claimedValue: '+91 98765 43210', matchedValue: '+91 98765 43210', matchType: 'EXACT', similarityScore: 100.0, contributionToTotal: 15.0 },
    { fieldName: 'UPI / Payment', weight: 20, claimedValue: 'defence123@upi', matchedValue: 'defence123@upi', matchType: 'EXACT', similarityScore: 100.0, contributionToTotal: 20.0 },
    { fieldName: 'Website', weight: 15, claimedValue: 'defence-recruitment.com', matchedValue: 'defence-recruitment.com', matchType: 'EXACT', similarityScore: 100.0, contributionToTotal: 15.0 },
    { fieldName: 'QR Code', weight: 10, claimedValue: 'Embedded QR Payload', matchedValue: 'Embedded QR Payload', matchType: 'EXACT', similarityScore: 100.0, contributionToTotal: 10.0 },
    { fieldName: 'Logo', weight: 4, claimedValue: 'Government Emblem', matchedValue: 'Scam Emblem Copy', matchType: 'SIMILAR', similarityScore: 82.0, contributionToTotal: 3.28 },
    { fieldName: 'Notification ID', weight: 3, claimedValue: 'MOD/2026/145', matchedValue: 'MOD/2026/099', matchType: 'DIFFERENT', similarityScore: 30.0, contributionToTotal: 0.9 },
    { fieldName: 'Date', weight: 3, claimedValue: '2026-08-15', matchedValue: '2026-05-10', matchType: 'DIFFERENT', similarityScore: 20.0, contributionToTotal: 0.6 }
  ];

  const dashboard: ExplainableResultDashboard = {
    analysisId: `mock-${Date.now()}`,
    title: params.content ? params.content.substring(0, 45) : 'Recruitment Notice Analysis',
    trustScore: {
      overallScore: isScam ? 18 : 92,
      riskLevel: isScam ? 'CRITICAL_SCAM' : 'VERIFIED_GENUINE',
      subScores: {
        officialRegistryAlignment: isScam ? 5 : 40,
        suspiciousSimilarityPenalty: isScam ? 3 : 32,
        riskAnomalyPenalty: isScam ? 10 : 20
      },
      recommendation: isScam 
        ? 'DO NOT proceed with this recruitment offer. High risk of financial and data fraud.'
        : 'Recruitment offer matches official government registry records.'
    },
    recruitmentDna: mockDna as any,
    fingerprintMatch: {
      matchedScamId: 'RF-10245',
      matchedScamName: 'Fake Ministry of Defence Recruitment Scam 2026',
      scamCategory: 'Advance Fee & Phishing Scam',
      fieldMatches: mockFieldMatches as any,
      matchedFieldsCount: 7,
      totalFieldsEvaluated: 9,
      overallSimilarityPercentage: 88.9,
      breakdownSummary: '7/9 characteristics matched'
    },
    officialVerification: {
      matchedRecordId: 'MOD-OFFICIAL-1',
      officialOrgName: 'Ministry of Defence',
      officialWebsiteUrl: 'https://mod.gov.in',
      isOrgVerified: true,
      isWebsiteGovDomain: false,
      isWebsiteInOfficialList: false,
      isEmailInOfficialList: false,
      isPhoneInOfficialList: false,
      isNotificationIdValid: false,
      feeDiscrepancy: { claimedFee: 500, officialFee: 100, isMatching: false },
      verificationScore: 15,
      notes: [
        'Website (defence-recruitment.com) differs from official portal (mod.gov.in).',
        'Official recruitment fees are deposited via treasury portals (SBI e-Pay), never via private UPI VPAs.'
      ]
    },
    aiReasoning: {
      overallRiskSummary: 'CRITICAL ALERT: High probability fake recruitment. Identified 4 severe red flags including private UPI payments and suspicious domains.',
      redFlags: [
        { category: 'Contact Channel', title: 'Government Emblem + Gmail/Private Email', description: 'Claims government representation but uses private email host.', severity: 'HIGH' },
        { category: 'Payment Endpoint', title: 'Private UPI VPA for Fee Collection', description: 'Application fee requested via private VPA (defence123@upi).', severity: 'CRITICAL' },
        { category: 'Web Portal', title: 'Suspicious Non-Government Domain', description: 'Domain lacks valid .gov.in or .nic.in TLD extension.', severity: 'HIGH' }
      ],
      anomaliesIdentified: ['Private UPI VPA', 'Non-gov domain', 'Free email provider'],
      chainOfThought: [
        'Analyzed recruitment offer claiming representation for Ministry of Defence.',
        'Identified critical fraud vector: Direct private UPI transfer request (defence123@upi).',
        'Fingerprint cross-comparison matched active threat intelligence record RF-10245.'
      ],
      confidenceScore: 96.5
    },
    evidenceGraph: {
      nodes: [
        { id: 'org_1', label: 'Ministry of Defence', type: 'ORGANIZATION', subText: 'Claimed Entity' },
        { id: 'notif_1', label: 'Ref: MOD/2026/145', type: 'NOTIFICATION', subText: 'Claimed ID' },
        { id: 'web_1', label: 'defence-recruitment.com', type: 'WEBSITE', subText: 'Unverified Domain', isHighRisk: true },
        { id: 'email_1', label: 'recruitment@defence-gov.com', type: 'EMAIL', subText: 'Domain Email', isHighRisk: true },
        { id: 'phone_1', label: '+91 98765 43210', type: 'PHONE', subText: 'Helpline Number' },
        { id: 'payment_1', label: 'UPI: defence123@upi', type: 'PAYMENT', subText: 'Private VPA (High Risk)', isHighRisk: true },
        { id: 'qr_1', label: 'Encoded Payment QR', type: 'QR', subText: 'Embedded Scan Code', isHighRisk: true },
        { id: 'job_1', label: 'Junior Security Officer', type: 'JOB', subText: '1450 Posts' }
      ],
      edges: [
        { id: 'e1', source: 'org_1', target: 'notif_1', label: 'ISSUED_NOTICE' },
        { id: 'e2', source: 'org_1', target: 'web_1', label: 'HOSTED_ON' },
        { id: 'e3', source: 'org_1', target: 'email_1', label: 'USES_CONTACT_EMAIL' },
        { id: 'e4', source: 'org_1', target: 'phone_1', label: 'HELPLINE_PHONE' },
        { id: 'e5', source: 'org_1', target: 'job_1', label: 'OFFERS_VACANCY' },
        { id: 'e6', source: 'notif_1', target: 'payment_1', label: 'DEMANDS_FEE' },
        { id: 'e7', source: 'payment_1', target: 'qr_1', label: 'EMBEDS_QR_PAYLOAD' }
      ]
    },
    fieldByFieldComparison: mockFieldMatches as any,
    actionItems: [
      'Do not transfer money to the provided UPI handle or QR code under any circumstances.',
      'Verify official notifications directly on the accredited portal (mod.gov.in).',
      'Report this fraudulent recruitment notification to Cyber Crime Helpline (1930) or PIB Fact Check.'
    ]
  };

  return {
    recordId: dashboard.analysisId,
    dashboard,
    pipelineSteps: {
      1: { title: dashboard.title, rawText: params.content || 'Sample Input' },
      2: { entities: dashboard.recruitmentDna.normalizedAttributes },
      3: dashboard.recruitmentDna,
      4: dashboard.evidenceGraph,
      5: dashboard.officialVerification,
      6: dashboard.fingerprintMatch,
      7: dashboard.aiReasoning,
      8: dashboard.trustScore,
      9: dashboard
    }
  };
}

export function getMockHistoryList(): AnalysisRecordItem[] {
  return [
    { id: 'hist-1', title: 'Ministry of Defence Recruitment Notice', inputType: 'PDF', trustScore: 18, riskLevel: 'CRITICAL_SCAM', status: 'COMPLETED', createdAt: '2026-09-06T10:15:00Z' },
    { id: 'hist-2', title: 'Railway Recruitment Board Security Guard', inputType: 'TEXT', trustScore: 28, riskLevel: 'HIGH_RISK', status: 'COMPLETED', createdAt: '2026-09-05T16:30:00Z' },
    { id: 'hist-3', title: 'SSC Combined Graduate Level Exam 2026', inputType: 'URL', trustScore: 94, riskLevel: 'VERIFIED_GENUINE', status: 'COMPLETED', createdAt: '2026-09-04T12:00:00Z' },
    { id: 'hist-4', title: 'India Post GDS Recruitment Drive', inputType: 'IMAGE', trustScore: 52, riskLevel: 'MEDIUM_RISK', status: 'COMPLETED', createdAt: '2026-09-03T09:20:00Z' }
  ];
}

function getMockThreatIntelList() {
  return [
    {
      id: 'RF-10245',
      scamName: 'Fake Ministry of Defence Recruitment Scam 2026',
      targetOrganization: 'Ministry of Defence',
      scamCategory: 'Fake Defence Hiring & Advance Payment Scam',
      threatLevel: 'CRITICAL_SCAM',
      reportedCount: 412,
      suspiciousWebsites: ['defence-recruitment.com', 'mod-apply-online.org'],
      suspiciousEmails: ['recruitment@defence-gov.com', 'defencejobs2026@gmail.com'],
      suspiciousPhones: ['+91 98765 43210'],
      upiDetails: ['defence123@upi'],
      createdAt: '2026-08-10'
    },
    {
      id: 'RF-08731',
      scamName: 'Phishing Railway RRB Security Guard Recruitment',
      targetOrganization: 'Railway Recruitment Board (RRB)',
      scamCategory: 'Phishing Portal & QR Code Scam',
      threatLevel: 'HIGH_RISK',
      reportedCount: 189,
      suspiciousWebsites: ['rrb-jobs-apply-gov.in.co'],
      suspiciousEmails: ['railwayjobs2026@gmail.com'],
      suspiciousPhones: ['+91 91234 56789'],
      upiDetails: ['rrb-fee-pay@ybl'],
      createdAt: '2026-08-18'
    }
  ];
}

function getMockOfficialRegistry() {
  return [
    { organizationName: 'Ministry of Defence', verifiedDomains: ['mod.gov.in', 'defence.gov.in'], officialEmails: ['recruitment@mod.gov.in'], verifiedBy: 'PIB Fact Check' },
    { organizationName: 'Railway Recruitment Board (RRB)', verifiedDomains: ['rrbcdg.gov.in', 'indianrailways.gov.in'], officialEmails: ['notice@rrbcdg.gov.in'], verifiedBy: 'Ministry of Railways' },
    { organizationName: 'Staff Selection Commission (SSC)', verifiedDomains: ['ssc.gov.in', 'ssc.nic.in'], officialEmails: ['helpdesk-ssc@gov.in'], verifiedBy: 'DoPT India' }
  ];
}
