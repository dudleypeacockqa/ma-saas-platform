import { FC } from 'react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { trackEvent } from '@/services/analytics';

export interface ConversionStage {
  id: string;
  label: string;
  count: number;
  conversionRate: number;
}

interface ConversionFunnelCardProps {
  stages: ConversionStage[];
}

export const ConversionFunnelCard: FC<ConversionFunnelCardProps> = ({ stages }) => (
  <Card className="border border-slate-200 dark:border-slate-800">
    <CardHeader className="flex flex-row items-center justify-between">
      <CardTitle className="text-xl">Conversion funnel performance</CardTitle>
      <button
        type="button"
        className="rounded-md border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-700 transition hover:border-blue-500 hover:text-blue-600 dark:border-slate-700 dark:text-slate-200"
        onClick={() => trackEvent('funnel_export_clicked')}
      >
        Export CSV
      </button>
    </CardHeader>
    <CardContent className="space-y-4">
      {stages.map((stage) => (
        <div key={stage.id} className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-slate-700 dark:text-slate-200">{stage.label}</span>
            <span className="text-slate-500 dark:text-slate-400">
              {stage.count.toLocaleString()} · {Math.round(stage.conversionRate * 100)}%
            </span>
          </div>
          <Progress value={stage.conversionRate * 100} />
        </div>
      ))}
    </CardContent>
  </Card>
);

