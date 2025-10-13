import { trackFunnelStage, FunnelStage } from '@/lib/advancedAnalytics';

export interface FunnelCheckpoint {
  stage: FunnelStage;
  timestamp: number;
  metadata?: Record<string, unknown>;
}

export interface FunnelSummary {
  checkpoints: FunnelCheckpoint[];
  totalDurationMs: number;
  stageDurations: Partial<Record<FunnelStage, number>>;
}

const STORAGE_KEY = 'ma_pricing_funnel_v1';

const loadCheckpoints = (): FunnelCheckpoint[] => {
  try {
    const stored = sessionStorage.getItem(STORAGE_KEY);
    if (!stored) return [];
    const parsed = JSON.parse(stored) as FunnelCheckpoint[];
    return parsed.map((checkpoint) => ({
      ...checkpoint,
      timestamp: checkpoint.timestamp,
    }));
  } catch (error) {
    console.warn('Unable to load funnel checkpoints', error);
    return [];
  }
};

const saveCheckpoints = (checkpoints: FunnelCheckpoint[]) => {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(checkpoints));
  } catch (error) {
    console.warn('Unable to persist funnel checkpoints', error);
  }
};

export const clearFunnel = () => {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.warn('Unable to clear funnel checkpoints', error);
  }
};

export const markFunnelStage = (stage: FunnelStage, metadata?: Record<string, unknown>) => {
  const checkpoints = loadCheckpoints();
  const timestamp = Date.now();

  const nextCheckpoints = [...checkpoints, { stage, timestamp, metadata }];
  saveCheckpoints(nextCheckpoints);
  trackFunnelStage(stage, { metadata });
};

export const getFunnelSummary = (): FunnelSummary | null => {
  const checkpoints = loadCheckpoints();
  if (checkpoints.length === 0) return null;

  const stageDurations = checkpoints.reduce<Partial<Record<FunnelStage, number>>>((acc, checkpoint, index) => {
    const next = checkpoints[index + 1];
    const duration = next ? next.timestamp - checkpoint.timestamp : 0;
    acc[checkpoint.stage] = (acc[checkpoint.stage] ?? 0) + duration;
    return acc;
  }, {});

  const totalDuration = checkpoints.length > 1
    ? checkpoints[checkpoints.length - 1].timestamp - checkpoints[0].timestamp
    : 0;

  return {
    checkpoints,
    totalDurationMs: totalDuration,
    stageDurations,
  };
};
