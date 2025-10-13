import { useEffect, useMemo, useState } from 'react';
import { useUser } from '@clerk/clerk-react';
import { motion } from 'framer-motion';
import { CheckCircle2, ArrowRight } from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { trackEvent } from '@/lib/analytics';

type OnboardingTask = {
  id: string;
  title: string;
  description: string;
  cta?: {
    label: string;
    href: string;
  };
  event: string;
};

type TaskState = OnboardingTask & {
  completed: boolean;
  completedAt?: string;
};

const BASE_TASKS: OnboardingTask[] = [
  {
    id: 'connect-data',
    title: 'Connect financial data',
    description: 'Link your accounting system to unlock AI-powered analytics.',
    cta: { label: 'Connect accounting', href: '/integrations' },
    event: 'onboarding_connect_data',
  },
  {
    id: 'create-deal',
    title: 'Create your first deal',
    description: 'Set up a pipeline entry so the team can collaborate.',
    cta: { label: 'Add deal', href: '/deals/new' },
    event: 'onboarding_create_deal',
  },
  {
    id: 'invite-team',
    title: 'Invite a team member',
    description: 'Bring collaborators into the workspace to accelerate diligence.',
    cta: { label: 'Invite teammate', href: '/teams/invite' },
    event: 'onboarding_invite_team',
  },
  {
    id: 'upload-document',
    title: 'Upload a document',
    description: 'Add diligence files to enable document collaboration and AI summaries.',
    cta: { label: 'Upload', href: '/documents' },
    event: 'onboarding_upload_document',
  },
  {
    id: 'schedule-demo',
    title: 'Schedule a strategy session',
    description: 'Book time with our team to tailor the platform to your mandate.',
    cta: { label: 'Book session', href: '/calendar/strategy' },
    event: 'onboarding_schedule_strategy',
  },
];

const usePersistedTasks = (userId?: string | null) => {
  const [tasks, setTasks] = useState<TaskState[]>(() =>
    BASE_TASKS.map((task) => ({ ...task, completed: false }))
  );

  useEffect(() => {
    if (!userId || typeof window === 'undefined') return;
    const stored = window.localStorage.getItem(`ma-onboarding-${userId}`);
    if (!stored) return;

    try {
      const parsed = JSON.parse(stored) as TaskState[];
      const merged = BASE_TASKS.map((base) => {
        const existing = parsed.find((task) => task.id === base.id);
        return {
          ...base,
          completed: existing?.completed ?? false,
          completedAt: existing?.completedAt,
        } satisfies TaskState;
      });
      setTasks(merged);
    } catch (error) {
      console.warn('Failed to parse onboarding state', error);
    }
  }, [userId]);

  useEffect(() => {
    if (!userId || typeof window === 'undefined') return;
    window.localStorage.setItem(`ma-onboarding-${userId}`, JSON.stringify(tasks));
  }, [tasks, userId]);

  return [tasks, setTasks] as const;
};

const OnboardingChecklist = () => {
  const { user } = useUser();
  const userId = user?.id ?? null;
  const [tasks, setTasks] = usePersistedTasks(userId);

  const completion = useMemo(() => {
    const total = tasks.length;
    const completed = tasks.filter((task) => task.completed).length;
    const percentage = total === 0 ? 0 : Math.round((completed / total) * 100);
    return { total, completed, percentage };
  }, [tasks]);

  const handleComplete = (task: TaskState) => {
    setTasks((prev) =>
      prev.map((item) =>
        item.id === task.id
          ? {
              ...item,
              completed: !item.completed,
              completedAt: !item.completed ? new Date().toISOString() : undefined,
            }
          : item
      )
    );

    trackEvent(task.event, {
      action: task.completed ? 'undo' : 'complete',
      task_id: task.id,
    });
  };

  if (!user) return null;

  return (
    <Card className="mb-8 border-primary-100 dark:border-primary-900">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Let’s get you set up</span>
          <Badge variant={completion.completed === completion.total ? 'default' : 'secondary'}>
            {completion.completed}/{completion.total} complete
          </Badge>
        </CardTitle>
        <CardDescription>
          Complete these steps to unlock the full value of the M&A platform. Your progress is saved automatically.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Progress value={completion.percentage} className="h-2" />
          <p className="text-sm text-muted-foreground">
            {completion.percentage}% complete · Finish all steps to trigger concierge outreach.
          </p>
        </div>

        <div className="space-y-4">
          {tasks.map((task) => (
            <motion.div
              key={task.id}
              layout
              className={`flex flex-col gap-2 rounded-lg border p-4 transition-colors ${
                task.completed ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/30' : 'border-border bg-card'
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2
                      className={`h-5 w-5 ${task.completed ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'}`}
                    />
                    <h3 className="font-semibold">{task.title}</h3>
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">{task.description}</p>
                </div>
                <Button variant={task.completed ? 'outline' : 'default'} size="sm" onClick={() => handleComplete(task)}>
                  {task.completed ? 'Mark incomplete' : 'Mark complete'}
                </Button>
              </div>

              {task.cta && !task.completed && (
                <Button variant="ghost" size="sm" asChild className="self-start">
                  <a href={task.cta.href} className="flex items-center gap-1">
                    {task.cta.label}
                    <ArrowRight className="h-3 w-3" />
                  </a>
                </Button>
              )}
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default OnboardingChecklist;
