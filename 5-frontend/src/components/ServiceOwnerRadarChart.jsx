import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend, Tooltip } from 'recharts';

    const ServiceOwnerRadarChart = ({ data, compareData, metricLabels }) => {
  // Comprobación robusta: Si no hay datos principales, no renderizar.
  if (!data || Object.keys(data).length === 0) {
    return <div className="text-center text-white/70">No hay datos disponibles para el gráfico de radar.</div>;
  }

  // Transformación de datos: Mapea las métricas y combina los datos actuales y de comparación.
  const chartData = Object.keys(metricLabels).map(key => {
    const valueCurrent = parseFloat(data[key]);
    const valueCompare = compareData ? parseFloat(compareData[key]) : null;
    
    const point = {
      subject: metricLabels[key],
      A: !isNaN(valueCurrent) ? valueCurrent : 0, // Datos del mes actual
      fullMark: 100,
    };

    if (compareData && !isNaN(valueCompare)) {
      point.B = valueCompare; // Datos del mes de comparación
    }

    return point;
  });

  const currentMonthLabel = data.month_label || 'Actual';
  const compareMonthLabel = compareData?.month_label || 'Comparación';

  return (
    <ResponsiveContainer width="100%" height={400}>
      <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
        <PolarGrid stroke="rgba(255, 255, 255, 0.2)" radialLines={false} />
        <PolarAngleAxis dataKey="subject" tick={{ fill: 'white', fontSize: 12 }} />
        <PolarRadiusAxis axisLine={false} tick={false} />
        
        {/* Radar para el mes actual */}
        <Radar 
          name={currentMonthLabel} 
          dataKey="A" 
          stroke="#00bcd4" 
          fill="#00bcd4" 
          fillOpacity={0.6} 
          isAnimationActive={false} 
        />
        
        {/* Radar para el mes de comparación (si existe) */}
        {compareData && (
          <Radar name={compareMonthLabel} dataKey="B" stroke="#8884d8" fill="#8884d8" fillOpacity={0.4} isAnimationActive={false} />
        )}

        <Tooltip
          contentStyle={{ backgroundColor: 'rgba(0, 0, 0, 0.8)', border: '1px solid #00bcd4', color: '#fff' }}
          formatter={(value, name) => [`${value.toFixed(2)}%`, name]}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
};

export default ServiceOwnerRadarChart;