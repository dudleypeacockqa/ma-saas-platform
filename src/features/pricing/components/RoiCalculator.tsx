import { FC, useMemo, useState } from 'react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { calculateRoi } from '@/services/pricing';

interface RoiCalculatorProps {
  planCost: number;
}

export const RoiCalculator: FC<RoiCalculatorProps> = ({ planCost }) => {
  const [averageDealValue, setAverageDealValue] = useState(50000);
  const [monthlyDeals, setMonthlyDeals] = useState(3);
  const [conversionLiftPercentage, setConversionLiftPercentage] = useState(12);

  const results = useMemo(
    () =>
      calculateRoi({
        averageDealValue,
        monthlyDeals,
        conversionLiftPercentage,
        planCost,
      }),
    [averageDealValue, monthlyDeals, conversionLiftPercentage, planCost],
  );

  const currency = new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'GBP',
    maximumFractionDigits: 0,
  });

  const percentageFormatter = new Intl.NumberFormat('en-GB', {
    style: 'percent',
    maximumFractionDigits: 1,
  });

  return (
    <Card className="border border-blue-100 bg-gradient-to-b from-white to-blue-50 dark:border-blue-900 dark:from-slate-900 dark:to-slate-950">
      <CardHeader>
        <CardTitle className="text-xl text-slate-900 dark:text-white">
          ROI impact from improved conversions
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 md:grid-cols-3">
          <div className="space-y-1">
            <Label htmlFor="deal-value">Average deal value (£)</Label>
            <Input
              id="deal-value"
              type="number"
              inputMode="decimal"
              min={0}
              value={averageDealValue}
              onChange={(event) => setAverageDealValue(Number(event.target.value))}
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="monthly-deals">Deals per month</Label>
            <Input
              id="monthly-deals"
              type="number"
              inputMode="numeric"
              min={0}
              value={monthlyDeals}
              onChange={(event) => setMonthlyDeals(Number(event.target.value))}
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="conversion-lift">Estimated conversion lift (%)</Label>
            <Input
              id="conversion-lift"
              type="number"
              inputMode="decimal"
              min={0}
              value={conversionLiftPercentage}
              onChange={(event) => setConversionLiftPercentage(Number(event.target.value))}
            />
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-lg bg-white p-4 text-center shadow-sm dark:bg-slate-900">
            <p className="text-xs uppercase tracking-wide text-slate-500">Incremental revenue</p>
            <p className="mt-2 text-2xl font-semibold text-blue-600 dark:text-blue-300">
              {currency.format(results.incrementalRevenue)}
            </p>
          </div>
          <div className="rounded-lg bg-white p-4 text-center shadow-sm dark:bg-slate-900">
            <p className="text-xs uppercase tracking-wide text-slate-500">ROI multiple</p>
            <p className="mt-2 text-2xl font-semibold text-blue-600 dark:text-blue-300">
              {Number.isFinite(results.roi)
                ? `${percentageFormatter.format(results.roi)}`
                : 'Infinite'}
            </p>
          </div>
          <div className="rounded-lg bg-white p-4 text-center shadow-sm dark:bg-slate-900">
            <p className="text-xs uppercase tracking-wide text-slate-500">Break-even deals</p>
            <p className="mt-2 text-2xl font-semibold text-blue-600 dark:text-blue-300">
              {results.breakEvenDeals}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

