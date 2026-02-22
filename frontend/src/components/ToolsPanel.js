import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import '../styles/ToolsPanel.css';

const FALLBACK_TOOLS = [
  { id: 'domain_discovery', name: 'Domain Discovery', description: 'Find your research niche by exploring emerging fields', capabilities: ['Topics', 'Subfields', 'Trends'] },
  { id: 'paper_summarizer', name: 'Paper Summarizer', description: 'Discover and summarize research papers from ArXiv', capabilities: ['Search', 'Summary', 'Citations'] },
  { id: 'professor_finder', name: 'Professor Finder', description: 'Find researchers and professors by field and institution', capabilities: ['Search', 'Institution', 'Field'] },
  { id: 'dataset_hub', name: 'Dataset Hub', description: 'Access curated datasets from HuggingFace', capabilities: ['Search', 'Download', 'Details'] },
  { id: 'pretrained_models', name: 'Pretrained Models', description: 'Discover state-of-the-art pretrained models', capabilities: ['Search', 'Compare', 'Use'] },
  { id: 'generate_code', name: 'Code Generator', description: 'Generate code snippets and solutions', capabilities: ['Generate', 'Explain', 'Examples'] },
];

const ToolsPanel = ({ onToolSelect }) => {
  const [tools, setTools] = useState(FALLBACK_TOOLS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTools();
  }, []);

  const fetchTools = async () => {
    setLoading(true);
    setError('');
    const result = await apiService.getTools();
    if (result.success && result.data) {
      // Accept both { tools: [...] } and plain array responses
      const fetchedTools = Array.isArray(result.data)
        ? result.data
        : (result.data.tools || result.data.data || []);
      if (fetchedTools.length > 0) {
        setTools(fetchedTools);
      }
    } else if (result.error) {
      setError(result.error);
    }
    setLoading(false);
  };

  if (loading) return <div className="tools-panel"><p>Loading tools...</p></div>;
  // If API failed but we still have fallback tools, show them with a soft notice
  const showNotice = Boolean(error && tools.length > 0);

  return (
    <div className="tools-panel">
      <h3>Available Research Tools</h3>
      {showNotice && <div className="tools-notice">Showing default tools (backend unreachable).</div>}
      <div className="tools-grid">
        {tools.map((tool, idx) => (
          <div 
            key={idx} 
            className="tool-card win-btn-classic" 
            style={{ textAlign: 'left', padding: '15px', display: 'flex', flexDirection: 'column' }}
            onClick={() => onToolSelect && onToolSelect(tool.id || tool.name.toLowerCase().replace(' ', '_'))}
          >
            <h4>{tool.name}</h4>
            <p>{tool.description}</p>
            {tool.capabilities && (
              <div className="capabilities">
                {tool.capabilities.map((cap, i) => (
                  <span key={i} className="capability-tag">{cap}</span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ToolsPanel;
