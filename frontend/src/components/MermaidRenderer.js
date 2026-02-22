import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import '../styles/MermaidRenderer.css';

// Initialize Mermaid with custom theme
mermaid.initialize({
  startOnLoad: false,
  theme: 'neutral',
  themeVariables: {
    primaryColor: '#f8f3e6',
    primaryTextColor: '#1b1b1b',
    primaryBorderColor: '#1b1b1b',
    lineColor: '#1b1b1b',
    secondaryColor: '#e8dfcf',
    tertiaryColor: '#f18b3a',
    background: '#fffdf7',
    mainBkg: '#fffdf7',
    textColor: '#1b1b1b',
    nodeBorder: '#1b1b1b',
    clusterBkg: '#f8f3e6',
    clusterBorder: '#1b1b1b',
  },
  mindmap: {
    padding: 20,
    useMaxWidth: true,
  },
});

const MermaidRenderer = ({ code, id = 'mermaid-diagram' }) => {
  const mermaidRef = useRef(null);
  const [error, setError] = useState(null);
  const [isRendering, setIsRendering] = useState(false);

  useEffect(() => {
    const renderDiagram = async () => {
      if (!code || !mermaidRef.current) return;

      setIsRendering(true);
      setError(null);

      try {
        // Clear previous content
        mermaidRef.current.innerHTML = '';

        // Generate unique ID for this render
        const uniqueId = `${id}-${Date.now()}`;

        // Render the diagram
        const { svg } = await mermaid.render(uniqueId, code);
        mermaidRef.current.innerHTML = svg;
      } catch (err) {
        console.error('Mermaid rendering error:', err);
        setError('Failed to render mind map. The diagram syntax may be invalid.');
      } finally {
        setIsRendering(false);
      }
    };

    renderDiagram();
  }, [code, id]);

  if (error) {
    return (
      <div className="mermaid-error">
        <p>⚠️ {error}</p>
        <details>
          <summary>View raw code</summary>
          <pre>{code}</pre>
        </details>
      </div>
    );
  }

  return (
    <div className="mermaid-container">
      {isRendering && <div className="mermaid-loading">Rendering diagram...</div>}
      <div ref={mermaidRef} className="mermaid-diagram" />
    </div>
  );
};

export default MermaidRenderer;
