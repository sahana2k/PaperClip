import React from 'react';
import { 
  HiBeaker, 
  HiFolder, 
  HiCommandLine, 
  HiChatBubbleLeftRight, 
  HiChartBar, 
  HiQuestionMarkCircle 
} from 'react-icons/hi2';
import '../styles/Desktop.css';

const Desktop = ({ onOpenWindow }) => {
  console.log('Desktop component rendered, onOpenWindow prop:', typeof onOpenWindow === 'function' ? 'FUNCTION' : 'NOT A FUNCTION');
  
  const icons = [
    { id: 'research', label: 'Research Lab', icon: <HiBeaker />, className: 'icon-research' },
    { id: 'projects', label: 'Projects', icon: <HiFolder />, className: 'icon-projects' },
    { id: 'tools', label: 'Tools', icon: <HiCommandLine />, className: 'icon-tools' },
    { id: 'chat', label: 'Chat', icon: <HiChatBubbleLeftRight />, className: 'icon-chat' },
    { id: 'stats', label: 'System Monitor', icon: <HiChartBar />, className: 'icon-stats' },
    { id: 'help', label: 'Help', icon: <HiQuestionMarkCircle />, className: 'icon-help' },
  ];

  return (
    <div className="desktop">
      <div className="desktop-icons">
        {icons.map((icon) => (
          <button
            key={icon.id}
            className="desktop-icon"
            type="button"
            onClick={(e) => {
              console.log('Icon clicked:', icon.id);
              if (typeof onOpenWindow === 'function') {
                onOpenWindow(icon.id);
              }
            }}
          >
            <div className={`icon-box ${icon.className}`}>
              <div className="icon-inner">
                {icon.icon}
              </div>
            </div>
            <span className="icon-label">{icon.label}</span>
          </button>
        ))}
      </div>

      <div className="desktop-watermark">
        <div className="watermark-title">PAPERCLIP</div>
        <div className="watermark-subtitle">A.I. RESEARCH OS v1.0</div>
      </div>

      <div className="system-panel">
        <div className="panel-title">SYSTEM INFO</div>
        <p>PaperClip OS utilizes advanced retro-neural circuits to compute future-tech in a 1995 environment.</p>
        <div className="panel-status">
          <span>Status:</span>
          <span className="status-pill">OPTIMAL</span>
        </div>
      </div>
    </div>
  );
};

export default Desktop;
