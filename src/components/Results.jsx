function fmt(n) {
  return Math.abs(n).toLocaleString('en-US', { maximumFractionDigits: 0 });
}

function Results({ roi, paybackPeriod, totalNetProfit, label, color }) {
  const roiPositive = roi >= 0;
  const profitPositive = totalNetProfit >= 0;

  return (
    <div className="card" style={color ? { borderTop: `3px solid ${color}` } : {}}>
      <h2 className="card-title" style={color ? { color } : {}}>
        {label || 'Results'}
      </h2>
      <div className="results-grid">
        <div className="result-item" style={color ? { borderLeftColor: color } : {}}>
          <span className="result-label">ROI</span>
          <span className={`result-value ${roiPositive ? 'positive' : 'negative'}`}>
            {roiPositive ? '+' : '-'}{fmt(roi)}%
          </span>
        </div>
        <div className="result-item" style={color ? { borderLeftColor: color } : {}}>
          <span className="result-label">Payback Period</span>
          <span className="result-value" style={{ color: color || '#2563eb' }}>
            {paybackPeriod === null ? 'Never' : `${paybackPeriod} months`}
          </span>
        </div>
        <div className="result-item" style={color ? { borderLeftColor: color } : {}}>
          <span className="result-label">Total Net Profit</span>
          <span className={`result-value ${profitPositive ? 'positive' : 'negative'}`}>
            {profitPositive ? '+' : '-'}${fmt(totalNetProfit)}
          </span>
        </div>
      </div>
    </div>
  );
}

export default Results;
