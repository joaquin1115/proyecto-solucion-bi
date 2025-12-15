import React, { useState, useRef, useCallback } from 'react';
import TooltipPortal from './TooltipPortal';

const GaugeChart = ({ value = 50 }) => {
  const [hoveredSegment, setHoveredSegment] = useState(null);  
  const containerRef = useRef(null);
  const [tooltip, setTooltip] = useState({ show: false, content: '', x: 0, y: 0 });
  const throttleTimeout = useRef(null);

  const throttledSetTooltip = useCallback((newTooltipState) => {
    if (throttleTimeout.current) {
      return;
    }
    setTooltip(newTooltipState);
    throttleTimeout.current = setTimeout(() => {
      throttleTimeout.current = null;
    }, 15);
  }, []);

  const segments = [
    { level: 'No Certificado', min: 0, max: 70, color: '#374151' },
    { level: 'Level 1', min: 70, max: 80, color: '#046a9a' },
    { level: 'Level 2', min: 80, max: 90, color: '#0587c7' },
    { level: 'Level 3', min: 90, max: 100, color: '#06a8f9' },
  ];

  const radius = 100;
  const strokeWidth = 25;
  const center = { x: 125, y: 125 };

  const getCurrentLevel = (val) => {
    for (let i = segments.length - 1; i >= 0; i--) {
      if (val >= segments[i].min) {
        return segments[i].level;
      }
    }
    return 'No Certificado';
  };

  const valueToAngle = (val) => {
    return (val / 100) * 180 - 90;
  };

  const angle = valueToAngle(value);

  const describeArc = (startAngle, endAngle) => {
    const start = {
      x: center.x + radius * Math.cos((startAngle - 90) * Math.PI / 180),
      y: center.y + radius * Math.sin((startAngle - 90) * Math.PI / 180),
    };
    const end = {
      x: center.x + radius * Math.cos((endAngle - 90) * Math.PI / 180),
      y: center.y + radius * Math.sin((endAngle - 90) * Math.PI / 180),
    };
    const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';
    return `M ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${end.x} ${end.y}`;
  };

  const ticks = Array.from({ length: 11 }, (_, i) => i * 10);

  const needleLength = radius - strokeWidth/2 + 8;
  const needleEndX = center.x + needleLength * Math.cos((angle - 90) * Math.PI / 180);
  const needleEndY = center.y + needleLength * Math.sin((angle - 90) * Math.PI / 180);
  
  // Puntos perpendiculares al ángulo de la aguja para la base del triángulo
  const baseWidth = 8;
  const perpAngle = angle;
  const base1X = center.x + baseWidth * Math.cos((perpAngle) * Math.PI / 180);
  const base1Y = center.y + baseWidth * Math.sin((perpAngle) * Math.PI / 180);
  const base2X = center.x - baseWidth * Math.cos((perpAngle) * Math.PI / 180);
  const base2Y = center.y - baseWidth * Math.sin((perpAngle) * Math.PI / 180);

  return ( // Contenedor principal simplificado
    <div 
      ref={containerRef}
      className="relative"
      onMouseLeave={() => { setHoveredSegment(null); throttledSetTooltip({ show: false }); }}
    >
      <TooltipPortal show={tooltip.show} x={tooltip.x} y={tooltip.y}>{tooltip.content}</TooltipPortal>
      <div className="flex flex-col items-center pb-8">
        <svg ref={containerRef} width="250" height="200" viewBox="-10 0 275 150">
          <defs>
            <filter id="gauge-glow" x="-50%" y="-50%" width="200%" height="200%">
              <feDropShadow dx="0" dy="2" stdDeviation="4" floodColor="#06a8f9" floodOpacity="0.6" />
            </filter>
            <filter id="needle-shadow" x="-50%" y="-50%" width="200%" height="200%">
              <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#000000" floodOpacity="0.8" />
            </filter>
          </defs>
          
          {/* Segments */}
          <g filter="url(#gauge-glow)">
            {segments.map(({ level, min, max, color }) => {
              const startAngle = valueToAngle(min);
              const endAngle = valueToAngle(max);
              const isHovered = hoveredSegment === level;
              const isAnotherHovered = hoveredSegment && !isHovered;

              return (
                <path
                  key={level}
                  d={describeArc(startAngle, endAngle)}
                  fill="none"
                  stroke={color}
                  strokeWidth={strokeWidth}
                  onMouseMove={(e) => {                    
                    setHoveredSegment(level);
                    const x = e.pageX;
                    const y = e.pageY;
                    throttledSetTooltip({ show: true, content: `${level}: ${min}% - ${max}%`, x, y });
                  }}
                  style={{
                    transition: 'all 0.2s ease-in-out',
                    filter: isHovered ? 'brightness(1.3)' : (isAnotherHovered ? 'brightness(0.7)' : 'brightness(1)'),
                    cursor: 'pointer'
                  }}
                />
              );
            })}
          </g>

          {/* Ticks */}
          {ticks.map(tickValue => {
            const tickAngle = valueToAngle(tickValue);
            const startRadius = radius - strokeWidth / 2 - 2;
            const endRadius = radius + strokeWidth / 2 + 2;
            const start = {
              x: center.x + startRadius * Math.cos((tickAngle - 90) * Math.PI / 180),
              y: center.y + startRadius * Math.sin((tickAngle - 90) * Math.PI / 180),
            };
            const end = {
              x: center.x + endRadius * Math.cos((tickAngle - 90) * Math.PI / 180),
              y: center.y + endRadius * Math.sin((tickAngle - 90) * Math.PI / 180),
            };
            const labelRadius = radius + strokeWidth / 2 + 15;
            const labelPos = {
              x: center.x + labelRadius * Math.cos((tickAngle - 90) * Math.PI / 180),
              y: center.y + labelRadius * Math.sin((tickAngle - 90) * Math.PI / 180),
            };

            return (
              <g key={tickValue}>
                <line x1={start.x} y1={start.y} x2={end.x} y2={end.y} stroke="rgba(255,255,255,0.3)" strokeWidth="1" />
                <text
                  x={labelPos.x}
                  y={labelPos.y}
                  textAnchor="middle"
                  dy="0.3em"
                  fill="rgba(255,255,255,0.5)"
                  style={{ fontSize: '12px', fontFamily: 'monospace' }}
                >
                  {tickValue}
                </text>
              </g>
            );
          })}

          {/* Needle */}
          <g filter="url(#needle-shadow)">
            <polygon 
              points={`${base1X},${base1Y} ${base2X},${base2Y} ${needleEndX},${needleEndY}`}
              fill="#fff"
            />
            <circle cx={center.x} cy={center.y} r="10" fill="#fff" />
            <circle cx={center.x} cy={center.y} r="6" fill="#06a8f9" />
          </g>
        </svg>
        <div className="flex flex-col items-center -mt-6">
          <span className="text-3xl font-bold text-white" style={{ fontFamily: 'Orbitron, monospace' }}>
            {value.toFixed(2)}%
          </span>
          <span className="text-sm text-blue-400 uppercase mt-1" style={{ fontFamily: 'monospace' }}>
            Adopción
          </span>
          <span className="text-xs text-white/70 uppercase" style={{ fontFamily: 'monospace' }}>
            {getCurrentLevel(value)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default GaugeChart;