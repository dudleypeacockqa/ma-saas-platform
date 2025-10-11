/**
 * Advanced Analytics - Cohorts, Funnels, and User Journeys
 */

import { trackEvent } from './analytics';

// Storage keys
const STORAGE_KEYS = {
  SESSION_ID: 'analytics_session_id',
  USER_ID: 'analytics_user_id',
  COHORT: 'analytics_cohort',
  FUNNEL_STATE: 'analytics_funnel_state',
};

/**
 * Generate or retrieve session ID
 */
function getSessionId() {
  let sessionId = sessionStorage.getItem(STORAGE_KEYS.SESSION_ID);
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    sessionStorage.setItem(STORAGE_KEYS.SESSION_ID, sessionId);
  }
  return sessionId;
}

/**
 * Get or set user cohort
 */
export function getUserCohort() {
  let cohort = localStorage.getItem(STORAGE_KEYS.COHORT);
  if (!cohort) {
    // Assign cohort based on signup date
    const signupDate = new Date();
    cohort = `${signupDate.getFullYear()}-W${Math.ceil((signupDate.getDate() + signupDate.getDay()) / 7)}`;
    localStorage.setItem(STORAGE_KEYS.COHORT, cohort);
  }
  return cohort;
}

/**
 * Track funnel step
 * @param {string} funnelName - Name of the funnel (e.g., 'signup', 'checkout')
 * @param {string} step - Step name (e.g., 'landing', 'form', 'confirmation')
 * @param {object} data - Additional data
 */
export function trackFunnelStep(funnelName, step, data = {}) {
  const sessionId = getSessionId();
  const cohort = getUserCohort();

  // Get current funnel state
  let funnelState = JSON.parse(sessionStorage.getItem(STORAGE_KEYS.FUNNEL_STATE) || '{}');

  if (!funnelState[funnelName]) {
    funnelState[funnelName] = {
      steps: [],
      startTime: Date.now(),
    };
  }

  // Add step to funnel
  funnelState[funnelName].steps.push({
    step,
    timestamp: Date.now(),
    data,
  });

  sessionStorage.setItem(STORAGE_KEYS.FUNNEL_STATE, JSON.stringify(funnelState));

  // Track event
  trackEvent('funnel_step', {
    funnel: funnelName,
    step,
    sessionId,
    cohort,
    stepNumber: funnelState[funnelName].steps.length,
    timeInFunnel: Date.now() - funnelState[funnelName].startTime,
    ...data,
  });
}

/**
 * Track funnel completion
 * @param {string} funnelName - Name of the funnel
 * @param {object} data - Additional data
 */
export function completeFunnel(funnelName, data = {}) {
  const sessionId = getSessionId();
  const cohort = getUserCohort();

  let funnelState = JSON.parse(sessionStorage.getItem(STORAGE_KEYS.FUNNEL_STATE) || '{}');

  if (funnelState[funnelName]) {
    const totalTime = Date.now() - funnelState[funnelName].startTime;
    const steps = funnelState[funnelName].steps;

    trackEvent('funnel_completed', {
      funnel: funnelName,
      sessionId,
      cohort,
      totalSteps: steps.length,
      totalTime,
      stepsCompleted: steps.map((s) => s.step),
      ...data,
    });

    // Clear funnel state
    delete funnelState[funnelName];
    sessionStorage.setItem(STORAGE_KEYS.FUNNEL_STATE, JSON.stringify(funnelState));
  }
}

/**
 * Track funnel abandonment
 * @param {string} funnelName - Name of the funnel
 * @param {string} reason - Reason for abandonment
 */
export function abandonFunnel(funnelName, reason = 'unknown') {
  const sessionId = getSessionId();
  const cohort = getUserCohort();

  let funnelState = JSON.parse(sessionStorage.getItem(STORAGE_KEYS.FUNNEL_STATE) || '{}');

  if (funnelState[funnelName]) {
    const steps = funnelState[funnelName].steps;
    const lastStep = steps[steps.length - 1];

    trackEvent('funnel_abandoned', {
      funnel: funnelName,
      sessionId,
      cohort,
      lastStep: lastStep?.step,
      stepsCompleted: steps.length,
      reason,
    });

    delete funnelState[funnelName];
    sessionStorage.setItem(STORAGE_KEYS.FUNNEL_STATE, JSON.stringify(funnelState));
  }
}

/**
 * Track user cohort behavior
 * @param {string} action - Action taken
 * @param {object} data - Additional data
 */
export function trackCohortBehavior(action, data = {}) {
  const cohort = getUserCohort();
  const sessionId = getSessionId();

  trackEvent('cohort_behavior', {
    cohort,
    sessionId,
    action,
    daysSinceSignup: getDaysSinceSignup(),
    ...data,
  });
}

/**
 * Calculate days since signup based on cohort
 */
function getDaysSinceSignup() {
  const cohort = getUserCohort();
  const [year, week] = cohort.split('-W');
  const cohortDate = new Date(year, 0, 1 + (week - 1) * 7);
  return Math.floor((Date.now() - cohortDate.getTime()) / (1000 * 60 * 60 * 24));
}

/**
 * Track A/B test variant
 * @param {string} experimentName - Name of the experiment
 * @param {string} variant - Variant assigned (A, B, etc.)
 */
export function trackExperiment(experimentName, variant) {
  const sessionId = getSessionId();
  const cohort = getUserCohort();

  trackEvent('experiment_view', {
    experiment: experimentName,
    variant,
    sessionId,
    cohort,
  });
}

/**
 * Track conversion for A/B test
 * @param {string} experimentName - Name of the experiment
 * @param {string} variant - Variant that converted
 * @param {string} goal - Conversion goal
 */
export function trackConversion(experimentName, variant, goal) {
  const sessionId = getSessionId();
  const cohort = getUserCohort();

  trackEvent('experiment_conversion', {
    experiment: experimentName,
    variant,
    goal,
    sessionId,
    cohort,
  });
}

/**
 * User Journey Tracking
 */
export class UserJourney {
  constructor(journeyName) {
    this.journeyName = journeyName;
    this.sessionId = getSessionId();
    this.cohort = getUserCohort();
    this.startTime = Date.now();
    this.touchpoints = [];
  }

  addTouchpoint(touchpoint, data = {}) {
    this.touchpoints.push({
      touchpoint,
      timestamp: Date.now(),
      data,
    });

    trackEvent('journey_touchpoint', {
      journey: this.journeyName,
      touchpoint,
      sessionId: this.sessionId,
      cohort: this.cohort,
      touchpointNumber: this.touchpoints.length,
      timeInJourney: Date.now() - this.startTime,
      ...data,
    });
  }

  complete(data = {}) {
    trackEvent('journey_completed', {
      journey: this.journeyName,
      sessionId: this.sessionId,
      cohort: this.cohort,
      totalTouchpoints: this.touchpoints.length,
      totalTime: Date.now() - this.startTime,
      touchpoints: this.touchpoints.map((t) => t.touchpoint),
      ...data,
    });
  }
}

/**
 * Predefined Funnels
 */
export const Funnels = {
  SIGNUP: 'signup',
  ONBOARDING: 'onboarding',
  DEAL_CREATION: 'deal_creation',
  PAYMENT: 'payment',
  REFERRAL: 'referral',
};

/**
 * Predefined Funnel Steps
 */
export const FunnelSteps = {
  [Funnels.SIGNUP]: {
    LANDING: 'landing',
    FORM: 'form',
    VERIFICATION: 'verification',
    CONFIRMATION: 'confirmation',
  },
  [Funnels.ONBOARDING]: {
    WELCOME: 'welcome',
    PROFILE: 'profile',
    ORGANIZATION: 'organization',
    INVITE_TEAM: 'invite_team',
    COMPLETE: 'complete',
  },
  [Funnels.DEAL_CREATION]: {
    START: 'start',
    BASIC_INFO: 'basic_info',
    DOCUMENTS: 'documents',
    VALUATION: 'valuation',
    REVIEW: 'review',
    SUBMIT: 'submit',
  },
  [Funnels.PAYMENT]: {
    PLAN_SELECTION: 'plan_selection',
    BILLING_INFO: 'billing_info',
    PAYMENT_METHOD: 'payment_method',
    CONFIRMATION: 'confirmation',
  },
};

/**
 * Initialize analytics on page load
 */
if (typeof window !== 'undefined') {
  // Track page unload (potential funnel abandonment)
  window.addEventListener('beforeunload', () => {
    const funnelState = JSON.parse(sessionStorage.getItem(STORAGE_KEYS.FUNNEL_STATE) || '{}');

    // Check for active funnels
    Object.keys(funnelState).forEach((funnelName) => {
      abandonFunnel(funnelName, 'page_unload');
    });
  });

  // Track visibility changes (tab switching)
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      trackEvent('tab_hidden', {
        sessionId: getSessionId(),
        cohort: getUserCohort(),
      });
    } else {
      trackEvent('tab_visible', {
        sessionId: getSessionId(),
        cohort: getUserCohort(),
      });
    }
  });
}

export { getSessionId };
