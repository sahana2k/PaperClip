import React, { useState, useEffect } from 'react';
import ChatInterface from './ChatInterface';
import ToolsPanel from './ToolsPanel';
import StatisticsPanel from './StatisticsPanel';
import ResearchPanel from './ResearchPanel';
import WorkspaceManager from './WorkspaceManager';
import Desktop from './Desktop';
import WindowFrame from './WindowFrame';
import DynamicToolInterface from './DynamicToolInterface';
import { apiService } from '../services/api';
import '../styles/App.css';
import '../styles/WindowSystem.css';

const DEFAULT_WINDOWS = {
  chat: { title: 'Chat v0.98', width: 760, height: 520 },
  research: { title: 'Research Lab v0.98', width: 820, height: 560 },
  tools: { title: 'Tools v0.98', width: 720, height: 520 },
  stats: { title: 'System Monitor v0.98', width: 640, height: 480 },
  projects: { title: 'Projects v0.98', width: 520, height: 420 },
  help: { title: 'Help v0.98', width: 640, height: 480 },
  
  // Specific Dynamic Tools
  domain_discovery: { title: 'Domain Discovery', width: 800, height: 550 },
  paper_summarizer: { title: 'Paper Summarizer', width: 800, height: 550 },
  professor_finder: { title: 'Professor Finder', width: 800, height: 550 },
  dataset_hub: { title: 'Dataset Hub', width: 800, height: 550 },
  pretrained_models: { title: 'Model Architect', width: 800, height: 550 },
  generate_code: { title: 'Research Engineer', width: 800, height: 550 },
};

const App = () => {
  const [user, setUser] = useState(null);
  const [authMode, setAuthMode] = useState('login');
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authName, setAuthName] = useState('');
  const [authError, setAuthError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [bootProgress, setBootProgress] = useState(0);
  const [activeWindowId, setActiveWindowId] = useState(null);
  const [clockTime, setClockTime] = useState(() => new Date());
  const [windows, setWindows] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem('paperclip_token');
    if (token) {
      apiService.setAuthToken(token);
      apiService.getMe().then((result) => {
        if (result.success) {
          setUser(result.data);
        } else {
          localStorage.removeItem('paperclip_token');
          apiService.setAuthToken(null);
        }
      });
    }
  }, []);

  useEffect(() => {
    const timer = setInterval(() => setClockTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    console.log('Windows state changed:', windows);
    // Auto-focus the most recently created window
    if (windows.length > 0 && !windows.some((w) => w.id === activeWindowId)) {
      const newestWindow = windows[windows.length - 1];
      setActiveWindowId(newestWindow.id);
    }
  }, [windows, activeWindowId]);

  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    setAuthError('');

    const email = authEmail.trim();
    const password = authPassword.trim();
    const name = authName.trim();

    if (!email || !password || (authMode === 'register' && !name)) {
      setAuthError('Please fill in all required fields');
      return;
    }

    const result = authMode === 'login'
      ? await apiService.login(email, password)
      : await apiService.register(email, password, name);

    if (result.success) {
      const token = result.data.access_token;
      localStorage.setItem('paperclip_token', token);
      apiService.setAuthToken(token);
      setIsLoading(true);
      setAuthPassword('');
      
      // Simulate boot sequence
      let progress = 0;
      const bootInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 100) {
          progress = 100;
          setBootProgress(100);
          clearInterval(bootInterval);
          setTimeout(() => {
            setUser(result.data.user);
            setIsLoading(false);
            setBootProgress(0);
          }, 800);
        } else {
          setBootProgress(progress);
        }
      }, 200);
    } else {
      setAuthError(result.error || 'Authentication failed');
    }
  };

  const bringToFront = (id) => {
    setWindows((prev) => {
      const maxZ = Math.max(0, ...prev.map((win) => win.zIndex || 0));
      return prev.map((win) => (win.id === id ? { ...win, zIndex: maxZ + 1 } : win));
    });
    setActiveWindowId(id);
  };

  const openWindow = (type) => {
    console.log('openWindow called with type:', type);
    setWindows((prev) => {
      const existing = prev.find((win) => win.type === type);
      const maxZ = Math.max(0, ...prev.map((win) => win.zIndex || 0));
      
      if (existing) {
        console.log('Window already exists, restoring:', existing.id);
        return prev.map((win) =>
          win.type === type ? { ...win, minimized: false, zIndex: maxZ + 1 } : win
        );
      }

      const defaults = DEFAULT_WINDOWS[type] || { title: 'Window', width: 680, height: 480 };
      const offset = 30 * prev.length;
      const newId = `${type}-${Date.now()}`;
      console.log('Creating new window:', { id: newId, type, defaults });
      
      return [
        ...prev,
        {
          id: newId,
          type,
          title: defaults.title,
          width: defaults.width,
          height: defaults.height,
          x: 180 + offset,
          y: 80 + offset,
          minimized: false,
          zIndex: maxZ + 1,
        },
      ];
    });
  };

  const closeWindow = (id) => {
    setWindows((prev) => prev.filter((win) => win.id !== id));
    setActiveWindowId((prev) => (prev === id ? null : prev));
  };

  const minimizeWindow = (id) => {
    setWindows((prev) => prev.map((win) => (win.id === id ? { ...win, minimized: true } : win)));
    setActiveWindowId((prev) => (prev === id ? null : prev));
  };

  const maximizeWindow = (id) => {
    setWindows((prev) =>
      prev.map((win) => (win.id === id ? { ...win, maximized: !win.maximized, minimized: false } : win))
    );
    bringToFront(id);
  };

  const restoreWindow = (id) => {
    setWindows((prev) => prev.map((win) => (win.id === id ? { ...win, minimized: false } : win)));
    bringToFront(id);
  };

  const moveWindow = (id, pos) => {
    setWindows((prev) => prev.map((win) => (win.id === id ? { ...win, ...pos } : win)));
  };

  const resizeWindow = (id, size) => {
    setWindows((prev) => prev.map((win) => (win.id === id ? { ...win, ...size } : win)));
  };

  const handleLogout = () => {
    localStorage.removeItem('paperclip_token');
    apiService.setAuthToken(null);
    setUser(null);
    setWindows([]);
  };

  const renderWindowContent = (type) => {
    console.log('renderWindowContent called with type:', type);
    switch (type) {
      case 'chat':
        console.log('Rendering ChatInterface');
        return <ChatInterface isAuthenticated={!!user} />;
      case 'research':
        console.log('Rendering ResearchPanel');
        return <ResearchPanel isAuthenticated={!!user} />;
      case 'tools':
        console.log('Rendering ToolsPanel');
        return <ToolsPanel onToolSelect={(toolId) => openWindow(toolId)} />;
      case 'domain_discovery':
      case 'paper_summarizer':
      case 'professor_finder':
      case 'dataset_hub':
      case 'pretrained_models':
      case 'generate_code':
        return <DynamicToolInterface toolId={type} isAuthenticated={!!user} />;
      case 'stats':
        console.log('Rendering StatisticsPanel');
        return <StatisticsPanel />;
      case 'projects':
        console.log('Rendering WorkspaceManager');
        return <WorkspaceManager isAuthenticated={!!user} />;
      case 'help':
        console.log('Rendering HelpTab');
        return <HelpTab />;
      default:
        console.log('Unknown window type, returning null:', type);
        return null;
    }
  };

  // Show login screen
  if (!user && !isLoading) {
    return (
      <div className="login-shell">
        <div className="auth-monitor">
            <div className="auth-bezel">
              <div className="auth-screen">
                <div className="auth-header">
                  <div className="auth-title">PAPERCLIP</div>
                  <div className="auth-subtitle">A.I. RESEARCH OS v1.0</div>
                </div>

                <form onSubmit={handleAuthSubmit} className="auth-form">
                  <div className="auth-tabs">
                    <button
                      type="button"
                      className={`auth-tab ${authMode === 'login' ? 'active' : ''}`}
                      onClick={() => setAuthMode('login')}
                    >
                      Login
                    </button>
                    <button
                      type="button"
                      className={`auth-tab ${authMode === 'register' ? 'active' : ''}`}
                      onClick={() => setAuthMode('register')}
                    >
                      Register
                    </button>
                  </div>

                  {authMode === 'register' && (
                    <label className="auth-field">
                      <span>NAME</span>
                      <div className="auth-input-wrap">
                        <input
                          type="text"
                          value={authName}
                          onChange={(e) => setAuthName(e.target.value)}
                        />
                        <span className="auth-caret" aria-hidden="true" />
                      </div>
                    </label>
                  )}

                  <label className="auth-field">
                    <span>USERNAME</span>
                    <div className="auth-input-wrap">
                      <input
                        type="email"
                        value={authEmail}
                        onChange={(e) => setAuthEmail(e.target.value)}
                      />
                      <span className="auth-caret" aria-hidden="true" />
                    </div>
                  </label>

                  <label className="auth-field">
                    <span>PASSWORD</span>
                    <div className="auth-input-wrap">
                      <input
                        type="password"
                        value={authPassword}
                        onChange={(e) => setAuthPassword(e.target.value)}
                      />
                    </div>
                  </label>

                  {authError && <div className="auth-error">{authError}</div>}

                  <button type="submit" className="auth-submit">
                    POWER ON
                  </button>
                </form>

                <div className="auth-footer">SYSTEM READY - PRESS POWER ON TO BOOT</div>
              </div>
            </div>
          </div>
      </div>
    );
  }

  // Show loading screen
  if (isLoading) {
    return (
      <div className="boot-shell">
        <div className="boot-screen">
          <div className="boot-logo">PAPERCLIP OS</div>
          <div className="boot-version">A.I. Research Operating System v1.0</div>
          
          <div className="boot-messages">
            <div className="boot-msg">[ OK ] Starting system services...</div>
            <div className="boot-msg">[ OK ] Loading neural modules...</div>
            <div className="boot-msg">[ OK ] Initializing research database...</div>
            <div className="boot-msg">[ OK ] Mounting workspace volumes...</div>
            {bootProgress > 50 && <div className="boot-msg">[ OK ] Starting desktop environment...</div>}
            {bootProgress > 80 && <div className="boot-msg">[ OK ] System ready.</div>}
          </div>

          <div className="boot-progress">
            <div className="boot-progress-bar" style={{ width: `${bootProgress}%` }} />
          </div>
          <div className="boot-percent">{Math.floor(bootProgress)}%</div>
        </div>
      </div>
    );
  }

  return (
    <div className="desktop-shell">
      <Desktop onOpenWindow={openWindow} />

      <div className="window-layer">
        {windows.map((win) => (
          <WindowFrame
            key={win.id}
            id={win.id}
            title={win.title}
            zIndex={win.zIndex}
            x={win.x}
            y={win.y}
            width={win.width}
            height={win.height}
            minimized={win.minimized}
            maximized={win.maximized}
            onClose={closeWindow}
            onMinimize={minimizeWindow}
            onMaximize={maximizeWindow}
            onFocus={bringToFront}
            onMove={moveWindow}
            onResize={resizeWindow}
          >
            {renderWindowContent(win.type)}
          </WindowFrame>
        ))}
      </div>

      <div className="taskbar">
        <div className="taskbar-start">
          <div className="start-user">
            <span className="start-icon">👤</span>
            <span>{user?.name || user?.email || 'User'}</span>
          </div>
          <button className="start-logout" type="button" onClick={handleLogout}>
            Logout
          </button>
        </div>
        <div className="taskbar-windows">
          {windows.map((win) => (
            <button
              key={win.id}
              className={`taskbar-app ${activeWindowId === win.id ? 'active' : ''}`}
              type="button"
              onClick={() => {
                if (win.minimized) {
                  restoreWindow(win.id);
                  return;
                }
                if (activeWindowId === win.id) {
                  minimizeWindow(win.id);
                  return;
                }
                bringToFront(win.id);
              }}
            >
              {win.title}
            </button>
          ))}
        </div>
        <div className="taskbar-right">
          {clockTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
};

const HelpTab = () => (
  <div className="help-tab">
    <h2>How to Use PaperClip</h2>
    <div className="help-content">
      <section>
        <h3>📚 Research Papers</h3>
        <p>Ask about papers, summaries, and academic research. Example: "Find papers on machine learning"</p>
      </section>
      <section>
        <h3>💻 Code & Development</h3>
        <p>Get code snippets, examples, and programming solutions. Example: "Show me a React hook example"</p>
      </section>
      <section>
        <h3>📊 Data & Datasets</h3>
        <p>Discover datasets and data resources. Example: "Find datasets for NLP"</p>
      </section>
      <section>
        <h3>🤖 Models</h3>
        <p>Explore pre-trained models and AI resources. Example: "Show me popular BERT models"</p>
      </section>
      <section>
        <h3>🔧 Available Tools</h3>
        <p>Visit the Tools tab to see all available research tools and their capabilities.</p>
      </section>
    </div>
  </div>
);

export default App;
