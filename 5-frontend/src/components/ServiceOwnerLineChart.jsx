import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  AreaChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

const ServiceOwnerLineChart = ({ data, chartType = 'line' }) => {
  if (!data || data.length === 0) {
    return <div className="flex items-center justify-center h-64 font-mono text-white/70">No hay datos para mostrar.</div>;
  }

  const ChartComponent = chartType === 'area' ? AreaChart : LineChart;
  const DataComponent = chartType === 'area' ? Area : Line;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <ChartComponent data={data} margin={{ top: 20, right: 20, left: -10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
        <XAxis dataKey="month_label" tick={{ fill: '#a0a0a0', fontSize: 12 }} />
        <YAxis
          tick={{ fill: '#a0a0a0', fontSize: 12 }}
          domain={[0, 100]}
          tickFormatter={(tick) => `${tick}%`}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            border: '1px solid #00bcd4',
            color: '#fff',
          }}
          formatter={(value) => [`${parseFloat(value).toFixed(2)}%`, 'Promedio']}
        />
        <Legend wrapperStyle={{ fontSize: '14px' }} />
        <DataComponent
          type="monotone"
          dataKey="avg_adoption"
          name={chartType === 'area' ? 'Promedio Acumulado' : 'Promedio Mensual'}
          stroke="#00bcd4"
          fill={chartType === 'area' ? "url(#colorUv)" : "#00bcd4"}
          fillOpacity={chartType === 'area' ? 0.4 : 1}
          strokeWidth={2}
          dot={{ r: 4 }}
          activeDot={{ r: 6, style: { stroke: '#fff', strokeWidth: 2 } }}
        />
        {chartType === 'area' && (
          <defs>
            <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00bcd4" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#00bcd4" stopOpacity={0}/>
            </linearGradient>
          </defs>
        )}
      </ChartComponent>
    </ResponsiveContainer>
  );
};

export default ServiceOwnerLineChart;