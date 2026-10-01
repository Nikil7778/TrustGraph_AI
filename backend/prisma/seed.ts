import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding TRUST AI Database...');

  // Clean existing
  await prisma.officialRegistry.deleteMany({});
  await prisma.knownSuspiciousFingerprint.deleteMany({});
  await prisma.systemWeights.deleteMany({});
  await prisma.analysisRecord.deleteMany({});
  await prisma.user.deleteMany({});

  // 0. Seed Users
  const userPasswordHash = await bcrypt.hash('password123', 10);
  const adminPasswordHash = await bcrypt.hash('admin123', 10);

  const userA = await prisma.user.create({
    data: {
      name: 'User A',
      email: 'userA@example.com',
      password: userPasswordHash,
      role: 'USER'
    }
  });

  const userB = await prisma.user.create({
    data: {
      name: 'User B',
      email: 'userB@example.com',
      password: userPasswordHash,
      role: 'USER'
    }
  });

  const adminUser = await prisma.user.create({
    data: {
      name: 'System Admin',
      email: 'admin@example.com',
      password: adminPasswordHash,
      role: 'ADMIN'
    }
  });

  console.log('👤 Created Users: User A (userA@example.com), User B (userB@example.com), Admin (admin@example.com)');

  // 1. System Weights
  await prisma.systemWeights.create({
    data: {
      id: 'default_weights',
      organizationWeight: 15.0,
      emailWeight: 15.0,
      phoneWeight: 15.0,
      upiWeight: 20.0,
      websiteWeight: 15.0,
      qrWeight: 10.0,
      logoWeight: 4.0,
      notificationIdWeight: 3.0,
      dateWeight: 3.0
    }
  });

  // 2. Official Registries
  await prisma.officialRegistry.createMany({
    data: [
      {
        organizationName: 'Ministry of Defence',
        orgAlias: JSON.stringify(['MOD', 'Defence Ministry', 'Indian Armed Forces']),
        officialWebsites: JSON.stringify(['mod.gov.in', 'defence.gov.in']),
        officialEmails: JSON.stringify(['recruitment@mod.gov.in', 'support@defence.gov.in']),
        officialPhones: JSON.stringify(['+911123010101', '+911123012345']),
        notificationIds: JSON.stringify(['MOD/2026/145', 'MOD/2026/089']),
        officialFees: 100,
        officialPaymentMethods: JSON.stringify(['SBI e-Pay', 'Bharatkosh Treasury Portal']),
        verifiedDomains: JSON.stringify(['mod.gov.in', 'defence.gov.in']),
        verifiedBy: 'Government of India PIB Fact Check'
      },
      {
        organizationName: 'Railway Recruitment Board (RRB)',
        orgAlias: JSON.stringify(['RRB', 'Indian Railways', 'Railway Ministry']),
        officialWebsites: JSON.stringify(['rrbcdg.gov.in', 'indianrailways.gov.in', 'rrb.gov.in']),
        officialEmails: JSON.stringify(['notice@rrbcdg.gov.in', 'helpdesk@rrb.gov.in']),
        officialPhones: JSON.stringify(['+911722730093', '139']),
        notificationIds: JSON.stringify(['CEN-01/2026', 'CEN-02/2026']),
        officialFees: 500,
        officialPaymentMethods: JSON.stringify(['SBI Gateway', 'NetBanking']),
        verifiedDomains: JSON.stringify(['rrbcdg.gov.in', 'indianrailways.gov.in']),
        verifiedBy: 'Ministry of Railways Official Gazette'
      },
      {
        organizationName: 'Staff Selection Commission (SSC)',
        orgAlias: JSON.stringify(['SSC', 'Staff Selection Commission India']),
        officialWebsites: JSON.stringify(['ssc.gov.in', 'ssc.nic.in']),
        officialEmails: JSON.stringify(['helpdesk-ssc@gov.in', 'cgl-support@ssc.nic.in']),
        officialPhones: JSON.stringify(['+911124361806']),
        notificationIds: JSON.stringify(['SSC-CGL-2026', 'SSC-CHSL-2026']),
        officialFees: 100,
        officialPaymentMethods: JSON.stringify(['BHIM UPI Gateway', 'SBI Cyber Treasury']),
        verifiedDomains: JSON.stringify(['ssc.gov.in', 'ssc.nic.in']),
        verifiedBy: 'DoPT - Department of Personnel and Training'
      }
    ]
  });

  // 3. Known Suspicious Fingerprints
  await prisma.knownSuspiciousFingerprint.createMany({
    data: [
      {
        id: 'RF-10245',
        scamName: 'Fake Ministry of Defence Recruitment Scam 2026',
        targetOrganization: 'Ministry of Defence',
        scamCategory: 'Fake Defence Hiring & Advance Payment Scam',
        notificationId: 'MOD/2026/145',
        suspiciousWebsites: JSON.stringify(['defence-recruitment.com', 'mod-apply-online.org']),
        suspiciousEmails: JSON.stringify(['recruitment@defence-gov.com', 'defencejobs2026@gmail.com']),
        suspiciousPhones: JSON.stringify(['+919876543210', '+919876543211']),
        upiDetails: JSON.stringify(['defence123@upi', 'defence-fee@ybl']),
        qrCodes: JSON.stringify(['suspicious_qr_payload_encoded']),
        logoHashes: JSON.stringify(['emblem_phash_89a7b']),
        threatLevel: 'CRITICAL_SCAM',
        reportedCount: 412,
        notes: 'Promises direct recruitment as Guard/Officer without written exam. Demands ₹500 via private UPI.'
      },
      {
        id: 'RF-08731',
        scamName: 'Phishing Railway RRB Security Guard Recruitment',
        targetOrganization: 'Railway Recruitment Board (RRB)',
        scamCategory: 'Phishing Portal & QR Code Scam',
        notificationId: 'CEN-99/2026',
        suspiciousWebsites: JSON.stringify(['rrb-jobs-apply-gov.in.co', 'rrb-railway-recruitment.com']),
        suspiciousEmails: JSON.stringify(['railwayjobs2026@gmail.com']),
        suspiciousPhones: JSON.stringify(['+919123456789']),
        upiDetails: JSON.stringify(['rrb-fee-pay@ybl']),
        qrCodes: JSON.stringify(['rrb_fake_qr_9011']),
        logoHashes: JSON.stringify(['rrb_phash_1234']),
        threatLevel: 'HIGH_RISK',
        reportedCount: 189,
        notes: 'Cloned website interface of RRB Chandigarh requesting ₹500 fee via Paytm/PhonePe QR code.'
      },
      {
        id: 'RF-04321',
        scamName: 'Fake SSC CGL Admit Card Download Fee',
        targetOrganization: 'Staff Selection Commission (SSC)',
        scamCategory: 'Admit Card Processing Fee Fraud',
        notificationId: 'SSC-CGL-2026-FAKE',
        suspiciousWebsites: JSON.stringify(['ssc-cgl-admit-card-online.org']),
        suspiciousEmails: JSON.stringify(['ssc.support2026@yahoo.com']),
        suspiciousPhones: JSON.stringify(['+919988776655']),
        upiDetails: JSON.stringify(['ssc-admit-fee@paytm']),
        qrCodes: JSON.stringify(['ssc_admit_qr']),
        logoHashes: JSON.stringify(['ssc_emblem_hash']),
        threatLevel: 'HIGH_RISK',
        reportedCount: 87,
        notes: 'Sends fake SMS with link to download hall ticket upon payment of ₹250 instant fee.'
      }
    ]
  });

  // Seed sample initial user analyses for User A & User B
  await prisma.analysisRecord.create({
    data: {
      userId: userA.id,
      title: 'Fake Ministry of Defence Recruitment Drive',
      inputType: 'TEXT',
      rawInputContent: 'Ministry of Defence Direct Recruitment MOD/2026/145 fee ₹500 via defence123@upi',
      status: 'COMPLETED',
      extractedData: JSON.stringify({}),
      recruitmentDna: JSON.stringify({}),
      evidenceGraph: JSON.stringify({}),
      verificationResult: JSON.stringify({}),
      fingerprintMatches: JSON.stringify({}),
      aiReasoning: JSON.stringify({}),
      trustScore: 18,
      riskLevel: 'CRITICAL_SCAM',
      explainableResult: JSON.stringify({})
    }
  });

  await prisma.analysisRecord.create({
    data: {
      userId: userA.id,
      title: 'Genuine Staff Selection Commission SSC CGL Notice',
      inputType: 'TEXT',
      rawInputContent: 'Staff Selection Commission SSC-CGL-2026 portal https://ssc.gov.in email helpdesk-ssc@gov.in fee ₹100',
      status: 'COMPLETED',
      extractedData: JSON.stringify({}),
      recruitmentDna: JSON.stringify({}),
      evidenceGraph: JSON.stringify({}),
      verificationResult: JSON.stringify({}),
      fingerprintMatches: JSON.stringify({}),
      aiReasoning: JSON.stringify({}),
      trustScore: 95,
      riskLevel: 'VERIFIED_GENUINE',
      explainableResult: JSON.stringify({})
    }
  });

  await prisma.analysisRecord.create({
    data: {
      userId: userB.id,
      title: 'Phishing Railway RRB Guard Hiring Notice',
      inputType: 'TEXT',
      rawInputContent: 'RRB CEN-99/2026 apply rrb-jobs-apply-gov.in.co fee rrb-fee-pay@ybl',
      status: 'COMPLETED',
      extractedData: JSON.stringify({}),
      recruitmentDna: JSON.stringify({}),
      evidenceGraph: JSON.stringify({}),
      verificationResult: JSON.stringify({}),
      fingerprintMatches: JSON.stringify({}),
      aiReasoning: JSON.stringify({}),
      trustScore: 32,
      riskLevel: 'HIGH_RISK',
      explainableResult: JSON.stringify({})
    }
  });

  console.log('✅ Database seeded successfully!');
}

main()
  .catch(e => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });

