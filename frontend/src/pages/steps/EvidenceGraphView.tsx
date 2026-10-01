import React, { useState, useMemo } from 'react';
import { ArrowRight, Network, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { ReactFlow, Background, Controls, Handle, Position, MarkerType } from '@xyflow/react';
import type { Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import type { EvidenceGraphData, GraphNode } from '../../types';

const CustomGraphNode: React.FC<{ data: any; selected?: boolean }> = ({ data, selected }) => {
  const isHighRisk = data.isHighRisk;
  return (
    <div
      className={`px-4 py-3 rounded-2xl border-2 transition-all shadow-md max-w-[210px] text-center bg-white cursor-pointer select-none ${
        isHighRisk
          ? selected
            ? 'border-red-600 ring-4 ring-red-100 bg-red-50/90 shadow-red-200'
            : 'border-red-400 bg-red-50/60 hover:border-red-500'
          : selected
          ? 'border-blue-600 ring-4 ring-blue-100 bg-blue-50/90 shadow-blue-200'
          : 'border-slate-300 bg-slate-50/90 hover:border-blue-400'
      }`}
    >
      <Handle type="target" position={Position.Top} className="!bg-slate-400 !w-2.5 !h-2.5" />
      <Handle type="source" position={Position.Bottom} className="!bg-slate-400 !w-2.5 !h-2.5" />
      <Handle type="target" position={Position.Left} id="target-left" className="!bg-slate-400 !w-2.5 !h-2.5" />
      <Handle type="source" position={Position.Right} id="source-right" className="!bg-slate-400 !w-2.5 !h-2.5" />

      <div className="flex items-center justify-center gap-1.5 mb-1">
        {isHighRisk ? (
          <AlertTriangle className="w-4 h-4 text-red-600 shrink-0" />
        ) : (
          <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
        )}
        <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-500">{data.type}</span>
      </div>
      <p className="text-xs font-black text-slate-900 leading-tight truncate">{data.label}</p>
      <p className="text-[10px] text-slate-500 font-medium mt-0.5">{data.subText}</p>
    </div>
  );
};

const nodeTypes = {
  customNode: CustomGraphNode,
};

export const EvidenceGraphView: React.FC<{ data: EvidenceGraphData; onNext: () => void }> = ({ data, onNext }) => {
  const graph = data || {
    nodes: [
      { id: 'org_1', label: 'Ministry of Defence', type: 'ORGANIZATION', subText: 'Claimed Entity' },
      { id: 'notif_1', label: 'Ref: MOD/2026/145', type: 'NOTIFICATION', subText: 'Claimed ID' },
      { id: 'web_1', label: 'defence-recruitment.com', type: 'WEBSITE', subText: 'Unverified Domain', isHighRisk: true },
      { id: 'email_1', label: 'recruitment@defence-gov.com', type: 'EMAIL', subText: 'Domain Email', isHighRisk: true },
      { id: 'phone_1', label: '+91 98765 43210', type: 'PHONE', subText: 'Helpline Phone' },
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
  };

  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(graph.nodes[0] || null);

  const defaultPositions: Record<string, { x: number; y: number }> = {
    org_1: { x: 280, y: 160 },
    notif_1: { x: 30, y: 30 },
    web_1: { x: 280, y: 10 },
    email_1: { x: 530, y: 30 },
    phone_1: { x: 30, y: 270 },
    job_1: { x: 530, y: 270 },
    payment_1: { x: 130, y: 390 },
    qr_1: { x: 430, y: 390 }
  };

  const flowNodes: Node[] = useMemo(() => {
    return (graph.nodes || []).map((node, idx) => {
      const pos = defaultPositions[node.id] || {
        x: 100 + (idx % 3) * 220,
        y: 60 + Math.floor(idx / 3) * 140
      };
      return {
        id: node.id,
        type: 'customNode',
        position: pos,
        data: { ...node },
        selected: selectedNode?.id === node.id
      };
    });
  }, [graph.nodes, selectedNode]);

  const flowEdges: Edge[] = useMemo(() => {
    const highRiskNodeIds = new Set((graph.nodes || []).filter(n => n.isHighRisk).map(n => n.id));

    return (graph.edges || []).map(edge => {
      const isHighRisk = highRiskNodeIds.has(edge.source) || highRiskNodeIds.has(edge.target);
      return {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.label,
        animated: isHighRisk,
        style: {
          stroke: isHighRisk ? '#ef4444' : '#3b82f6',
          strokeWidth: isHighRisk ? 2.5 : 1.8
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: isHighRisk ? '#ef4444' : '#3b82f6',
          width: 16,
          height: 16
        },
        labelStyle: {
          fill: isHighRisk ? '#991b1b' : '#1e40af',
          fontWeight: 800,
          fontSize: 10,
          fontFamily: 'monospace'
        },
        labelBgStyle: {
          fill: isHighRisk ? '#fef2f2' : '#eff6ff',
          fillOpacity: 0.95
        },
        labelBgPadding: [6, 4],
        labelBgBorderRadius: 6
      };
    });
  }, [graph.edges, graph.nodes]);

  const handleNodeClick = (_: React.MouseEvent, node: Node) => {
    const origNode = graph.nodes.find(n => n.id === node.id);
    if (origNode) {
      setSelectedNode(origNode);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900">Evidence Relationship Graph</h2>
          <p className="text-sm text-slate-500 font-medium mt-1">
            Interactive topology rendering entity connections and flagging suspicious relationships.
          </p>
        </div>
        <button
          onClick={onNext}
          className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 transition-all flex items-center gap-2"
        >
          <span>Next: Official Verification</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8 bg-white rounded-3xl border border-slate-200/80 p-5 shadow-sm h-[520px] flex flex-col justify-between relative overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3 z-10">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wide flex items-center gap-2">
              <Network className="w-4 h-4 text-blue-600" />
              <span>Interactive Graph Topology Canvas</span>
            </span>
            <div className="flex items-center gap-4 text-[11px] font-medium">
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-blue-500" /> Verified / Entity</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse" /> High Risk Connection</span>
            </div>
          </div>

          <div className="w-full h-full relative rounded-2xl overflow-hidden my-2 border border-slate-100">
            <ReactFlow
              nodes={flowNodes}
              edges={flowEdges}
              nodeTypes={nodeTypes}
              onNodeClick={handleNodeClick}
              fitView
              fitViewOptions={{ padding: 0.2 }}
              proOptions={{ hideAttribution: true }}
            >
              <Background color="#cbd5e1" gap={16} size={1} />
              <Controls className="!bg-white !border !border-slate-200 !shadow-sm !rounded-xl overflow-hidden" />
            </ReactFlow>
          </div>

          <p className="text-[11px] text-slate-400 text-center font-medium z-10">
            Pan & zoom or click any node in the interactive topology to inspect relationship vectors
          </p>
        </div>

        <div className="lg:col-span-4 bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm flex flex-col justify-between h-[520px] overflow-y-auto">
          <div>
            <h3 className="text-base font-bold text-slate-900 pb-3 border-b border-slate-100">
              Node Details Inspector
            </h3>

            {selectedNode ? (
              <div className="mt-4 space-y-4">
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/60 space-y-2">
                  <div>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Node ID</span>
                    <p className="text-xs font-bold text-slate-900 font-mono">{selectedNode.id}</p>
                  </div>

                  <div>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mt-2">Label / Value</span>
                    <p className="text-base font-extrabold text-slate-900 break-words">{selectedNode.label}</p>
                  </div>

                  <div>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mt-2">Entity Type</span>
                    <span className="inline-block px-2.5 py-1 rounded-lg bg-blue-100 text-blue-800 font-extrabold text-xs mt-0.5">
                      {selectedNode.type}
                    </span>
                  </div>
                </div>

                <div className={`p-4 rounded-2xl border ${selectedNode.isHighRisk ? 'bg-red-50 border-red-200 text-red-900' : 'bg-emerald-50 border-emerald-200 text-emerald-900'}`}>
                  <h4 className="text-xs font-bold uppercase tracking-wide flex items-center gap-1.5">
                    {selectedNode.isHighRisk ? <AlertTriangle className="w-4 h-4 text-red-600" /> : <CheckCircle2 className="w-4 h-4 text-emerald-600" />}
                    <span>Risk Topology Assessment</span>
                  </h4>
                  <p className="text-xs mt-2 font-medium leading-relaxed">
                    {selectedNode.isHighRisk
                      ? 'HIGH RISK: Suspicious entity vector connected to advance-fee demand, unverified private handle, or spoofed domain.'
                      : 'NORMAL: Entity attribute matches standard expected structural recruitment pattern.'}
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-400 mt-4">Select a node from the left interactive topology canvas to view details.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

