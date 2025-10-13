import { FC } from 'react';

import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';

interface PricingExperimentControlsProps {
  variant: 'A' | 'B';
  onChange: (variant: 'A' | 'B') => void;
}

export const PricingExperimentControls: FC<PricingExperimentControlsProps> = ({
  variant,
  onChange,
}) => {
  const isVariantB = variant === 'B';

  return (
    <div className="flex flex-col gap-2 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-900 dark:text-white">A/B experiment</p>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Toggle variant B to expose a 5% launch incentive for high-intent visitors.
          </p>
        </div>
        <Switch
          checked={isVariantB}
          onCheckedChange={(checked) => onChange(checked ? 'B' : 'A')}
        />
      </div>
      <div className="grid gap-1 text-xs text-slate-600 dark:text-slate-300">
        <p>
          <span className="font-semibold">Variant A:</span> Baseline pricing with standard messaging.
        </p>
        <p>
          <span className="font-semibold">Variant B:</span> Adds urgency messaging and limited-time incentive.
        </p>
        <Label className="text-[11px] text-blue-500">
          All toggles sync to GA4 conversion events and attribution dashboards.
        </Label>
      </div>
    </div>
  );
};

