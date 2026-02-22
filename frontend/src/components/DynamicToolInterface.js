import React, { useState, useEffect, useRef, useCallback } from 'react';
import { FiSend, FiCpu, FiBookOpen, FiSearch, FiCode, FiLayers, FiUsers, FiSave } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { apiService } from '../services/api';
import '../styles/DynamicToolInterface.css';

const TOOL_CONFIGS = {
  domain_discovery: { icon: <FiLayers />, title: 'Domain Discovery', placeholder: 'Enter a research field (e.g., Quantum ML)...' },
  paper_summarizer: { icon: <FiBookOpen />, title: 'Paper Summarizer', placeholder: 'Enter paper title, URL (arXiv), or abstract...' },
  professor_finder: { icon: <FiUsers />, title: 'Professor Finder', placeholder: 'Search for experts in (e.g., Computer Vision)...' },
  dataset_hub: { icon: <FiSearch />, title: 'Dataset Hub', placeholder: 'Describe the data you need...' },
  pretrained_models: { icon: <FiCpu />, title: 'Model Architect', placeholder: 'Search/Compare models (e.g., Llama-3 vs Mistral)...' },
  generate_code: { icon: <FiCode />, title: 'Research Engineer', placeholder: 'Describe the research code needed...' }
};

const DynamicToolInterface = ({ toolId, isAuthenticated }) => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [workspaces, setWorkspaces] = useState([]);
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState('');
  const messagesEndRef = useRef(null);
  
  const config = TOOL_CONFIGS[toolId] || { icon: <FiCpu />, title: 'Research Tool', placeholder: 'Enter query...' };

  const formatContent = (content, tool) => {
    // Specialized formatting for different tools
    if (tool === 'paper_summarizer') {
      const sections = content.split('\n\n');
      return (
        <div className="specialized-summary">
          <div className="summary-tldr"><strong>Summary TL;DR:</strong> {sections[0]}</div>
          <div className="summary-details">
            {sections.slice(1).map((s, i) => <div key={i} className="summary-point">{s}</div>)}
          </div>
        </div>
      );
    }
    if (tool === 'generate_code') {
      return <div className="specialized-code">{content}</div>;
    }
    if (tool === 'dataset_hub') {
      return (
        <div className="specialized-data">
          <div className="data-header">🔍 Dataset Discovery Report</div>
          <div className="data-body">{content}</div>
        </div>
      );
    }
    return content;
  };

  const loadMessages = useCallback(async (wsId) => {
    if (!wsId) return;
    const result = await apiService.getWorkspaceMessages(wsId);
    if (result.success) {
      const filtered = (result.data.messages || []).filter(m => 
        m.tool_type === toolId || !m.tool_type
      );
      setMessages(filtered.map(m => ({ role: m.role, content: m.content, tool_type: m.tool_type })));
    }
  }, [toolId]);

  const handleWorkspaceChange = (e) => {
    const wsId = e.target.value;
    setSelectedWorkspaceId(wsId);
    setMessages([]);
    loadMessages(wsId);
  };

  useEffect(() => {
    if (isAuthenticated) {
      apiService.getWorkspaces().then(res => {
        if (res.success) {
          const list = res.data.workspaces || [];
          setWorkspaces(list);
          if (list.length > 0) {
            const initialWs = String(list[0].id);
            setSelectedWorkspaceId(initialWs);
            loadMessages(initialWs);
          }
        }
      });
    }
  }, [isAuthenticated, loadMessages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim() || isLoading) return;

    const userMsg = query.trim();
    setQuery('');
    setError('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsLoading(true);

    const result = await apiService.query(
      userMsg, 
      messages, 
      selectedWorkspaceId || null, 
      toolId
    );

    if (result.success) {
      setMessages(prev => [...prev, { role: 'assistant', content: result.data.response, tool_type: toolId }]);
    } else {
      setError(result.error || 'Request failed');
    }
    setIsLoading(false);
  };

  const handleSaveToWorkspace = async (content) => {
    if (!selectedWorkspaceId) {
      alert('Please select a workspace first!');
      return;
    }
    const title = window.prompt('Enter resource title:', `Result from ${config.title}`);
    if (!title) return;

    const res = await apiService.createWorkspaceResource(selectedWorkspaceId, title, content, 'tool_result');
    if (res.success) {
      alert('Result saved to workspace!');
    } else {
      alert('Failed to save.');
    }
  };

  return (
    <div className="dynamic-tool-container">
      <div className="tool-sidebar">
        <div className="tool-info">
          <div className="tool-icon-large">{config.icon}</div>
          <h3>{config.title}</h3>
          <p className="tool-desc">Specialized AI agent focusing only on {config.title.toLowerCase()} tasks.</p>
        </div>

        <div className="tool-context-picker">
          <label>Target Workspace:</label>
          <select 
            value={selectedWorkspaceId} 
            onChange={handleWorkspaceChange}
            className="win-input"
          >
            <option value="">Independent Study</option>
            {workspaces.map(ws => (
              <option key={ws.id} value={ws.id}>{ws.name}</option>
            ))}
          </select>
          <small>Responses will consider this workspace's resources & memory.</small>
        </div>
      </div>

      <div className="tool-main">
        <div className="tool-messages">
          {messages.length === 0 && (
            <div className="tool-welcome">
              <div className="welcome-orb"></div>
              <h4>How can I help you today?</h4>
              <p>Specialized context is active. Ask me anything related to {config.title.toLowerCase()}.</p>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`tool-msg ${m.role}`}>
              <div className="msg-header">
                <strong>{m.role === 'user' ? 'YOU' : config.title.toUpperCase()}</strong>
                {m.role === 'assistant' && (
                  <button onClick={() => handleSaveToWorkspace(m.content)} className="msg-save-btn" title="Save to Workspace">
                    <FiSave />
                  </button>
                )}
              </div>
              <div className="msg-content">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ node, inline, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '');
                      return !inline && match ? (
                        <SyntaxHighlighter style={vscDarkPlus} language={match[1]} PreTag="div" {...props}>
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={className} {...props}>{children}</code>
                      );
                    }
                  }}
                >
                  {m.role === 'assistant' ? formatContent(m.content, m.tool_type || toolId) : m.content}
                </ReactMarkdown>
              </div>
            </div>
          ))}
          {isLoading && <div className="loading-dots"><span>.</span><span>.</span><span>.</span></div>}
          {error && <div className="tool-error">{error}</div>}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSend} className="tool-input-area">
          <input 
            type="text" 
            className="win-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={config.placeholder}
            disabled={isLoading}
          />
          <button type="submit" className="win-btn-classic" disabled={isLoading}>
            <FiSend /> Invoke
          </button>
        </form>
      </div>
    </div>
  );
};

export default DynamicToolInterface;
