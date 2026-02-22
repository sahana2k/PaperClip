import React, { useState, useEffect, useCallback } from 'react';
import { 
  FiFolder, 
  FiTrash2, 
  FiFileText, 
  FiMessageSquare, 
  FiArrowLeft,
  FiDatabase
} from 'react-icons/fi';
import { apiService } from '../services/api';
import '../styles/WorkspaceManager.css';

const WorkspaceManager = ({ isAuthenticated }) => {
  const [workspaces, setWorkspaces] = useState([]);
  const [activeWorkspace, setActiveWorkspace] = useState(null);
  const [newWorkspaceName, setNewWorkspaceName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [workspaceData, setWorkspaceData] = useState({
    messages: [],
    resources: [],
    memory: []
  });
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'details'
  const [detailTab, setDetailTab] = useState('resources'); // 'resources', 'chats', 'memory'

  const loadWorkspaces = useCallback(async () => {
    setIsLoading(true);
    const result = await apiService.getWorkspaces();
    if (result.success) {
      setWorkspaces(result.data.workspaces || []);
    } else {
      setError(result.error || 'Failed to load workspaces');
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      loadWorkspaces();
    }
  }, [isAuthenticated, loadWorkspaces]);

  const handleCreateWorkspace = async (e) => {
    e.preventDefault();
    if (!newWorkspaceName.trim()) return;

    setIsLoading(true);
    const result = await apiService.createWorkspace(newWorkspaceName.trim());
    if (result.success) {
      setNewWorkspaceName('');
      await loadWorkspaces();
      if (result.data) {
          selectWorkspace(result.data);
      }
    } else {
      setError(result.error || 'Failed to create workspace');
    }
    setIsLoading(false);
  };

  const handleDeleteWorkspace = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm('Classic OS Prompt: Delete this workspace and all its memory forever?')) return;

    setIsLoading(true);
    const result = await apiService.deleteWorkspace(id);
    if (result.success) {
      if (activeWorkspace?.id === id) {
        setActiveWorkspace(null);
        setViewMode('list');
      }
      await loadWorkspaces();
    } else {
      setError(result.error || 'Failed to delete workspace');
    }
    setIsLoading(false);
  };

  const selectWorkspace = async (ws) => {
    setActiveWorkspace(ws);
    setViewMode('details');
    setIsLoading(true);
    
    try {
      const [msgRes, resRes, memRes] = await Promise.all([
        apiService.getWorkspaceMessages(ws.id),
        apiService.getWorkspaceResources(ws.id),
        apiService.getWorkspaceMemory(ws.id)
      ]);

      setWorkspaceData({
        messages: msgRes.success ? msgRes.data.messages : [],
        resources: resRes.success ? resRes.data.resources : [],
        memory: memRes.success ? memRes.data.memory : []
      });
    } catch (err) {
      setError('Failed to load workspace contents.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) return <div className="p-4">Please log in to manage workspaces.</div>;

  return (
    <div className="workspace-manager">
      <div className="workspace-header">
        <div className="workspace-title">
          <FiFolder />
          <span>{viewMode === 'list' ? 'Workspace Explorer' : activeWorkspace?.name}</span>
        </div>
        {viewMode === 'details' && (
          <button className="win-btn-classic" onClick={() => setViewMode('list')}>
            <FiArrowLeft /> Back
          </button>
        )}
      </div>

      <div className="workspace-content">
        {error && <div className="auth-error" style={{ padding: '4px', margin: '4px' }}>{error}</div>}

        {viewMode === 'list' ? (
          <>
            <form onSubmit={handleCreateWorkspace} className="workspace-create-form">
              <input
                type="text"
                className="win-input"
                placeholder="Name your new workspace..."
                value={newWorkspaceName}
                onChange={(e) => setNewWorkspaceName(e.target.value)}
              />
              <button type="submit" disabled={isLoading} className="win-btn-classic">
                Create
              </button>
            </form>

            <div className="workspace-grid">
              {workspaces.map(ws => (
                <div 
                  key={ws.id} 
                  className="workspace-card"
                  onClick={() => selectWorkspace(ws)}
                >
                  <FiFolder className="workspace-card-icon" />
                  <span className="workspace-card-name">{ws.name}</span>
                  <button 
                    className="win-btn-classic"
                    style={{ padding: '2px', marginTop: '4px' }}
                    onClick={(e) => handleDeleteWorkspace(e, ws.id)}
                  >
                    <FiTrash2 size={12} />
                  </button>
                </div>
              ))}
              {workspaces.length === 0 && !isLoading && (
                <div style={{ gridColumn: '1/-1', textAlign: 'center', opacity: 0.5, marginTop: '20px' }}>
                  No workspaces found. Create one to begin.
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="workspace-details">
            <div className="workspace-sidebar">
              <button 
                className={`sidebar-tab ${detailTab === 'resources' ? 'active' : ''}`}
                onClick={() => setDetailTab('resources')}
              >
                <FiFileText /> Resources
              </button>
              <button 
                className={`sidebar-tab ${detailTab === 'chats' ? 'active' : ''}`}
                onClick={() => setDetailTab('chats')}
              >
                <FiMessageSquare /> Messages
              </button>
              <button 
                className={`sidebar-tab ${detailTab === 'memory' ? 'active' : ''}`}
                onClick={() => setDetailTab('memory')}
              >
                <FiDatabase /> Memory
              </button>
            </div>

            <div className="workspace-main">
              {isLoading ? (
                <div>Loading workspace data...</div>
              ) : (
                <>
                  {detailTab === 'resources' && (
                    <div className="resources-list">
                      <h4 style={{ margin: '0 0 8px 0', borderBottom: '1px solid #c0c0c0' }}>Files & Resources</h4>
                      {workspaceData.resources.length > 0 ? (
                        workspaceData.resources.map((res, i) => (
                          <div key={i} className="resource-item">
                            <span className="resource-type">[{res.type}]</span>
                            <span className="resource-title">{res.title}</span>
                          </div>
                        ))
                      ) : (
                        <p style={{ opacity: 0.7, fontSize: '0.8rem' }}>No resources saved yet.</p>
                      )}
                    </div>
                  )}

                  {detailTab === 'chats' && (
                    <div className="chats-list">
                      <h4 style={{ margin: '0 0 8px 0', borderBottom: '1px solid #c0c0c0' }}>Recent Activity</h4>
                      {workspaceData.messages.length > 0 ? (
                        workspaceData.messages.slice(-10).map((msg, i) => (
                          <div key={i} className={`chat-bubble-tiny ${msg.role}`}>
                            <strong>{msg.role === 'user' ? 'YOU' : 'AI'}:</strong> {msg.content.substring(0, 100)}...
                          </div>
                        ))
                      ) : (
                        <p style={{ opacity: 0.7, fontSize: '0.8rem' }}>No chat history.</p>
                      )}
                    </div>
                  )}

                  {detailTab === 'memory' && (
                    <div className="memory-list">
                      <h4 style={{ margin: '0 0 8px 0', borderBottom: '1px solid #c0c0c0' }}>System Context</h4>
                      {workspaceData.memory.length > 0 ? (
                        workspaceData.memory.map((item, i) => (
                          <div key={i} className="resource-item">
                            <strong style={{ fontSize: '0.75rem' }}>{item.key}:</strong> 
                            <span style={{ fontSize: '0.75rem', marginLeft: '4px' }}>{item.value}</span>
                          </div>
                        ))
                      ) : (
                        <p style={{ opacity: 0.7, fontSize: '0.8rem' }}>No memory facts extracted.</p>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkspaceManager;
