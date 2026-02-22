import React, { useEffect, useRef, useState } from 'react';
import '../styles/WindowSystem.css';

const WindowFrame = ({
  id,
  title,
  zIndex,
  x,
  y,
  width,
  height,
  minimized,
  maximized,
  onClose,
  onMinimize,
  onMaximize,
  onFocus,
  onMove,
  onResize,
  children,
}) => {
  const frameRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [resizing, setResizing] = useState(false);
  const dragOffset = useRef({ x: 0, y: 0 });
  const resizeStart = useRef({ x: 0, y: 0, w: 0, h: 0 });

  useEffect(() => {
    const handleMove = (event) => {
      if (dragging && !maximized) {
        onMove(id, {
          x: event.clientX - dragOffset.current.x,
          y: event.clientY - dragOffset.current.y,
        });
      }
      if (resizing && !maximized) {
        const dx = event.clientX - resizeStart.current.x;
        const dy = event.clientY - resizeStart.current.y;
        onResize(id, {
          width: Math.max(420, resizeStart.current.w + dx),
          height: Math.max(280, resizeStart.current.h + dy),
        });
      }
    };

    const handleUp = () => {
      setDragging(false);
      setResizing(false);
    };

    if (dragging || resizing) {
      window.addEventListener('mousemove', handleMove);
      window.addEventListener('mouseup', handleUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleUp);
    };
  }, [dragging, resizing, id, onMove, onResize, maximized]);

  const startDrag = (event) => {
    if (minimized || maximized) return;
    onFocus(id);
    const rect = frameRef.current.getBoundingClientRect();
    dragOffset.current = { x: event.clientX - rect.left, y: event.clientY - rect.top };
    setDragging(true);
  };

  const startResize = (event) => {
    if (maximized) return;
    event.stopPropagation();
    onFocus(id);
    resizeStart.current = {
      x: event.clientX,
      y: event.clientY,
      w: width,
      h: height,
    };
    setResizing(true);
  };

  if (minimized) return null;

  return (
    <div
      ref={frameRef}
      className={`window-frame ${maximized ? 'maximized' : ''}`}
      style={{
        transform: maximized ? 'none' : `translate(${x}px, ${y}px)`,
        width: maximized ? '100%' : width,
        height: maximized ? 'calc(100vh - 2.4rem)' : height,
        zIndex,
        top: 0,
        left: 0,
      }}
      onMouseDown={() => onFocus(id)}
    >
      <div className="window-titlebar" onMouseDown={startDrag} onDoubleClick={() => onMaximize(id)}>
        <span>{title}</span>
        <div className="window-controls">
          <button className="win-btn" type="button" onClick={() => onMinimize(id)}>
            _
          </button>
          <button className="win-btn" type="button" onClick={() => onMaximize(id)}>
            {maximized ? '❐' : '□'}
          </button>
          <button className="win-btn" type="button" onClick={() => onClose(id)}>
            X
          </button>
        </div>
      </div>
      <div className="window-body">
        {children}
      </div>
      {!maximized && <div className="window-resizer" onMouseDown={startResize} />}
    </div>
  );
};

export default WindowFrame;
