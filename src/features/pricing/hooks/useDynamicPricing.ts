import { useEffect, useMemo, useState } from 'react';

import {
  UserPricingContext,
  createPricingSnapshot,
  buildPricingContext,
  DynamicPricingResult,
  persistExperimentVariant,
} from '@/services/pricing';
import { trackConversionStep } from '@/services/analytics';

interface DynamicPricingOptions {
  initialContext?: Partial<UserPricingContext>;
}

export const useDynamicPricing = (options?: DynamicPricingOptions) => {
  const [context, setContext] = useState<UserPricingContext>(() =>
    buildPricingContext(options?.initialContext),
  );
  const [pricing, setPricing] = useState<DynamicPricingResult[]>(() =>
    createPricingSnapshot(buildPricingContext(options?.initialContext)),
  );

  useEffect(() => {
    const snapshot = createPricingSnapshot(context);
    setPricing(snapshot);
  }, [context]);

  const toggleBillingInterval = (billingInterval: UserPricingContext['billingInterval']) => {
    setContext((prev) => ({ ...prev, billingInterval }));
    trackConversionStep('toggle_billing_interval', {
      interval: billingInterval,
    });
  };

  const updateExperimentVariant = (variant: 'A' | 'B') => {
    persistExperimentVariant(variant);
    setContext((prev) => ({ ...prev, experimentVariant: variant }));
  };

  const value = useMemo(
    () => ({
      context,
      pricing,
      toggleBillingInterval,
      updateExperimentVariant,
      setContext,
    }),
    [context, pricing],
  );

  return value;
};
