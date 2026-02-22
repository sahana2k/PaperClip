import React, { useState, useEffect, useCallback } from 'react';
import { FiCopy, FiDownload, FiDatabase } from 'react-icons/fi';
import MermaidRenderer from './MermaidRenderer';
import { apiService } from '../services/api';
import '../styles/ResearchPanel.css';

const ResearchPanel = ({ isAuthenticated = false }) => {
  const [activeTab, setActiveTab] = useState('mindmap');
  const [topic, setTopic] = useState('');
  const [goal, setGoal] = useState('');
  const [constraints, setConstraints] = useState('');
  const [ideaFocus, setIdeaFocus] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [workspaces, setWorkspaces] = useState([]);
  const [workspaceId, setWorkspaceId] = useState('');
  const [isWorkspaceLoading, setIsWorkspaceLoading] = useState(false);
  
  // Data states
  const [mindMapData, setMindMapData] = useState(null);
  const [podcastData, setPodcastData] = useState(null);
  const [citationsData, setCitationsData] = useState(null);
  const [ideationData, setIdeationData] = useState(null);
  const [experimentData, setExperimentData] = useState(null);
  const [ideationHistory, setIdeationHistory] = useState([]);
  const [experimentHistory, setExperimentHistory] = useState([]);

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
      setIdeationHistory([]);
      setExperimentHistory([]);
    }
  }, [isAuthenticated, loadWorkspaces]);

  const loadPhase4History = useCallback(async (id) => {
    const [ideationResult, experimentResult] = await Promise.all([
      apiService.getWorkspaceIdeation(id),
      apiService.getWorkspaceExperiments(id),
    ]);

    if (ideationResult.success) {
      setIdeationHistory(ideationResult.data.items || []);
    }

    if (experimentResult.success) {
      setExperimentHistory(experimentResult.data.items || []);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated && workspaceId) {
      loadPhase4History(workspaceId);
    } else {
      setIdeationHistory([]);
      setExperimentHistory([]);
    }
  }, [isAuthenticated, workspaceId, loadPhase4History]);

  const renderValue = (value) => {
    if (Array.isArray(value)) {
      return (
        <ul>
          {value.map((item, idx) => (
            <li key={idx}>{item}</li>
          ))}
        </ul>
      );
    }
    if (typeof value === 'string' && value.trim()) {
      return <p>{value}</p>;
    }
    return <p className="empty-field">Not provided</p>;
  };

  const handleUseIdeationItem = (item) => {
    setIdeationData({
      topic: item.topic,
      ...item.payload,
      saved: item,
    });
  };

  const handleUseExperimentItem = (item) => {
    const payload = item.payload || {};
    setExperimentData({
      topic: item.topic,
      ...payload,
      plan: payload.plan || payload,
      saved: item,
    });
  };

  const handleGenerate = async () => {
    if (!topic.trim()) {
      setError('Please enter a research topic');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      if (activeTab === 'mindmap') {
        const result = await apiService.generateMindMap(topic);
        if (result.success) {
          setMindMapData(result.data);
        } else {
          setError(result.error);
        }
      } else if (activeTab === 'podcast') {
        const result = await apiService.generatePodcast(topic);
        if (result.success) {
          setPodcastData(result.data);
        } else {
          setError(result.error);
        }
      } else if (activeTab === 'citations') {
        const result = await apiService.getCitations(topic);
        if (result.success) {
          setCitationsData(result.data);
        } else {
          setError(result.error);
        }
      } else if (activeTab === 'ideation') {
        const result = await apiService.generateIdeation(
          topic,
          goal || null,
          constraints || null,
          workspaceId || null
        );
        if (result.success) {
          const payload = result.data.ideation || {};
          setIdeationData({
            topic: result.data.topic,
            ...payload,
            saved: result.data.saved || null,
          });
          if (workspaceId) {
            loadPhase4History(workspaceId);
          }
        } else {
          setError(result.error);
        }
      } else if (activeTab === 'experiment') {
        const result = await apiService.generateExperimentDesign(
          topic,
          ideaFocus || null,
          constraints || null,
          workspaceId || null
        );
        if (result.success) {
          const payload = result.data.experiment || {};
          setExperimentData({
            topic: result.data.topic,
            ...payload,
            plan: payload.plan || payload,
            saved: result.data.saved || null,
          });
          if (workspaceId) {
            loadPhase4History(workspaceId);
          }
        } else {
          setError(result.error);
        }
      }
    } catch (err) {
      setError('Failed to generate research content');
    }
    setIsLoading(false);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const downloadBibTeX = () => {
    if (!citationsData?.bibtex_entries) return;
    
    const bibContent = citationsData.bibtex_entries.join('\n\n');
    const blob = new Blob([bibContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${topic.replace(/\s+/g, '_')}_citations.bib`;
    link.click();
  };

  const hasActiveContent =
    (activeTab === 'mindmap' && mindMapData) ||
    (activeTab === 'podcast' && podcastData) ||
    (activeTab === 'citations' && citationsData) ||
    (activeTab === 'ideation' && ideationData) ||
    (activeTab === 'experiment' && experimentData);

  return (
    <div className="research-panel window-shell">
      <div className="panel-menubar">
        <button
          className={`menu-item ${activeTab === 'mindmap' ? 'active' : ''}`}
          onClick={() => setActiveTab('mindmap')}
        >
          Mind Map
        </button>
        <button
          className={`menu-item ${activeTab === 'podcast' ? 'active' : ''}`}
          onClick={() => setActiveTab('podcast')}
        >
          Podcast Script
        </button>
        <button
          className={`menu-item ${activeTab === 'citations' ? 'active' : ''}`}
          onClick={() => setActiveTab('citations')}
        >
          Citations
        </button>
        <button
          className={`menu-item ${activeTab === 'ideation' ? 'active' : ''}`}
          onClick={() => setActiveTab('ideation')}
        >
          Ideation
        </button>
        <button
          className={`menu-item ${activeTab === 'experiment' ? 'active' : ''}`}
          onClick={() => setActiveTab('experiment')}
        >
          Experiment Design
        </button>
      </div>

      <div className="panel-body">
        <div className="research-header">
          <h2>PAPERCLIP</h2>
          <p>A.I. RESEARCH OS v1.0</p>
        </div>

        {isAuthenticated && (
          <div className="research-workspace">
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
        )}

        <div className="research-input-section">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter research topic (e.g., 'transformers in NLP')"
            className="research-input"
            onKeyPress={(e) => e.key === 'Enter' && handleGenerate()}
          />
          <button
            onClick={handleGenerate}
            disabled={isLoading || !topic.trim()}
            className="generate-btn"
          >
            {isLoading ? 'Generating...' : 'Generate'}
          </button>
        </div>

        {activeTab === 'ideation' && (
          <div className="research-subinputs">
            <input
              type="text"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="Goal (optional)"
            />
            <input
              type="text"
              value={constraints}
              onChange={(e) => setConstraints(e.target.value)}
              placeholder="Constraints (optional)"
            />
          </div>
        )}

        {activeTab === 'experiment' && (
          <div className="research-subinputs">
            <input
              type="text"
              value={ideaFocus}
              onChange={(e) => setIdeaFocus(e.target.value)}
              placeholder="Idea or hypothesis (optional)"
            />
            <input
              type="text"
              value={constraints}
              onChange={(e) => setConstraints(e.target.value)}
              placeholder="Constraints (optional)"
            />
          </div>
        )}

        {error && <div className="error-message">{error}</div>}

        <div className="research-content">
        {activeTab === 'mindmap' && mindMapData && (
          <div className="content-section">
            <div className="section-header">
              <h3>Mind Map: {mindMapData.topic}</h3>
              <button
                onClick={() => copyToClipboard(mindMapData.mermaid_code)}
                className="action-btn"
                title="Copy Mermaid code"
              >
                <FiCopy /> Copy Code
              </button>
            </div>
            <MermaidRenderer code={mindMapData.mermaid_code} id="research-mindmap" />
            <p className="meta-info">Generated from {mindMapData.papers_count} papers</p>
          </div>
        )}

        {activeTab === 'podcast' && podcastData && (
          <div className="content-section">
            <div className="section-header">
              <h3>Podcast Script: {podcastData.topic}</h3>
              <button
                onClick={() => copyToClipboard(podcastData.script)}
                className="action-btn"
                title="Copy script"
              >
                <FiCopy /> Copy Script
              </button>
            </div>
            <div className="podcast-script">
              {podcastData.script.split('\n').map((line, idx) => {
                const isHost = line.toLowerCase().startsWith('host:');
                const isGuest = line.toLowerCase().startsWith('guest:');
                
                if (isHost || isGuest) {
                  return (
                    <div key={idx} className={`podcast-line ${isHost ? 'host' : 'guest'}`}>
                      <strong>{isHost ? 'Host:' : 'Guest:'}</strong>
                      {line.replace(/^(host|guest):/i, '')}
                    </div>
                  );
                }
                return <p key={idx}>{line}</p>;
              })}
            </div>
            <p className="meta-info">Generated from {podcastData.papers_count} papers</p>
          </div>
        )}

        {activeTab === 'citations' && citationsData && (
          <div className="content-section">
            <div className="section-header">
              <h3>Citations: {citationsData.topic}</h3>
              <button
                onClick={downloadBibTeX}
                className="action-btn"
                title="Download BibTeX"
              >
                <FiDownload /> Download BibTeX
              </button>
            </div>

            <div className="citations-summary">
              <h4>Summary with Citations</h4>
              <div className="citation-text">
                {citationsData.summary_with_citations}
              </div>
            </div>

            <div className="papers-list">
              <h4>Papers ({citationsData.total_papers})</h4>
              {citationsData.papers.map((paper, idx) => (
                <div key={idx} className="paper-card">
                  <div className="paper-number">[{idx + 1}]</div>
                  <div className="paper-details">
                    <h5>{paper.title}</h5>
                    <p className="paper-authors">{paper.authors.join(', ')}</p>
                    <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer" className="paper-link">
                      View PDF
                    </a>
                  </div>
                </div>
              ))}
            </div>

            <div className="bibtex-section">
              <h4>BibTeX Entries</h4>
              <pre className="bibtex-code">
                {citationsData.bibtex_entries.join('\n\n')}
              </pre>
            </div>
          </div>
        )}

        {activeTab === 'ideation' && ideationData && (
          <div className="content-section">
            <div className="section-header">
              <h3>Ideation: {ideationData.topic}</h3>
              <button
                onClick={() => copyToClipboard(JSON.stringify(ideationData.ideas || ideationData.raw || '', null, 2))}
                className="action-btn"
                title="Copy ideas"
              >
                <FiCopy /> Copy Ideas
              </button>
            </div>

            {ideationData.saved && (
              <div className="saved-banner">
                Saved to workspace on {new Date(ideationData.saved.created_at).toLocaleString()}
              </div>
            )}

            {ideationData.ideas && ideationData.ideas.length > 0 ? (
              <div className="idea-grid">
                {ideationData.ideas.map((idea, idx) => (
                  <div key={idx} className="idea-card">
                    <div className="idea-title">{idx + 1}. {idea.title || 'Untitled idea'}</div>
                    <div className="idea-block">
                      <span>Hypothesis</span>
                      <p>{idea.hypothesis || 'Not provided'}</p>
                    </div>
                    <div className="idea-block">
                      <span>Novelty</span>
                      <p>{idea.novelty || 'Not provided'}</p>
                    </div>
                    <div className="idea-block">
                      <span>Feasibility</span>
                      <p>{idea.feasibility || 'Not provided'}</p>
                    </div>
                    <div className="idea-block">
                      <span>Risks</span>
                      <p>{idea.risks || 'Not provided'}</p>
                    </div>
                    <div className="idea-block">
                      <span>Next steps</span>
                      {renderValue(idea.next_steps)}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              ideationData.raw && (
                <pre className="idea-raw">{ideationData.raw}</pre>
              )
            )}

            {isAuthenticated && workspaceId && ideationHistory.length > 0 && (
              <div className="saved-list">
                <div className="saved-header">Saved sessions</div>
                {ideationHistory.map((item) => (
                  <button
                    key={item.id}
                    className="saved-card"
                    onClick={() => handleUseIdeationItem(item)}
                  >
                    <div className="saved-title">{item.topic}</div>
                    <div className="saved-meta">{new Date(item.created_at).toLocaleString()}</div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'experiment' && experimentData && (
          <div className="content-section">
            <div className="section-header">
              <h3>Experiment Design: {experimentData.topic}</h3>
              <button
                onClick={() => copyToClipboard(JSON.stringify(experimentData.plan || experimentData.raw || '', null, 2))}
                className="action-btn"
                title="Copy plan"
              >
                <FiCopy /> Copy Plan
              </button>
            </div>

            {experimentData.saved && (
              <div className="saved-banner">
                Saved to workspace on {new Date(experimentData.saved.created_at).toLocaleString()}
              </div>
            )}

            {experimentData.plan?.raw ? (
              <pre className="idea-raw">{experimentData.plan.raw}</pre>
            ) : (
              <div className="experiment-grid">
                <div className="experiment-card">
                  <h4>Objective</h4>
                  {renderValue(experimentData.plan?.objective)}
                </div>
                <div className="experiment-card">
                  <h4>Hypothesis</h4>
                  {renderValue(experimentData.plan?.hypothesis)}
                </div>
                <div className="experiment-card">
                  <h4>Datasets</h4>
                  {renderValue(experimentData.plan?.datasets)}
                </div>
                <div className="experiment-card">
                  <h4>Metrics</h4>
                  {renderValue(experimentData.plan?.metrics)}
                </div>
                <div className="experiment-card">
                  <h4>Baselines</h4>
                  {renderValue(experimentData.plan?.baselines)}
                </div>
                <div className="experiment-card">
                  <h4>Methodology</h4>
                  {renderValue(experimentData.plan?.methodology)}
                </div>
                <div className="experiment-card">
                  <h4>Ablations</h4>
                  {renderValue(experimentData.plan?.ablations)}
                </div>
                <div className="experiment-card">
                  <h4>Compute</h4>
                  {renderValue(experimentData.plan?.compute)}
                </div>
                <div className="experiment-card">
                  <h4>Risks</h4>
                  {renderValue(experimentData.plan?.risks)}
                </div>
                <div className="experiment-card">
                  <h4>Success criteria</h4>
                  {renderValue(experimentData.plan?.success_criteria)}
                </div>
                <div className="experiment-card">
                  <h4>Timeline</h4>
                  {renderValue(experimentData.plan?.timeline)}
                </div>
              </div>
            )}

            {isAuthenticated && workspaceId && experimentHistory.length > 0 && (
              <div className="saved-list">
                <div className="saved-header">Saved plans</div>
                {experimentHistory.map((item) => (
                  <button
                    key={item.id}
                    className="saved-card"
                    onClick={() => handleUseExperimentItem(item)}
                  >
                    <div className="saved-title">{item.topic}</div>
                    <div className="saved-meta">{new Date(item.created_at).toLocaleString()}</div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {!hasActiveContent && !isLoading && (
          <div className="empty-research">
            <p>Enter a research topic and click "Generate" to create content</p>
          </div>
        )}
        </div>
      </div>
    </div>
  );
};

export default ResearchPanel;
