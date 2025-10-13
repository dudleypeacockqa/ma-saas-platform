import { FC, useMemo } from 'react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  OnboardingMilestone,
  OnboardingStage,
  getOnboardingState,
  markMilestoneComplete,
  scheduleEmailSequence,
} from '@/services/onboarding';

interface OnboardingAssistantProps {
  onStateChange?: (state: ReturnType<typeof getOnboardingState>) => void;
}

const renderMilestone = (
  milestone: OnboardingMilestone,
  onComplete: (stage: OnboardingStage) => void,
) => (
  <div
    key={milestone.id}
    className="flex items-start justify-between rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900"
  >
    <div>
      <p className="text-sm font-semibold text-slate-900որեն">{milestone.title}</p>
      <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{milestone.description}</p>
    </div>
    <Button
      variant={milestone.completed ? 'ghost' : 'secondary'}
      className="ml-4"
      disabled={milestone.completed}
      onClick={() => onComplete(milestone.id)}
    >
      {milestone.completed ? 'Completed' : milestone.ctaLabel}
    </Button>
  </div>
);

export const OnboardingAssistant: FC<OnboardingAssistantProps> = ({ onStateChange }) => {
  const state = useMemo(() => getOnboardingState(), []);

  const handleComplete = (stage: OnboardingStage) => {
    const updated = markMilestoneComplete(stage);
    onStateChange?.(updated);
    scheduleEmailSequence(`${stage}_nurture`);
  };

  return (
    <Card className="border border-slate-200 dark:border-slate-800">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-lg">Onboarding journey</CardTitle>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {state.completionRate}% complete · Next milestone keeps your trial on pace.
          </p>
        </div>
        <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700 dark:bg-blue-900/40 dark:text-blue-200">
          Last completed: {state.lastCompleted ?? 'Not started'}
        </span>
      </CardHeader>
      <CardContent className="space-y-3">
        {state.milestones.map((milestone) => renderMilestone(milestone, handleComplete))}
      </CardContent>
    </Card>
  );
};

