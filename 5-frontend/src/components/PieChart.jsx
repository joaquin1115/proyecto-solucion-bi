import React, { useState, useRef, useCallback } from 'react';
import TooltipPortal from './TooltipPortal';

const PieChart = ({ data }) => {
  const [hoveredSlice, setHoveredSlice] = useState(null);  
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
    }, 30);
  }, []);

  const colors = {
    'LEVEL 3': '#06a8f9', // Azul primario
    'LEVEL 2': '#0587c7', // Un poco más oscuro
    'LEVEL 1': '#046a9a', // Aún más oscuro
    'no certificado': '#374151', // Gris oscuro
  };

  const levels = ['LEVEL 3', 'LEVEL 2', 'LEVEL 1', 'no certificado'];

  const total = levels.reduce((sum, level) => sum + (data[level] || 0), 0);

  if (total === 0) {
    return <div className="flex items-center justify-center h-64 font-mono text-white/70">No hay datos para mostrar en el gráfico.</div>;
  }

  let cumulativePercent = 0;

  const getCoordinatesForPercent = (percent) => {
    const x = Math.cos(2 * Math.PI * percent);
    const y = Math.sin(2 * Math.PI * percent);
    return [x, y];
  };

  const slices = levels.map(level => {
    const value = data[level] || 0;
    if (value === 0) return null; // ¡Corrección clave! Ignorar segmentos con valor 0

    const percent = value / total;
    const [startX, startY] = getCoordinatesForPercent(cumulativePercent);
    cumulativePercent += percent;
    const [endX, endY] = getCoordinatesForPercent(cumulativePercent);
    const largeArcFlag = percent > 0.5 ? 1 : 0;

    const pathData = [
      `M ${startX} ${startY}`, // Move
      `A 1 1 0 ${largeArcFlag} 1 ${endX} ${endY}`, // Arc
      'L 0 0', // Line to center
    ].join(' ');

    return {
      pathData,
      color: colors[level],
      label: level,
      value,
      percentage: (percent * 100).toFixed(2) // Ajustado a 2 decimales como en el ejemplo
    };
  }).filter(Boolean); // Eliminar los elementos nulos del array

  return (
    <div 
      ref={containerRef}
      className="flex flex-col md:flex-row items-center justify-center gap-8 p-4 relative"
      onMouseLeave={() => { setHoveredSlice(null); throttledSetTooltip({ show: false }); }}
    >
      <TooltipPortal show={tooltip.show} x={tooltip.x} y={tooltip.y}>{tooltip.content}</TooltipPortal>
      <div className="relative w-96 h-96">
        <svg ref={containerRef} viewBox="-1.2 -1.2 2.4 2.4" style={{ transform: 'rotate(-90deg)' }}>
          <defs>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feDropShadow dx="0" dy="0" stdDeviation="0.05" floodColor="#06a8f9" floodOpacity="0.7" />
            </filter>
          </defs>
          <g filter="url(#glow)">
            {slices.map((slice, index) => (
              <path
                key={index}
                d={slice.pathData}
                fill={slice.color}
                onMouseMove={(e) => {                  
                  setHoveredSlice(slice.label);
                  const x = e.pageX;
                  const y = e.pageY;
                  throttledSetTooltip({ show: true, content: `${slice.label}: ${slice.value} (${slice.percentage}%)`, x, y });
                }}
                style={{
                  cursor: 'pointer',
                  transform: hoveredSlice === slice.label ? 'scale(1.05)' : 'scale(1)',
                  transformOrigin: 'center',
                  transition: 'transform 0.2s ease-in-out, filter 0.2s ease-in-out',
                  filter: hoveredSlice && hoveredSlice !== slice.label ? 'brightness(0.7)' : 'brightness(1)',
                }}
              />
            ))}
          </g>
        </svg>
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="flex flex-col items-center text-center">
                <span className="font-orbitron text-4xl font-bold text-white">
                    {hoveredSlice ? data[hoveredSlice] : total}
                </span>
                <span className="font-mono text-sm text-primary uppercase">
                    {hoveredSlice ? hoveredSlice : 'Total'}
                </span>
            </div>
        </div>
      </div>
      <div className="font-mono text-sm text-white/80">
        <h3 className="font-orbitron text-xl font-bold text-white mb-4">Leyenda</h3>
        <div className="grid grid-cols-2 gap-x-8 gap-y-4">
          {levels.map(level => {
            const slice = slices.find(s => s.label === level) || { label: level, value: 0, percentage: '0.00' };
            return (
            <div key={level} className="flex items-start gap-3">
              <div className="w-3 h-3 rounded-sm mt-1" style={{ backgroundColor: colors[level] }} />
              <div>
                <p className="capitalize text-white font-bold">{slice.label}</p>
                <p className="text-primary">{slice.percentage}% ({slice.value})</p>
              </div>
            </div>
            )
          })}
        </div>
      </div>
    </div>
  );
};

export default PieChart;