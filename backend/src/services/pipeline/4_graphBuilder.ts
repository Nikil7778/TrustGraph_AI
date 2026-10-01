import { EvidenceGraphData, GraphEdge, GraphNode, RecruitmentDNA } from '../../types';

export function buildEvidenceGraph(dna: RecruitmentDNA): EvidenceGraphData {
  const norm = dna.normalizedAttributes;

  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];

  const orgLabel = norm.organization.raw && norm.organization.raw !== 'Unspecified / Unknown Organization'
    ? norm.organization.raw
    : 'Claimed Entity (Unspecified)';

  nodes.push({
    id: 'org_1',
    label: orgLabel,
    type: 'ORGANIZATION',
    subText: norm.organization.raw !== 'Unspecified / Unknown Organization' ? 'Claimed Entity' : 'Unspecified Entity'
  });

  if (norm.notificationId.normalized && norm.notificationId.normalized !== 'NOT PROVIDED') {
    nodes.push({
      id: 'notif_1',
      label: `Ref: ${norm.notificationId.normalized}`,
      type: 'NOTIFICATION',
      subText: 'Notification Ref ID'
    });
    edges.push({ id: 'e1', source: 'org_1', target: 'notif_1', label: 'ISSUED_NOTICE' });
  }

  if (norm.website.normalizedDomain && norm.website.normalizedDomain !== 'not provided') {
    nodes.push({
      id: 'web_1',
      label: norm.website.normalizedDomain,
      type: 'WEBSITE',
      subText: norm.website.isGovDomain ? 'Official Domain (.gov.in)' : 'Unverified Web Domain',
      isHighRisk: !norm.website.isGovDomain
    });
    edges.push({ id: 'e2', source: 'org_1', target: 'web_1', label: 'HOSTED_ON' });
  }

  if (norm.email.raw && norm.email.raw !== 'Not Provided') {
    nodes.push({
      id: 'email_1',
      label: norm.email.raw,
      type: 'EMAIL',
      subText: norm.email.isFreeProvider ? 'Public Provider (Gmail/Yahoo)' : 'Domain Contact Email',
      isHighRisk: norm.email.isFreeProvider
    });
    edges.push({ id: 'e3', source: 'org_1', target: 'email_1', label: 'USES_CONTACT_EMAIL' });
  }

  if (norm.phone.normalized && norm.phone.normalized !== 'Not Provided') {
    nodes.push({
      id: 'phone_1',
      label: norm.phone.normalized,
      type: 'PHONE',
      subText: 'Helpline Number'
    });
    edges.push({ id: 'e4', source: 'org_1', target: 'phone_1', label: 'HELPLINE_PHONE' });
  }

  if (norm.payment.upiId && norm.payment.upiId !== 'Not Provided') {
    nodes.push({
      id: 'payment_1',
      label: `UPI: ${norm.payment.upiId}`,
      type: 'PAYMENT',
      subText: norm.payment.isPrivateUpi ? 'Private VPA (High Risk)' : 'Official Treasury',
      isHighRisk: norm.payment.isPrivateUpi
    });
    const parentId = nodes.some(n => n.id === 'notif_1') ? 'notif_1' : 'org_1';
    edges.push({ id: 'e6', source: parentId, target: 'payment_1', label: 'DEMANDS_FEE' });
  }

  if (norm.jobMetadata.designation && norm.jobMetadata.designation !== 'Unspecified Position') {
    nodes.push({
      id: 'job_1',
      label: norm.jobMetadata.designation,
      type: 'JOB',
      subText: norm.jobMetadata.totalVacancies ? `${norm.jobMetadata.totalVacancies} Posts` : 'Job Vacancy'
    });
    edges.push({ id: 'e5', source: 'org_1', target: 'job_1', label: 'OFFERS_VACANCY' });
  }

  if (nodes.length === 1 && nodes[0].id === 'org_1') {
    nodes.push({
      id: 'text_1',
      label: 'Unstructured Text Content',
      type: 'JOB',
      subText: 'No Structured Recruitment Parameters Found',
      isHighRisk: false
    });
    edges.push({ id: 'e_text', source: 'org_1', target: 'text_1', label: 'CONTAINS_INPUT' });
  }

  return { nodes, edges };
}

