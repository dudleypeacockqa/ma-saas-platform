import { FC } from 'react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { DynamicPricingResult } from '@/services/pricing';

interface DynamicPricingTableProps {
  results: DynamicPricingResult[];
  activePlan?: string;
  onSelectPlan?: (plan: DynamicPricingResult) => void;
}

const planHighlights: Record<string, string[]> = {
  solo: [
    'Deal pipeline + document management',
    'AI insights limited to 50 requests/month',
    'Email support',
  ],
  growth: [
    'Advanced analytics and forecasting',
    'Unlimited AI deal analysis',
    'Priority success manager',
    'Workflow automation suite',
  ],
  enterprise: [
    'Global permissions and SSO support',
    'Dedicated pod + 24/5 concierge',
    'White-label investor portals',
    'Portfolio-level reporting',
  ],
};

const planBadges: Record<string, string | undefined> = {
  solo: 'Launch',
  growth: 'Most Popular',
  enterprise: 'Scale',
};

export const DynamicPricingTable: FC<DynamicPricingTableProps> = ({
  results,
  activePlan,
  onSelectPlan,
}) => (
  <div className="grid gap-6 lg:grid-cols-3">
    {results.map((plan) => {
      const badge = planBadges[plan.plan];
      const isActive = activePlan ? activePlan === plan.plan : plan.plan === 'growth';
      return (
        <Card
          key={plan.plan}
          className={cn(
            'relative border border-slate-200 transition-all hover:shadow-lg dark:border-slate-800',
            isActive &&
              'border-blue-500 shadow-xl ring-1 ring-blue-500 dark:border-blue-400 dark:ring-blue-400',
            'flex flex-col justify-between'
          )}
        >
          {badge ? (
            <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white">
              {badge}
            </Badge>
          ) : null}
          <CardHeader>
            <CardTitle className="text-2xl text-slate-900 dark:text-white">
              {plan.plan === 'solo' && 'Solo Dealmaker'}
              {plan.plan === 'growth' && 'Growth Firm'}
              {plan.plan === 'enterprise' && 'Enterprise'}
            </CardTitle>
            <div className="mt-4 text-slate-600 dark:text-slate-300">
              <span className="text-4xl font-bold text-slate-900 dark:text-white">
                {plan.displayPrice}
              </span>
              <span className="ml-1 text-sm uppercase text-slate-500 dark:text-slate-400">
                {plan.billingInterval === 'monthly' ? '/month' : '/year'}
              </span>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-semibold text-blue-500 dark:text-blue-300">Adjustments</p>
              <ul className="mt-2 space-y-1">
                {plan.adjustments.length ? (
                  plan.adjustments.map((adjustment, index) => (
                    <li key={`${plan.plan}-adjustment-${index}`} className="text-sm text-slate-600 dark:text-slate-300">
                      {adjustment.reason} ({Math.round(adjustment.value * 100)}%)
                    </li>
                  ))
                ) : (
                  <li className="text-sm text-slate-500">Baseline pricing applied</li>
                )}
              </ul>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900 dark:text-white">Highlights</p>
              <ul className="mt-2 space-y-1">
                {planHighlights[plan.plan].map((item) => (
                  <li key={item} className="text-sm text-slate-600 dark:text-slate-300">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <button
              type="button"
              className={cn(
                'w-full rounded-md px-4 py-2 text-sm font-semibold transition-colors',
                isActive
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'border border-slate-300 text-slate-700 hover:border-blue-500 dark:border-slate-700 dark:text-slate-200'
              )}
              onClick={() => onSelectPlan?.(plan)}
            >
              Choose plan
            </button>
          </CardContent>
        </Card>
      );
    })}
  </div>
);

