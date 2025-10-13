import { useEffect, useMemo, useState } from 'react';
import { trackEvent, setUserProperties } from '@/lib/analytics';
import { trackEcommerceEvent } from '@/lib/advancedAnalytics';

export interface ExperimentVariant {
  id: string;
  weight?: number;
  name?: string;
  description?: string;
}

export interface ExperimentDefinition {
  key: string;
  description?: string;
  variants: ExperimentVariant[];
  defaultVariant?: string;
  targeting?: (context: ExperimentContext) => boolean;
}

export interface ExperimentContext {
  userId?: string;
  tier?: string | null;
  isTrialing?: boolean;
  segment?: string;
  region?: string;
  deviceType?: 'mobile' | 'desktop' | 'tablet';
}

export interface ExperimentAssignment {
  key: string;
  variant: string;
  name?: string;
}

const STORAGE_KEY = 'ma_experiment_assignments_v1';

type AssignmentMap = Record<string, ExperimentAssignment>;

let assignmentsCache: AssignmentMap | null = null;

const loadAssignments = (): AssignmentMap => {
  if (assignmentsCache) return assignmentsCache;

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      assignmentsCache = {};
      return assignmentsCache;
    }
    assignmentsCache = JSON.parse(stored) as AssignmentMap;
    return assignmentsCache;
  } catch (error) {
    console.warn('Unable to load experiment assignments', error);
    assignmentsCache = {};
    return assignmentsCache;
  }
};

const persistAssignments = (assignments: AssignmentMap) => {
  assignmentsCache = assignments;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(assignments));
  } catch (error) {
    console.warn('Unable to persist experiment assignments', error);
  }
};

const chooseVariant = (experiment: ExperimentDefinition): ExperimentVariant => {
  const variants = experiment.variants;
  const totalWeight = variants.reduce((sum, variant) => sum + (variant.weight ?? 1), 0);
  let threshold = Math.random() * totalWeight;

  for (const variant of variants) {
    threshold -= variant.weight ?? 1;
    if (threshold <= 0) {
      return variant;
    }
  }

  return variants[0];
};

const recordAssignment = (assignment: ExperimentAssignment, context?: ExperimentContext) => {
  trackEvent('experiment_assigned', {
    experiment_key: assignment.key,
    variant: assignment.variant,
    variant_name: assignment.name,
    tier: context?.tier,
    segment: context?.segment,
  });

  setUserProperties({
    [`exp_${assignment.key}`]: assignment.variant,
  });
};

const createAssignment = (
  experiment: ExperimentDefinition,
  context?: ExperimentContext,
): ExperimentAssignment => {
  const variant = chooseVariant(experiment);
  const assignment: ExperimentAssignment = {
    key: experiment.key,
    variant: variant.id,
    name: variant.name,
  };

  const assignments = loadAssignments();
  assignments[experiment.key] = assignment;
  persistAssignments(assignments);
  recordAssignment(assignment, context);
  return assignment;
};

export const getAssignment = (
  experiment: ExperimentDefinition,
  context?: ExperimentContext,
): ExperimentAssignment => {
  const assignments = loadAssignments();
  const existing = assignments[experiment.key];
  if (existing) {
    return existing;
  }

  return createAssignment(experiment, context);
};

export const initializeExperiments = (
  experiments: ExperimentDefinition[],
  context?: ExperimentContext,
): AssignmentMap => {
  const assignments = loadAssignments();
  const nextAssignments = { ...assignments };

  experiments.forEach((experiment) => {
    if (experiment.targeting && !experiment.targeting(context ?? {})) {
      return;
    }

    if (!nextAssignments[experiment.key]) {
      nextAssignments[experiment.key] = createAssignment(experiment, context);
    }
  });

  persistAssignments(nextAssignments);
  return nextAssignments;
};

export const logExperimentExposure = (
  experimentKey: string,
  variant: string,
  metadata?: Record<string, unknown>,
) => {
  trackEvent('experiment_exposure', {
    experiment_key: experimentKey,
    variant,
    ...metadata,
  });
};

export const logExperimentConversion = (
  experimentKey: string,
  variant: string,
  payload: {
    items: {
      item_id: string;
      item_name: string;
      price: number;
      currency: string;
      tier: string;
      billing_interval: 'monthly' | 'yearly';
    }[];
    value: number;
    currency: string;
  },
) => {
  trackEcommerceEvent('experiment_conversion', {
    ...payload,
    experiment: experimentKey,
    variant,
  });
};

export const useExperiment = (
  experiment: ExperimentDefinition,
  context?: ExperimentContext,
): ExperimentAssignment => {
  const [assignment, setAssignment] = useState<ExperimentAssignment | null>(() => {
    try {
      const stored = loadAssignments()[experiment.key];
      return stored ?? null;
    } catch (error) {
      console.warn('Unable to read experiment assignment', error);
      return null;
    }
  });

  useEffect(() => {
    if (assignment) return;

    const next = getAssignment(experiment, context);
    setAssignment(next);
  }, [experiment, context, assignment]);

  return useMemo(() => {
    if (assignment) return assignment;
    return {
      key: experiment.key,
      variant: experiment.defaultVariant ?? experiment.variants[0]?.id ?? 'control',
      name: experiment.variants[0]?.name,
    };
  }, [assignment, experiment]);
};
