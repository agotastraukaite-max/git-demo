import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Legend,
  ResponsiveContainer,
} from 'recharts';

function formatDollar(value) {
  const abs = Math.abs(value);
  const sign = value < 0 ? '-' : '';
  if (abs >= 1000000) return `${sign}$${(abs / 1000000).toFixed(1)}M`;
  if (abs >= 1000) return `${sign}$${(abs / 1000).toFixed(0)}K`;
  return `${sign}$${abs}`;
}

function CustomTooltip({ active, payload, label, compareMode }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <p className="tooltip-month">Month {label}</p>
      {payload.map((entry) => (
        <p key={entry.dataKey} className="tooltip-value" style={{ color: entry.color }}>
          {compareMode ? `${entry.name}: ` : ''}
          {entry.value >= 0 ? '+' : '-'}${Math.abs(entry.value).toLocaleString('en-US', { maximumFractionDigits: 0 })}
        </p>
      ))}
    </div>
  );
}

function CashFlowChart({ dataA, dataB }) {
  const compareMode = Boolean(dataB);

  const chartData = compareMode
    ? Array.from({ length: Math.max(dataA.length, dataB.length) }, (_, i) => ({
        month: i + 1,
        A: dataA[i]?.cashFlow ?? null,
        B: dataB[i]?.cashFlow ?? null,
      }))
    : dataA.map(d => ({ month: d.month, A: d.cashFlow }));

  return (
    <div className="card">
      <h2 className="card-title">Cumulative Cash Flow</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="month"
            label={{ value: 'Month', position: 'insideBottom', offset: -2, fontSize: 12 }}
            tick={{ fontSize: 12 }}
          />
          <YAxis tickFormatter={formatDollar} tick={{ fontSize: 11 }} width={60} />
          <Tooltip content={<CustomTooltip compareMode={compareMode} />} />
          {compareMode && (
            <Legend
              verticalAlign="top"
              height={32}
              formatter={(value) => value === 'A' ? 'Scenario A' : 'Scenario B'}
            />
          )}
          <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="5 5" strokeWidth={2} />
          <Line
            type="monotone"
            dataKey="A"
            name="A"
            stroke="#2563eb"
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 5, fill: '#2563eb' }}
          />
          {compareMode && (
            <Line
              type="monotone"
              dataKey="B"
              name="B"
              stroke="#16a34a"
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 5, fill: '#16a34a' }}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default CashFlowChart;
