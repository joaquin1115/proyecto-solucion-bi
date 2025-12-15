import React, { useState, useRef, useCallback } from 'react';
import TooltipPortal from './TooltipPortal';

const StackedBarChart = ({ data }) => {
  const [tooltip, setTooltip] = useState({ show: false, content: '', x: 0, y: 0 });
  const containerRef = useRef(null);
  const throttleTimeout = useRef(null);

  // Usamos useCallback para memorizar la función y evitar que se recree en cada render.
  // Se mueve al principio para cumplir con las Reglas de los Hooks.
  const throttledSetTooltip = useCallback((newTooltipState) => {
    // Si ya hay un timeout pendiente, no hacemos nada.
    if (throttleTimeout.current) {
      return;
    }
    setTooltip(newTooltipState);
    // Creamos un nuevo timeout para bloquear actualizaciones por 50ms.
    throttleTimeout.current = setTimeout(() => {
      throttleTimeout.current = null;
    }, 30); // Limita la actualización para un rendimiento fluido
  }, []);

  const formatGeographyName = (name) => {
    if (name === 'COMMERCIAL CLIENT SOLUTIONS') {
      return 'COMM CLIENT SOLUTIONS';
    }
    return name;
  };

  const colors = {
    'LEVEL 3': '#06a8f9',
    'LEVEL 2': '#0587c7',
    'LEVEL 1': '#046a9a',
    'no certificado': '#374151',
  };
  const levels = ['LEVEL 3', 'LEVEL 2', 'LEVEL 1', 'no certificado'];

  if (!data || data.length === 0) {
    return <div className="flex items-center justify-center h-64 font-mono text-white/70">No hay datos para mostrar en el gráfico.</div>;
  }

  const totals = data.map(item =>
    levels.reduce((sum, level) => sum + (Number(item[level]) || 0), 0)
  );

  if (totals.every(t => t === 0)) {
    return <div className="flex items-center justify-center h-64 font-mono text-white/70">No hay datos para mostrar en el gráfico.</div>;
  }

  const barHeight = 30;
  const gap = 20;
  const totalChartHeight = data.length * (barHeight + gap);

  const viewBoxWidth = 1000;
  const labelWidth = 200;
  const barAreaWidth = viewBoxWidth - labelWidth - 50; // 50 for total label

  return (
    <div 
      ref={containerRef}
      className="p-4 overflow-x-auto relative"
      onMouseLeave={() => throttledSetTooltip({ show: false, content: '', x: 0, y: 0 })}
    >
      <TooltipPortal show={tooltip.show} x={tooltip.x} y={tooltip.y}>{tooltip.content}</TooltipPortal>
      <div className="w-full min-w-[600px] -ml-4">
        <svg ref={containerRef} width="100%" height={totalChartHeight} viewBox={`-20 0 ${viewBoxWidth + 40} ${totalChartHeight}`} aria-labelledby="title" role="img">
          <title id="title">Gráfico de barras de niveles de certificación por geografía</title>
          <defs>
            <filter id="bar-chart-glow" x="-10%" y="-10%" width="120%" height="120%">
              <feDropShadow dx="2" dy="2" stdDeviation="3" floodColor="#06a8f9" floodOpacity="0.4" />
            </filter>
          </defs>
          {data.map((item, index) => {
            let accumulatedWidth = 0;
            const total = totals[index];
            if (total === 0) return null;

            return (
              <g key={item.geografia} transform={`translate(0, ${index * (barHeight + gap)})`}>
                <text x={labelWidth - 10} y={barHeight / 2} dy=".35em" className="fill-white/80 font-mono text-sm" textAnchor="end">
                  {formatGeographyName(item.geografia)}
                </text>
                <g transform={`translate(${labelWidth}, 0)`} filter="url(#bar-chart-glow)">
                  {levels.map(level => {
                    const value = Number(item[level]) || 0;
                    if (value === 0) return null;

                    const percentage = (value / total);
                    const barWidth = percentage * barAreaWidth;

                    const isInside = barWidth > 30;
                    const textX = accumulatedWidth + barWidth / 2;

                    const handleMouseMove = (e) => {
                      const x = e.pageX;
                      const y = e.pageY;
                      throttledSetTooltip({ show: true, content: `${level}: ${value}`, x, y });
                    };

                    const segment = (
                      <g
                        key={level}
                        onMouseMove={handleMouseMove}
                        style={{ cursor: 'pointer' }}
                      >
                        <rect
                          x={accumulatedWidth}
                          y="0"
                          width={barWidth}
                          height={barHeight}
                          fill={colors[level]}
                        />
                        {isInside && (
                          <text x={textX} y={barHeight / 2} dy=".35em" className="font-bold text-xs fill-white" textAnchor="middle" style={{ pointerEvents: 'none' }}>
                            {value}
                          </text>
                        )}
                      </g>
                    );
                    accumulatedWidth += barWidth;
                    return segment;
                  })}
                </g>
                <text x={labelWidth + accumulatedWidth + 10} y={barHeight / 2} dy=".35em" className="fill-white font-bold text-sm">
                  {total}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
};

export default StackedBarChart;