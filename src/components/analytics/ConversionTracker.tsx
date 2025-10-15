import { FC, useEffect, useState } from 'react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { trackEvent } from '@/services/analytics';

interface MetricCard {
  label: string;
  value: string;
  delta: string;
}

const defaultMetrics: MetricCard[] = [
  { label: 'Trial-to-paid', value: '32.6%', delta: '+3.4%' },
  { label: 'Activated in 7 days', value: '78%', delta: '+5.0%' },
  { label: 'Expansion revenue', value: '£47.5k', delta: '+11%' },
];

export const ConversionTracker: FC = () => {
  const [metrics, setMetrics] = useState<MetricCard[]>(defaultMetrics);

  useEffect(() => {
    const stored = localStorage.getItem('conversion_metrics');
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as MetricCard[];
        setMetrics(parsed);
      } catch (error) {
        console.warn('Failed to parse conversion metrics', error);
      }
    }
  }, []);

  const handleRefresh = () => {
    trackEvent('conversion_metrics_refreshed');
    localStorage.removeItem('conversion_metrics');
    setMetrics(defaultMetrics);
  };

  return (
    <Card className="border border-slate-200 dark:border-slate-800">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg">Revenue conversion metrics</CardTitle>
        <button
          type="button"
          className="rounded-md border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-700 transition hover:border-blue-500 hover:text-blue-600 dark:border-slate-700 dark:text-slate-200"
          onClick={handleRefresh}
        >
          Refresh
        </button>
      </CardHeader>
      <CardContent className="grid gap-4 md:grid-cols-3">
        {metrics.map((metric) => (
          <div
            key={metric.label}
            className="rounded-xl border border-blue-100 bg-blue-50 p-4 text-center dark:border-blue-900/40 dark:bg-blue-950/40"
          >
            <p className="text-xs uppercase tracking-wide text-blue-700 dark:text-blue-300">
              {metric.label}
            </p>
            <p className="mt-3 text-2xl font-semibold text-slate-900 dark:text-white">
              {metric.value}
            </p>
            <p className="text-xs font-semibold text-emerald-600 dark:text-emerald-300">
              {metric.delta}
            </p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};

