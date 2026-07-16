function fmt(n) {
  return Math.abs(n).toLocaleString('en-US', { maximumFractionDigits: 0 });
}

function Results({ roi, paybackPeriod, totalNetProfit }) {
  const roiPositive = roi >= 0;
  const profitPositive = totalNetProfit >= 0;

  return (
    <div className="card">
      <h2 className="card-title">Results</h2>
      <div className="results-grid">
        <div className="result-item">
          <span className="result-label">ROI</span>
          <span className={`result-value ${roiPositive ? 'positive' : 'negative'}`}>
            {roiPositive ? '+' : '-'}{fmt(roi)}%
          </span>
        </div>
        <div className="result-item">
          <span className="result-label">Payback Period</span>
          <span className="result-value neutral">
            {paybackPeriod === null ? 'Never' : `${paybackPeriod} months`}
          </span>
        </div>
        <div className="result-item">
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
