import React, { useState } from 'react';

const PieChart = ({ data }) => {
  const [hoveredSlice, setHoveredSlice] = useState(null);

  const colors = {
    'LEVEL 3': '#06a8f9',
    'LEVEL 2': '#0587c7',
    'LEVEL 1': '#046a9a',
    'no certificado': '#374151',
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
      percentage: (percent * 100).toFixed(1)
    };
  });

  return (
    <div className="flex flex-col md:flex-row items-center justify-center gap-8 p-4">
      <div className="relative w-64 h-64">
        <svg viewBox="-1.2 -1.2 2.4 2.4" style={{ transform: 'rotate(-90deg)' }}>
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
                onMouseEnter={() => setHoveredSlice(slice.label)}
                onMouseLeave={() => setHoveredSlice(null)}
                style={{
                  cursor: 'pointer',
                  transform: hoveredSlice === slice.label ? 'scale(1.05)' : 'scale(1)',
                  transformOrigin: 'center',
                  transition: 'transform 0.2s ease-in-out, filter 0.2s ease-in-out',
                  filter: hoveredSlice && hoveredSlice !== slice.label ? 'brightness(0.7)' : 'brightness(1)',
                }}
              >
                <title>{`${slice.label}: ${slice.value} (${slice.percentage}%)`}</title>
              </path>
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
      <div className="flex flex-col gap-4 font-mono text-sm">
        {slices.map(slice => (
          <div key={slice.label} className="flex items-center gap-3">
            <div
              className="w-4 h-4 rounded-sm"
              style={{ backgroundColor: slice.color }}
            />
            <div className="flex justify-between w-48 text-white/80">
              <span className="capitalize">{slice.label}</span>
              <span className="font-bold text-white">{slice.value}</span>
            </div>
            <div className="w-16 text-right text-primary font-bold">
              {slice.percentage}%
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PieChart;