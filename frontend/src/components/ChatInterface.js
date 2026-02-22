import React, { useState, useEffect, useRef, useCallback } from 'react';
import { FiCopy, FiFolderPlus, FiTrash2, FiDatabase } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { apiService } from '../services/api';
import '../styles/ChatInterface.css';

const ChatInterface = ({ isAuthenticated = false }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [workspaces, setWorkspaces] = useState([]);
  const [workspaceId, setWorkspaceId] = useState('');
  const [workspaceName, setWorkspaceName] = useState('');
  const [memoryKey, setMemoryKey] = useState('');
  const [memoryValue, setMemoryValue] = useState('');
  const [memoryItems, setMemoryItems] = useState([]);
  const [isWorkspaceLoading, setIsWorkspaceLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadWorkspaces = useCallback(async () => {
    setIsWorkspaceLoading(true);
    const result = await apiService.getWorkspaces();
    if (result.success) {
      const list = result.data.workspaces || [];
      setWorkspaces(list);
      if (!workspaceId && list.length > 0) {
        setWorkspaceId(String(list[0].id));
      }
    }
    setIsWorkspaceLoading(false);
  }, [workspaceId]);

  useEffect(() => {
    if (isAuthenticated) {
      loadWorkspaces();
    } else {
      setWorkspaces([]);
      setWorkspaceId('');
      setMessages([]);
      setMemoryItems([]);
    }
  }, [isAuthenticated, loadWorkspaces]);

  const loadWorkspaceData = useCallback(async (id) => {
    const [messagesResult, memoryResult] = await Promise.all([
      apiService.getWorkspaceMessages(id),
      apiService.getWorkspaceMemory(id),
    ]);

    if (messagesResult.success) {
      const msgs = (messagesResult.data.messages || []).map((m) => ({
        role: m.role,
        content: m.content,
        tool_type: m.tool_type, // Capture the tool type
      }));
      setMessages(msgs);
    }

    if (memoryResult.success) {
      setMemoryItems(memoryResult.data.memory || []);
    }
  }, []);

  useEffect(() => {
    if (workspaceId && isAuthenticated) {
      loadWorkspaceData(workspaceId);
    } else if (!workspaceId) {
      setMessages([]);
      setMemoryItems([]);
    }
  }, [workspaceId, isAuthenticated, loadWorkspaceData]);

  const handleCreateWorkspace = async () => {
    if (!workspaceName.trim()) return;
    const result = await apiService.createWorkspace(workspaceName.trim());
    if (result.success) {
      setWorkspaceName('');
      await loadWorkspaces();
    } else {
      setError(result.error || 'Failed to create workspace');
    }
  };

  const handleAddMemory = async () => {
    if (!workspaceId || !memoryKey.trim() || !memoryValue.trim()) return;
    const result = await apiService.addWorkspaceMemory(
      workspaceId,
      memoryKey.trim(),
      memoryValue.trim()
    );
    if (result.success) {
      setMemoryKey('');
      setMemoryValue('');
      const updated = await apiService.getWorkspaceMemory(workspaceId);
      if (updated.success) {
        setMemoryItems(updated.data.memory || []);
      }
    } else {
      setError(result.error || 'Failed to add memory item');
    }
  };

  const handleDeleteMemory = async (key) => {
    if (!workspaceId) return;
    const result = await apiService.deleteWorkspaceMemory(workspaceId, key);
    if (result.success) {
      setMemoryItems((prev) => prev.filter((item) => item.key !== key));
    } else {
      setError(result.error || 'Failed to delete memory item');
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setError('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await apiService.query(userMessage, messages, workspaceId || null);

      if (response.success && response.data) {
        const assistantResponse = response.data.response || response.data.content || 'No response received';
        setMessages((prev) => [...prev, { role: 'assistant', content: assistantResponse }]);
      } else {
        const errorMsg = response.error || 'Failed to get response. Make sure backend is running on http://localhost:8000';
        setError(errorMsg);
        setMessages((prev) => prev.slice(0, -1));
      }
    } catch (err) {
      setError('Connection error. Is the backend running?');
      setMessages((prev) => prev.slice(0, -1));
    }
    setIsLoading(false);
  };

  const handleSaveResource = async (content) => {
    if (!workspaceId) {
      setError('Please select a workspace first!');
      return;
    }

    const title = window.prompt('Enter a title for this resource:', 'Saved Snippet');
    if (!title) return;

    const result = await apiService.createWorkspaceResource(workspaceId, title, content, 'note');
    if (result.success) {
      alert('Classic OS Message: Resource saved to workspace!');
    } else {
      setError(result.error || 'Failed to save resource');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const downloadChat = async () => {
    const result = await apiService.exportChat('json');
    if (result.success) {
      const dataStr = JSON.stringify(result.data, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `chat_${new Date().toISOString().split('T')[0]}.json`;
      link.click();
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-menubar">
        <button className="menu-item" type="button">File</button>
        <button className="menu-item" type="button">Edit</button>
        <button className="menu-item" type="button">View</button>
        <button className="menu-item" type="button">Help</button>
        <button className="menu-item export-btn" type="button" onClick={downloadChat}>
          Export
        </button>
      </div>

      {isAuthenticated && (
        <div className="workspace-bar">
          <div className="workspace-select">
            <label>
              <FiDatabase /> Workspace
            </label>
            <select value={workspaceId} onChange={(e) => setWorkspaceId(e.target.value)}>
              <option value="">No workspace</option>
              {workspaces.map((ws) => (
                <option key={ws.id} value={ws.id}>
                  {ws.name}
                </option>
              ))}
            </select>
            {isWorkspaceLoading && <span className="workspace-loading">Loading...</span>}
          </div>

          <div className="workspace-create">
            <input
              type="text"
              value={workspaceName}
              onChange={(e) => setWorkspaceName(e.target.value)}
              placeholder="New workspace name"
              className="workspace-input"
            />
            <button
              className="workspace-btn"
              onClick={handleCreateWorkspace}
              disabled={!workspaceName.trim()}
            >
              <FiFolderPlus /> Create
            </button>
          </div>
        </div>
      )}

      {workspaceId && (
        <div className="memory-panel">
          <div className="memory-header">Workspace Memory</div>
          <div className="memory-list">
            {memoryItems.length === 0 && <div className="memory-empty">No memory items yet</div>}
            {memoryItems.map((item) => (
              <div key={item.key} className="memory-item">
                <div className="memory-text">
                  <div className="memory-key">{item.key}</div>
                  <div className="memory-value">{item.value}</div>
                </div>
                <button
                  className="memory-delete"
                  onClick={() => handleDeleteMemory(item.key)}
                  title="Delete memory"
                >
                  <FiTrash2 />
                </button>
              </div>
            ))}
          </div>

          <div className="memory-inputs">
            <input
              type="text"
              value={memoryKey}
              onChange={(e) => setMemoryKey(e.target.value)}
              placeholder="Memory key (e.g., focus)"
            />
            <input
              type="text"
              value={memoryValue}
              onChange={(e) => setMemoryValue(e.target.value)}
              placeholder="Memory value (e.g., summarize with citations)"
            />
            <button
              className="memory-add"
              onClick={handleAddMemory}
              disabled={!memoryKey.trim() || !memoryValue.trim()}
            >
              Add
            </button>
          </div>
        </div>
      )}

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <h3>Start Your Research Journey</h3>
            <p>Ask questions about papers, code, datasets, and more</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`message message-${msg.role}`}>
              <div className="message-label">
                {msg.tool_type ? msg.tool_type.substring(0, 3).toUpperCase() : (msg.role === 'user' ? 'USR' : 'SYS')}
              </div>
              <div className="message-content">
                {msg.tool_type && (
                  <div className="tool-badge">
                    ⚡ {msg.tool_type.replace('_', ' ')}
                  </div>
                )}
                <div className="message-text">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      code({ node, inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || '');
                        return !inline && match ? (
                          <SyntaxHighlighter
                            style={vscDarkPlus}
                            language={match[1]}
                            PreTag="div"
                            {...props}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        ) : (
                          <code className={className} {...props}>
                            {children}
                          </code>
                        );
                      },
                      a({ node, children, ...props }) {
                        return (
                          <a {...props} target="_blank" rel="noopener noreferrer">
                            {children}
                          </a>
                        );
                      },
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
              </div>
              <div className="message-actions">
                <button
                  className="copy-btn"
                  onClick={() => copyToClipboard(msg.content)}
                  title="Copy message"
                >
                  <FiCopy />
                </button>
                {msg.role === 'assistant' && (
                  <button
                    className="copy-btn save-resource-btn"
                    onClick={() => handleSaveResource(msg.content)}
                    title="Save to Workspace"
                  >
                    <FiFolderPlus />
                  </button>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message message-assistant">
            <div className="message-content">
              <div className="typing-animation">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        {error && <div className="error-message">{error}</div>}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} className="chat-input-form">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Enter research query..."
          disabled={isLoading}
          className="chat-input"
        />
        <button type="submit" disabled={isLoading || !inputValue.trim()} className="send-btn">
          {isLoading ? 'WORKING' : 'RUN'}
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;
