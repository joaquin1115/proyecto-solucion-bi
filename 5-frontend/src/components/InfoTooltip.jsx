import React, { useState } from 'react';

const InfoTooltip = ({ children, text }) => {
  const [show, setShow] = useState(false);

  if (!text) {
    return <>{children}</>;
  }

  return (
    <div 
      className="relative inline-block" 
      onMouseEnter={() => setShow(true)} 
      onMouseLeave={() => setShow(false)}
    >
      {children}
      {show && (
        <div 
          className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max max-w-xs p-2 rounded-md text-white font-mono text-sm z-10"
          style={{
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            border: '1px solid #00bcd4',
          }}
        >
          {text}
        </div>
      )}
    </div>
  );
};

export default InfoTooltip;