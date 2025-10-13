import { useEffect, useState } from 'react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  fetchUsageSnapshot,
  predictChurn,
  recordRetentionAction,
  subscribeToUsageAlerts,
  updateSubscription,
} from '@/services/subscription';

type PlanTier = 'solo' | 'growth' | 'enterprise';

interface UsageSnapshotDisplay {
  label: string;
  value: string;
}

export const SubscriptionManager = () => {
  const [loading, setLoading] = useState(false);
  const [usage, setUsage] = useState<UsageSnapshotDisplay[]>([]);
  const [churnScore, setChurnScore] = useState('Refreshing...');

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const snapshot = await fetchUsageSnapshot();
        if (mounted) {
          setUsage([
            { label: 'Active deals', value: snapshot.activeDeals.toString() },
            { label: 'Team seats', value: snapshot.teamSeats.toString() },
            { label: 'Storage', value: snapshot.storageGb + ' GB' },
          ]);
        }
      } catch (error) {
        console.warn('Failed to fetch usage snapshot', error);
      }
    };

    const loadChurn = async () => {
      try {
        const signal = await predictChurn();
        if (mounted) {
          const readable = signal.riskLevel.toUpperCase() + ' - ' + Math.round(signal.score * 100) + '% risk';
          setChurnScore(readable);
        }
      } catch (error) {
        console.warn('Failed to load churn score', error);
      }
    };

    load();
    loadChurn();

    return () => {
      mounted = false;
    };
  }, []);

  const handlePlanChange = async (action: 'upgrade' | 'downgrade', plan: PlanTier) => {
    setLoading(true);
    try {
      await updateSubscription(action, { plan });
    } finally {
      setLoading(false);
    }
  };

  const handleUsageAlert = async () => {
    await subscribeToUsageAlerts(85);
  };

  return (
    <Card className="border border-slate-200 dark:border-slate-800">
      <CardHeader>
        <CardTitle className="text-lg">Subscription operations</CardTitle>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Real-time upgrade controls, usage guardrails, and churn prevention playbooks.
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-3 text-sm text-slate-600 dark:text-slate-300 md:grid-cols-3">
          {usage.map((item) => (
            <div key={item.label} className="rounded-md border border-slate-200 bg-white p-3 dark:border-slate-800 dark:bg-slate-900">
              <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
                {item.label}
              </p>
              <p className="mt-2 text-lg font-semibold text-slate-900 dark:text-white">{item.value}</p>
            </div>
          ))}
        </div>

        <div className="flex flex-wrap gap-3">
          <Button disabled={loading} onClick={() => handlePlanChange('upgrade', 'growth')}>
            Upgrade to Growth
          </Button>
          <Button variant="secondary" disabled={loading} onClick={() => handlePlanChange('upgrade', 'enterprise')}>
            Upgrade to Enterprise
          </Button>
          <Button variant="ghost" disabled={loading} onClick={() => handlePlanChange('downgrade', 'solo')}>
            Downgrade to Solo
          </Button>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          <Button variant="outline" onClick={handleUsageAlert}>
            Configure usage alerts
          </Button>
          <Button
            variant="outline"
            onClick={() => recordRetentionAction('case_study_sent', { plan: 'growth' })}
          >
            Trigger retention playbook
          </Button>
        </div>

        <div className="rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700 dark:border-amber-900/60 dark:bg-amber-950/30 dark:text-amber-200">
          <p className="font-semibold">Churn risk indicator</p>
          <p className="mt-1">{churnScore}</p>
        </div>
      </CardContent>
    </Card>
  );
};

