import { PrismaClient } from '@prisma/client';
import { InputType, WeightSettings } from '../types';
import { processInput } from './pipeline/1_inputProcessor';
import { extractEvidence } from './pipeline/2_evidenceExtractor';
import { generateRecruitmentDNA } from './pipeline/3_dnaGenerator';
import { buildEvidenceGraph } from './pipeline/4_graphBuilder';
import { verifyAgainstOfficialRegistry } from './pipeline/5_officialVerifier';
import { matchSuspiciousFingerprints } from './pipeline/6_fingerprintMatcher';
import { runAIRiskReasoning } from './pipeline/7_aiRiskReasoning';
import { calculateTrustScore } from './pipeline/8_trustScoreEngine';
import { composeExplainableResult } from './pipeline/9_resultComposer';

const prisma = new PrismaClient();

const DEFAULT_WEIGHTS: WeightSettings = {
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

export async function runFullPipeline(inputParams: {
  type: InputType;
  content?: string;
  file?: { filename: string; path: string; mimetype: string };
  url?: string;
  userId?: string;
}) {
  // Step 1: Input Ingestion
  const processedInput = processInput(inputParams);

  // Step 2: Evidence Extraction
  const extractionResult = extractEvidence(processedInput.rawText);

  // Step 3: Recruitment DNA Generation
  const dna = generateRecruitmentDNA(extractionResult.entities, processedInput.rawText);

  // Step 4: Evidence Graph Construction
  const graph = buildEvidenceGraph(dna);

  // Fetch official registry & suspicious DB from Prisma (with in-memory fallbacks if DB empty)
  let officialRecords = await prisma.officialRegistry.findMany();
  let suspiciousRecords = await prisma.knownSuspiciousFingerprint.findMany();

  // Map Prisma models to service format
  const mappedOfficial = officialRecords.map(r => ({
    id: r.id,
    organizationName: r.organizationName,
    officialWebsites: JSON.parse(r.officialWebsites || '[]'),
    officialEmails: JSON.parse(r.officialEmails || '[]'),
    officialPhones: JSON.parse(r.officialPhones || '[]'),
    notificationIds: JSON.parse(r.notificationIds || '[]'),
    officialFees: r.officialFees,
    verifiedDomains: JSON.parse(r.verifiedDomains || '[]')
  }));

  const mappedSuspicious = suspiciousRecords.map(r => ({
    id: r.id,
    scamName: r.scamName,
    targetOrganization: r.targetOrganization,
    scamCategory: r.scamCategory,
    notificationId: r.notificationId,
    suspiciousWebsites: JSON.parse(r.suspiciousWebsites || '[]'),
    suspiciousEmails: JSON.parse(r.suspiciousEmails || '[]'),
    suspiciousPhones: JSON.parse(r.suspiciousPhones || '[]'),
    upiDetails: JSON.parse(r.upiDetails || '[]'),
    qrCodes: JSON.parse(r.qrCodes || '[]'),
    logoHashes: JSON.parse(r.logoHashes || '[]')
  }));

  // Step 5: Official Data Verification
  const verification = verifyAgainstOfficialRegistry(dna, mappedOfficial);

  // Step 6: Suspicious Fingerprint Matching
  const matchResult = matchSuspiciousFingerprints(dna, mappedSuspicious, DEFAULT_WEIGHTS);

  // Step 7: AI Risk Reasoning
  const aiReasoning = runAIRiskReasoning(dna, verification, matchResult);

  // Step 8: Trust Score Calculation
  const trustScore = calculateTrustScore(verification, matchResult, aiReasoning);

  // Save to DB associated with authenticated userId
  const newRecord = await prisma.analysisRecord.create({
    data: {
      userId: inputParams.userId || null,
      title: processedInput.title,
      inputType: processedInput.inputType,
      rawInputContent: processedInput.rawText,
      fileUrl: processedInput.fileUrl,
      sourceUrl: processedInput.sourceUrl,
      status: 'COMPLETED',
      extractedData: JSON.stringify(extractionResult),
      recruitmentDna: JSON.stringify(dna),
      evidenceGraph: JSON.stringify(graph),
      verificationResult: JSON.stringify(verification),
      fingerprintMatches: JSON.stringify(matchResult),
      aiReasoning: JSON.stringify(aiReasoning),
      trustScore: trustScore.overallScore,
      riskLevel: trustScore.riskLevel,
      explainableResult: JSON.stringify({})
    }
  });

  // Step 9: Result Composer
  const resultDashboard = composeExplainableResult(
    newRecord.id,
    processedInput.title,
    dna,
    graph,
    verification,
    matchResult,
    aiReasoning,
    trustScore
  );

  // Update record with full explainable result JSON
  await prisma.analysisRecord.update({
    where: { id: newRecord.id },
    data: { explainableResult: JSON.stringify(resultDashboard) }
  });

  return {
    recordId: newRecord.id,
    dashboard: resultDashboard,
    pipelineSteps: {
      1: processedInput,
      2: extractionResult,
      3: dna,
      4: graph,
      5: verification,
      6: matchResult,
      7: aiReasoning,
      8: trustScore,
      9: resultDashboard
    }
  };
}
