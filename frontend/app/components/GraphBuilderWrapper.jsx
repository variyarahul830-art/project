'use client';

import { ReactFlowProvider } from 'reactflow';
import GraphBuilder from './GraphBuilder';

export default function GraphBuilderWrapper({ workflowId, onWorkflowChange }) {
  return (
    <ReactFlowProvider>
      <GraphBuilder initialWorkflowId={workflowId} onWorkflowChange={onWorkflowChange} />
    </ReactFlowProvider>
  );
}
