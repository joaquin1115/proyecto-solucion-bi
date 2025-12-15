import React from 'react';
import ReactDOM from 'react-dom';

const TooltipPortal = ({ children, show, x, y }) => {
  if (!show) {
    return null;
  }

  const tooltipStyle = {
    position: 'absolute',
    top: `${y}px`,
    left: `${x}px`,
    transform: 'translate(15px, -100%)', // Mueve el tooltip arriba y a la derecha del cursor
    pointerEvents: 'none',
    zIndex: 1000,
  };

  const tooltipContent = (
    <div style={tooltipStyle}>
      <div 
        className="p-2 rounded-md text-white font-mono text-sm"
        style={{
          backgroundColor: 'rgba(0, 0, 0, 0.9)',
          border: '1px solid #00bcd4',
        }}
      >
        {children}
      </div>
    </div>
  );

  return ReactDOM.createPortal(tooltipContent, document.body);
};

export default TooltipPortal;