export function calculate({ initialInvestment, monthlyRevenue, monthlyCosts, period }) {
  const monthlyNetProfit = monthlyRevenue - monthlyCosts;
  const totalNetProfit = monthlyNetProfit * period - initialInvestment;
  const roi = initialInvestment > 0 ? (totalNetProfit / initialInvestment) * 100 : 0;

  let paybackPeriod;
  if (monthlyNetProfit <= 0) {
    paybackPeriod = null;
  } else {
    paybackPeriod = Math.ceil(initialInvestment / monthlyNetProfit);
  }

  const cashFlowData = Array.from({ length: period }, (_, i) => {
    const month = i + 1;
    return {
      month,
      cashFlow: monthlyNetProfit * month - initialInvestment,
    };
  });

  return { roi, paybackPeriod, totalNetProfit, monthlyNetProfit, cashFlowData };
}
