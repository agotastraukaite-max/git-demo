function InputForm({ values, onChange, onReset, currency, onCurrencyChange, currencies, label, color }) {
  function handleChange(e) {
    const { name, value } = e.target;
    onChange({ ...values, [name]: Number(value) });
  }

  return (
    <div className="card" style={color ? { borderTop: `3px solid ${color}` } : {}}>
      <div className="card-title-row">
        <h2 className="card-title" style={color ? { color } : {}}>
          {label ? `${label} — Details` : 'Project Details'}
        </h2>
        <button className="reset-btn" onClick={onReset} type="button">Reset</button>
      </div>
      <div className="form-group">
        <label htmlFor="currency">Currency</label>
        <select
          id="currency"
          value={currency}
          onChange={e => onCurrencyChange(e.target.value)}
        >
          {Object.keys(currencies).map(code => (
            <option key={code} value={code}>
              {code} ({currencies[code].trim()})
            </option>
          ))}
        </select>
      </div>
      <div className="form-group">
        <label htmlFor={`initialInvestment-${label || 'main'}`}>Initial Investment</label>
        <input
          id={`initialInvestment-${label || 'main'}`}
          type="number"
          name="initialInvestment"
          value={values.initialInvestment}
          min="0"
          onChange={handleChange}
        />
      </div>
      <div className="form-group">
        <label htmlFor={`monthlyRevenue-${label || 'main'}`}>Expected Monthly Revenue</label>
        <input
          id={`monthlyRevenue-${label || 'main'}`}
          type="number"
          name="monthlyRevenue"
          value={values.monthlyRevenue}
          min="0"
          onChange={handleChange}
        />
      </div>
      <div className="form-group">
        <label htmlFor={`monthlyCosts-${label || 'main'}`}>Monthly Operating Costs</label>
        <input
          id={`monthlyCosts-${label || 'main'}`}
          type="number"
          name="monthlyCosts"
          value={values.monthlyCosts}
          min="0"
          onChange={handleChange}
        />
      </div>
      <div className="form-group">
        <label htmlFor={`period-${label || 'main'}`}>Calculation Period (months)</label>
        <select
          id={`period-${label || 'main'}`}
          name="period"
          value={values.period}
          onChange={handleChange}
        >
          <option value={12}>12 months</option>
          <option value={24}>24 months</option>
          <option value={36}>36 months</option>
        </select>
      </div>
    </div>
  );
}

export default InputForm;
