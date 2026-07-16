import { useState } from 'react';
import InputForm from './components/InputForm';
import Results from './components/Results';
import CashFlowChart from './components/CashFlowChart';
import { calculate } from './utils/calculations';

const DEFAULTS = {
  initialInvestment: 100000,
  monthlyRevenue: 15000,
  monthlyCosts: 5000,
  period: 12,
};

function App() {
  const [values, setValues] = useState(DEFAULTS);
  const { roi, paybackPeriod, totalNetProfit, cashFlowData } = calculate(values);

  return (
    <div className="app-wrapper">
      <header className="app-header">
        <h1 className="app-title">Business ROI Calculator</h1>
        <p className="app-subtitle">Estimate your return on investment and break-even point</p>
      </header>
      <main className="app-layout">
        <div className="col-left">
          <InputForm values={values} onChange={setValues} />
        </div>
        <div className="col-right">
          <Results roi={roi} paybackPeriod={paybackPeriod} totalNetProfit={totalNetProfit} />
          <CashFlowChart data={cashFlowData} />
        </div>
      </main>
    </div>
  );
}

export default App;
