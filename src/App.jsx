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
  const [compareMode, setCompareMode] = useState(false);
  const [activeTab, setActiveTab] = useState('A');
  const [scenarioA, setScenarioA] = useState(DEFAULTS);
  const [scenarioB, setScenarioB] = useState(DEFAULTS);

  const calcA = calculate(scenarioA);
  const calcB = calculate(scenarioB);

  const activeValues = activeTab === 'A' ? scenarioA : scenarioB;
  const activeOnChange = activeTab === 'A' ? setScenarioA : setScenarioB;

  function toggleCompare() {
    setCompareMode(prev => !prev);
    setActiveTab('A');
  }

  return (
    <div className="app-wrapper">
      <header className="app-header">
        <div className="header-top">
          <div>
            <h1 className="app-title">Business ROI Calculator</h1>
            <p className="app-subtitle">Estimate your return on investment and break-even point</p>
          </div>
          <button className={`compare-btn ${compareMode ? 'active' : ''}`} onClick={toggleCompare}>
            {compareMode ? '← Single Mode' : 'Compare Scenarios'}
          </button>
        </div>
      </header>

      <main className="app-layout">
        <div className="col-left">
          {compareMode && (
            <div className="tabs">
              <button
                className={`tab-btn ${activeTab === 'A' ? 'active-a' : ''}`}
                onClick={() => setActiveTab('A')}
              >
                Scenario A
              </button>
              <button
                className={`tab-btn ${activeTab === 'B' ? 'active-b' : ''}`}
                onClick={() => setActiveTab('B')}
              >
                Scenario B
              </button>
            </div>
          )}
          <InputForm
            values={activeValues}
            onChange={activeOnChange}
            label={compareMode ? (activeTab === 'A' ? 'Scenario A' : 'Scenario B') : null}
            color={compareMode ? (activeTab === 'A' ? '#2563eb' : '#16a34a') : null}
          />
        </div>

        <div className="col-right">
          {compareMode ? (
            <div className="results-compare">
              <Results {...calcA} label="Scenario A" color="#2563eb" />
              <Results {...calcB} label="Scenario B" color="#16a34a" />
            </div>
          ) : (
            <Results roi={calcA.roi} paybackPeriod={calcA.paybackPeriod} totalNetProfit={calcA.totalNetProfit} />
          )}
          <CashFlowChart
            dataA={calcA.cashFlowData}
            dataB={compareMode ? calcB.cashFlowData : null}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
