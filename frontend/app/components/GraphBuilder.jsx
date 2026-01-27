'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import ReactFlow, {
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import * as hasura from '../services/hasura';

// Custom Node Component with handles
function CustomNode({ data, id, selected }) {
  return (
    <div
      style={{
        background: selected ? '#667eea' : '#764ba2',
        color: 'white',
        padding: '15px',
        borderRadius: '4px',
        border: selected ? '3px solid #fff' : '2px solid white',
        fontSize: '13px',
        fontWeight: '600',
        textAlign: 'center',
        minWidth: '140px',
        maxWidth: '180px',
        wordWrap: 'break-word',
        boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
        cursor: 'grab',
        transition: 'all 0.2s',
        position: 'relative',
      }}
    >
      <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'normal', lineHeight: '1.4' }}>
        {data.label}
      </div>
      <Handle type="target" position={Position.Top} style={{ background: '#667eea', width: '8px', height: '8px' }} />
      <Handle type="source" position={Position.Bottom} style={{ background: '#667eea', width: '8px', height: '8px' }} />
    </div>
  );
}

export default function GraphBuilder({ initialWorkflowId, onWorkflowChange }) {
  const [nodes, setReactFlowNodes, onNodesChange] = useNodesState([]);
  const [edges, setReactFlowEdges, onEdgesChange] = useEdgesState([]);
  const [dbNodes, setDbNodes] = useState([]);
  const [dbEdges, setDbEdges] = useState([]);
  const [newNodeText, setNewNodeText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [contextMenu, setContextMenu] = useState(null);
  
  // Workflow management
  const [workflows, setWorkflows] = useState([]);
  const [currentWorkflowId, setCurrentWorkflowId] = useState(initialWorkflowId || null);
  const [newWorkflowName, setNewWorkflowName] = useState('');
  const [showNewWorkflowForm, setShowNewWorkflowForm] = useState(false);


  // Load workflows on mount
  useEffect(() => {
    loadWorkflows();
  }, []);

  // Notify parent of workflow changes
  useEffect(() => {
    if (onWorkflowChange) {
      onWorkflowChange(currentWorkflowId);
    }
  }, [currentWorkflowId, onWorkflowChange]);

  // Load current workflow data when workflow changes
  useEffect(() => {
    if (currentWorkflowId) {
      loadWorkflowData(currentWorkflowId);
    }
  }, [currentWorkflowId]);

  const loadWorkflows = async () => {
    try {
      const data = await hasura.getWorkflows();
      const workflowsList = data.workflows || [];
      setWorkflows(workflowsList);
      // Set first workflow as current if none selected
      if (workflowsList.length > 0 && !currentWorkflowId) {
        setCurrentWorkflowId(workflowsList[0].id);
      }
    } catch (err) {
      console.error('Failed to load workflows:', err);
    }
  };

  const loadWorkflowData = async (workflowId) => {
    try {
      const [nodesData, edgesData] = await Promise.all([
        hasura.getNodes(workflowId),
        hasura.getEdges(workflowId)
      ]);
      
      setDbNodes(nodesData.nodes || []);
      setDbEdges(edgesData.edges || []);
    } catch (err) {
      console.error('Failed to load workflow data:', err);
    }
  };

  const createWorkflow = async (e) => {
    e.preventDefault();
    if (!newWorkflowName.trim()) {
      setError('Please enter workflow name');
      return;
    }

    setLoading(true);
    try {
      const data = await hasura.createWorkflow(newWorkflowName.trim(), '');
      const newWorkflow = data.insert_workflows_one;
      
      setWorkflows([...workflows, newWorkflow]);
      setCurrentWorkflowId(newWorkflow.id);
      setNewWorkflowName('');
      setShowNewWorkflowForm(false);
      setSuccess('Workflow created successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message || 'Failed to create workflow');
    } finally {
      setLoading(false);
    }
  };

  // Convert DB data to ReactFlow format with vertical tree layout
  useEffect(() => {
    // Build tree structure from edges
    const buildTreeStructure = () => {
      const nodeMap = new Map(dbNodes.map(n => [n.id, { ...n, children: [] }]));
      const rootNodes = [];
      const visited = new Set();

      // Find root nodes (nodes with no incoming edges)
      dbNodes.forEach(node => {
        const hasIncoming = dbEdges.some(e => e.target_node_id === node.id);
        if (!hasIncoming) {
          rootNodes.push(node.id);
        }
      });

      // If no root nodes found, start with first node
      if (rootNodes.length === 0 && dbNodes.length > 0) {
        rootNodes.push(dbNodes[0].id);
      }

      // Calculate levels and positions using BFS
      const queue = rootNodes.map(id => ({ id, level: 0 }));
      const levels = new Map();

      while (queue.length > 0) {
        const { id, level } = queue.shift();
        if (visited.has(id)) continue;
        visited.add(id);

        if (!levels.has(level)) levels.set(level, []);
        levels.get(level).push(id);

        // Find all children
        dbEdges.forEach(edge => {
          if (edge.source_node_id === id && !visited.has(edge.target_node_id)) {
            queue.push({ id: edge.target_node_id, level: level + 1 });
          }
        });
      }

      // Position nodes: y based on level (top to bottom), x based on position in level (left to right)
      const nodePositions = new Map();
      let levelIndex = 0;
      levels.forEach((nodeIds, level) => {
        const nodesInLevel = nodeIds.length;
        const levelWidth = nodesInLevel * 250;
        const startX = -levelWidth / 2 + 125;

        nodeIds.forEach((nodeId, index) => {
          nodePositions.set(nodeId, {
            x: startX + index * 250,
            y: level * 250,
          });
        });
      });

      // Create ReactFlow nodes with calculated positions
      const reactFlowNodes = dbNodes.map(node => {
        const pos = nodePositions.get(node.id) || { x: 0, y: 0 };
        return {
          id: String(node.id),
          data: { label: node.text },
          position: pos,
          type: 'default',
        };
      });

      return reactFlowNodes;
    };

    const reactFlowNodes = buildTreeStructure();

    const reactFlowEdges = dbEdges.map((edge) => ({
      id: String(edge.id),
      source: String(edge.source_node_id),
      target: String(edge.target_node_id),
      animated: true,
      style: { stroke: '#667eea', strokeWidth: 2 },
      type: 'smoothstep',
    }));

    setReactFlowNodes(reactFlowNodes);
    setReactFlowEdges(reactFlowEdges);
  }, [dbNodes, dbEdges, setReactFlowNodes, setReactFlowEdges]);

  const handleAddNode = async (e) => {
    e.preventDefault();
    if (!newNodeText.trim()) {
      setError('Please enter node text');
      return;
    }

    if (!currentWorkflowId) {
      setError('Please select or create a workflow first');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const data = await hasura.createNode(currentWorkflowId, newNodeText.trim());
      const newNode = data.insert_nodes_one;
      setDbNodes([newNode, ...dbNodes]);
      setNewNodeText('');
      setSuccess('Node created successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create node');
    } finally {
      setLoading(false);
    }
  };

  const onConnect = useCallback(
    async (connection) => {
      if (!currentWorkflowId) {
        setError('Workflow not selected');
        return;
      }

      const sourceId = Number(connection.source);
      const targetId = Number(connection.target);

      if (sourceId === targetId) {
        setError('Cannot connect node to itself');
        setTimeout(() => setError(''), 3000);
        return;
      }

      setLoading(true);
      setError('');

      try {
        const data = await hasura.createEdge(currentWorkflowId, sourceId, targetId);
        const newEdge = data.insert_edges_one;
        setDbEdges([newEdge, ...dbEdges]);
        setSuccess('Connection created!');
        setTimeout(() => setSuccess(''), 3000);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to create edge');
        setTimeout(() => setError(''), 3000);
      } finally {
        setLoading(false);
      }
    },
    [dbEdges, currentWorkflowId]
  );

  const handleNodeContextMenu = (e, nodeId) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY, type: 'node', id: nodeId });
  };

  const handleEdgeContextMenu = (e, edgeId) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY, type: 'edge', id: edgeId });
  };

  const handleDeleteNode = async (nodeId) => {
    if (!confirm('Delete this node? Connected edges will also be deleted.')) return;

    try {
      await hasura.deleteNode(nodeId);
      setDbNodes(dbNodes.filter(n => n.id !== nodeId));
      setDbEdges(dbEdges.filter(e => e.source_node_id !== nodeId && e.target_node_id !== nodeId));
      setSuccess('Node deleted successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete node');
    } finally {
      setContextMenu(null);
    }
  };

  const handleDeleteEdge = async (edgeId) => {
    try {
      await hasura.deleteEdge(edgeId);
      setDbEdges(dbEdges.filter(e => e.id !== edgeId));
      setSuccess('Edge deleted successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete edge');
    } finally {
      setContextMenu(null);
    }
  };


  const getNodeText = (nodeId) => {
    return dbNodes.find(n => n.id === nodeId)?.text || `Item #${nodeId}`;
  };

  const nodeTypes = { default: CustomNode };

  return (
    <div className="graph-builder-wrapper" onClick={() => setContextMenu(null)}>
      <div className="graph-builder-left">
        <div className="controls-panel">
          <h2>🏗️ Knowledge Base</h2>

          {error && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}

          <div className="builder-section">
            <h3>📋 Select Knowledge Base</h3>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
              <select
                value={currentWorkflowId || ''}
                onChange={(e) => setCurrentWorkflowId(Number(e.target.value) || null)}
                className="input-field"
                style={{ flex: 1 }}
              >
                <option value="">Choose knowledge base...</option>
                {workflows.map(w => (
                  <option key={w.id} value={w.id}>{w.name}</option>
                ))}
              </select>
            </div>
            <button
              onClick={() => setShowNewWorkflowForm(!showNewWorkflowForm)}
              className="btn btn-primary"
              style={{ width: '100%' }}
            >
              ➕ New Knowledge Base
            </button>
            {showNewWorkflowForm && (
              <form onSubmit={createWorkflow} style={{ marginTop: '12px' }}>
                <input
                  type="text"
                  placeholder="Knowledge base name..."
                  value={newWorkflowName}
                  onChange={(e) => setNewWorkflowName(e.target.value)}
                  disabled={loading}
                  className="input-field"
                  style={{ marginBottom: '8px' }}
                />
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button type="submit" disabled={loading} className="btn btn-primary" style={{ flex: 1 }}>
                    Create
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowNewWorkflowForm(false)}
                    className="btn"
                    style={{ flex: 1, background: '#999', color: 'white' }}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>

          <div className="builder-section">
            <h3>➕ Add Information</h3>
            <form onSubmit={handleAddNode} className="form">
              <input
                type="text"
                placeholder="Enter information..."
                value={newNodeText}
                onChange={(e) => setNewNodeText(e.target.value)}
                disabled={loading || !currentWorkflowId}
                className="input-field"
              />
              <button type="submit" disabled={loading || !currentWorkflowId} className="btn btn-primary">
                {loading ? 'Adding...' : 'Add Item'}
              </button>
            </form>
          </div>

          <div className="builder-section">
            <h3>📊 Knowledge Stats</h3>
            <div className="graph-stats">
              <div className="stat-card">
                <div className="stat-value">{dbNodes.length}</div>
                <div className="stat-label">Items</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{dbEdges.length}</div>
                <div className="stat-label">Connections</div>
              </div>
            </div>
          </div>

          <div className="builder-section">
            <h3>🎮 How to Use</h3>
            <div className="instructions">
              <ul>
                <li>✏️ Add items using the form above</li>
                <li>🖱️ Drag items to rearrange them</li>
                <li>🔗 Drag from item handles to create connections</li>
                <li>🔍 Scroll to zoom in/out</li>
                <li>📍 Space + drag to pan</li>
                <li>🗑️ Right-click items/connections to delete</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div className="graph-builder-right">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          onNodeContextMenu={(e, node) => handleNodeContextMenu(e, node.id)}
          onEdgeContextMenu={(e, edge) => handleEdgeContextMenu(e, edge.id)}
          fitView
        >
          <Background />
          <Controls />
        </ReactFlow>

        {contextMenu && (
          <div
            className="context-menu"
            style={{ top: `${contextMenu.y}px`, left: `${contextMenu.x}px` }}
          >
            {contextMenu.type === 'node' && (
              <button
                onClick={() => handleDeleteNode(Number(contextMenu.id))}
                className="context-menu-item"
              >
                🗑️ Delete Node
              </button>
            )}
            {contextMenu.type === 'edge' && (
              <button
                onClick={() => handleDeleteEdge(Number(contextMenu.id))}
                className="context-menu-item"
              >
                🗑️ Delete Edge
              </button>
            )}
          </div>
        )}
      </div>

      <style jsx>{`
        .graph-builder-wrapper {
          display: flex;
          height: 100vh;
          gap: 0;
          background: #f5f5f5;
          position: relative;
        }

        .graph-builder-left {
          width: 350px;
          background: white;
          border-right: 2px solid #e0e0e0;
          overflow-y: auto;
          overflow-x: hidden;
          scroll-behavior: smooth;
          box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
        }

        .graph-builder-left::-webkit-scrollbar {
          width: 8px;
        }

        .graph-builder-left::-webkit-scrollbar-track {
          background: #f1f1f1;
        }

        .graph-builder-left::-webkit-scrollbar-thumb {
          background: #ccc;
          border-radius: 4px;
        }

        .graph-builder-left::-webkit-scrollbar-thumb:hover {
          background: #999;
        }

        .controls-panel {
          padding: 20px;
        }

        .controls-panel h2 {
          font-size: 24px;
          color: #333;
          margin: 0 0 20px 0;
          font-weight: 700;
        }

        .builder-section {
          margin-bottom: 20px;
          background: #f9f9f9;
          padding: 15px;
          border-radius: 8px;
          border: 1px solid #e8e8e8;
        }

        .builder-section h3 {
          font-size: 14px;
          color: #555;
          margin: 0 0 12px 0;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .form {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .input-field {
          padding: 10px 12px;
          border: 2px solid #e0e0e0;
          border-radius: 6px;
          font-size: 13px;
          font-family: inherit;
          transition: all 0.2s ease;
        }

        .input-field:focus {
          outline: none;
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .input-field:disabled {
          background-color: #f5f5f5;
          cursor: not-allowed;
        }

        .btn {
          padding: 10px 15px;
          border: none;
          border-radius: 6px;
          font-size: 13px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .btn-primary {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .btn-primary:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .alert {
          padding: 12px 14px;
          border-radius: 6px;
          margin-bottom: 15px;
          font-weight: 500;
          font-size: 13px;
          animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .alert-error {
          background-color: #ffe0e0;
          color: #d32f2f;
          border-left: 4px solid #d32f2f;
        }

        .alert-success {
          background-color: #e0ffe0;
          color: #388e3c;
          border-left: 4px solid #388e3c;
        }

        .graph-stats {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 10px;
        }

        .stat-card {
          background: white;
          padding: 12px;
          border-radius: 6px;
          text-align: center;
          border: 1px solid #e0e0e0;
        }

        .stat-value {
          font-size: 24px;
          font-weight: 700;
          color: #667eea;
        }

        .stat-label {
          font-size: 12px;
          color: #999;
          margin-top: 4px;
        }

        .instructions {
          background: white;
          padding: 12px;
          border-radius: 6px;
          border-left: 3px solid #667eea;
        }

        .instructions ul {
          margin: 0;
          padding: 0 0 0 18px;
          font-size: 12px;
          color: #666;
          line-height: 1.6;
        }

        .instructions li {
          margin: 6px 0;
        }

        .graph-builder-right {
          flex: 1;
          background: white;
          position: relative;
        }

        .context-menu {
          position: fixed;
          background: white;
          border: 1px solid #ddd;
          border-radius: 6px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          z-index: 1000;
          padding: 4px 0;
          min-width: 150px;
        }

        .context-menu-item {
          display: block;
          width: 100%;
          padding: 10px 16px;
          border: none;
          background: white;
          color: #333;
          cursor: pointer;
          font-size: 13px;
          font-weight: 500;
          text-align: left;
          transition: all 0.2s ease;
        }

        .context-menu-item:hover {
          background: #f0f0f0;
          color: #d32f2f;
        }

        .context-menu-item:first-child {
          border-radius: 6px 6px 0 0;
        }

        .context-menu-item:last-child {
          border-radius: 0 0 6px 6px;
        }

        @media (max-width: 768px) {
          .graph-builder-wrapper {
            flex-direction: column;
          }

          .graph-builder-left {
            width: 100%;
            border-right: none;
            border-bottom: 2px solid #e0e0e0;
            max-height: 250px;
          }

          .graph-builder-right {
            min-height: 400px;
          }
        }
      `}</style>
    </div>
  );
}
