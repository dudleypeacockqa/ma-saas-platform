import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser, useAuth } from '@clerk/clerk-react';
import { Button } from '@/components/ui/button';
import { Loader2, CreditCard, LogIn, Check } from 'lucide-react';
import { toast } from 'sonner';

interface CheckoutButtonProps {
  planName: string;
  planTier: string;
  price: string;
  interval?: string;
  isCurrentPlan?: boolean;
  variant?: 'default' | 'outline' | 'secondary' | 'ghost' | 'link' | 'destructive';
  className?: string;
}

export const CheckoutButton = ({
  planName,
  planTier,
  price,
  interval = 'month',
  isCurrentPlan = false,
  variant = 'default',
  className = ''
}: CheckoutButtonProps) => {
  const { isSignedIn, userId } = useUser();
  const { getToken } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleCheckout = async () => {
    // If not signed in, redirect to sign-up
    if (!isSignedIn) {
      toast.info('Please sign up to choose a plan');
      navigate('/sign-up');
      return;
    }

    setIsLoading(true);

    try {
      // Get authentication token
      const token = await getToken();

      if (!token) {
        toast.error('Authentication failed. Please sign in again.');
        navigate('/sign-in');
        return;
      }

      // Create checkout session
      const response = await fetch(`${API_BASE_URL}/api/payments/checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          price_id: `price_${planTier}`,
          success_url: `${window.location.origin}/subscription/success?session_id={CHECKOUT_SESSION_ID}`,
          cancel_url: `${window.location.origin}/subscription/cancel`,
          mode: 'subscription'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create checkout session');
      }

      const data = await response.json();

      // Redirect to Stripe Checkout
      if (data.session_url) {
        window.location.href = data.session_url;
      } else {
        throw new Error('No checkout URL received');
      }

    } catch (error) {
      console.error('Checkout error:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to start checkout. Please try again.');
      setIsLoading(false);
    }
  };

  // If current plan, show indicator
  if (isCurrentPlan) {
    return (
      <Button
        className={`w-full ${className}`}
        variant="outline"
        disabled
      >
        <Check className="h-4 w-4 mr-2" />
        Current Plan
      </Button>
    );
  }

  // Button for non-authenticated users
  if (!isSignedIn) {
    return (
      <Button
        className={`w-full ${className}`}
        variant={variant}
        onClick={handleCheckout}
        disabled={isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            Loading...
          </>
        ) : (
          <>
            <LogIn className="h-4 w-4 mr-2" />
            Sign Up & Choose Plan
          </>
        )}
      </Button>
    );
  }

  // Button for authenticated users
  return (
    <Button
      className={`w-full ${className}`}
      variant={variant}
      onClick={handleCheckout}
      disabled={isLoading}
    >
      {isLoading ? (
        <>
          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          Creating checkout...
        </>
      ) : (
        <>
          <CreditCard className="h-4 w-4 mr-2" />
          Choose {planName}
        </>
      )}
    </Button>
  );
};

export default CheckoutButton;
