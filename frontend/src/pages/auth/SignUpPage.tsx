import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSignUp } from '@clerk/clerk-react';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, MailCheck, ShieldCheck } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';

const passwordSchema = z
  .string()
  .min(10, { message: 'Password must be at least 10 characters long.' })
  .regex(/[A-Z]/, { message: 'Include at least one uppercase letter.' })
  .regex(/[a-z]/, { message: 'Include at least one lowercase letter.' })
  .regex(/[0-9]/, { message: 'Include at least one number.' })
  .regex(/[^A-Za-z0-9]/, { message: 'Include at least one special character.' });

const registrationSchema = z
  .object({
    firstName: z.string().min(2, { message: 'First name must have at least 2 characters.' }),
    lastName: z.string().min(2, { message: 'Last name must have at least 2 characters.' }),
    email: z.string().email({ message: 'Enter a valid work email address.' }),
    password: passwordSchema,
    confirmPassword: z.string(),
    company: z.string().optional(),
  })
  .refine((values) => values.password === values.confirmPassword, {
    path: ['confirmPassword'],
    message: 'Passwords do not match.',
  });

const verificationSchema = z.object({
  code: z
    .string()
    .min(6, { message: 'Enter the 6-digit verification code.' })
    .max(6, { message: 'Verification code is 6 digits.' })
    .regex(/^[0-9]{6}$/, { message: 'Use the 6-digit code sent to your email.' }),
});

const passwordChecklist = [
  { label: '10+ characters', test: (value: string) => value.length >= 10 },
  { label: 'Uppercase letter', test: (value: string) => /[A-Z]/.test(value) },
  { label: 'Lowercase letter', test: (value: string) => /[a-z]/.test(value) },
  { label: 'Number', test: (value: string) => /[0-9]/.test(value) },
  { label: 'Special character', test: (value: string) => /[^A-Za-z0-9]/.test(value) },
];

const SignUpPage = () => {
  const navigate = useNavigate();
  const { isLoaded, signUp, setActive } = useSignUp();
  const [step, setStep] = useState<'form' | 'verify'>('form');
  const [pendingEmail, setPendingEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);

  const form = useForm<z.infer<typeof registrationSchema>>({
    resolver: zodResolver(registrationSchema),
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      confirmPassword: '',
      company: '',
    },
  });

  const verificationForm = useForm<z.infer<typeof verificationSchema>>({
    resolver: zodResolver(verificationSchema),
    defaultValues: { code: '' },
  });

  const passwordValue = form.watch('password');

  const checklist = useMemo(
    () => passwordChecklist.map(({ label, test }) => ({ label, passed: test(passwordValue ?? '') })),
    [passwordValue]
  );

  useEffect(() => {
    if (!isLoaded) {
      form.reset();
      verificationForm.reset();
      setStep('form');
      setPendingEmail('');
    }
  }, [isLoaded, form, verificationForm]);

  const parseClerkError = (error: unknown) => {
    if (typeof error === 'string') {
      return error;
    }

    if (error && typeof error === 'object' && 'errors' in error && Array.isArray(error.errors)) {
      return error.errors.map((err: any) => err.longMessage || err.message).filter(Boolean).join('\n') || 'Unable to complete registration.';
    }

    return 'Unable to complete registration. Please try again.';
  };

  const handleRegistration = async (values: z.infer<typeof registrationSchema>) => {
    if (!isLoaded || !signUp) {
      toast.error('Registration is unavailable. Try again shortly.');
      return;
    }

    setIsSubmitting(true);

    try {
      await signUp.create({
        emailAddress: values.email,
        password: values.password,
        firstName: values.firstName,
        lastName: values.lastName,
        unsafeMetadata: values.company ? { company: values.company } : undefined,
      });

      await signUp.prepareEmailAddressVerification({ strategy: 'email_code' });

      setPendingEmail(values.email);
      setStep('verify');
      verificationForm.reset();

      toast.success('We sent a verification code to your email. Enter it below to activate your account.');
    } catch (error) {
      toast.error(parseClerkError(error));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleVerification = async (values: z.infer<typeof verificationSchema>) => {
    if (!isLoaded || !signUp) {
      toast.error('Verification is unavailable. Try again shortly.');
      return;
    }

    setIsVerifying(true);

    try {
      const verificationAttempt = await signUp.attemptEmailAddressVerification({ code: values.code });

      if (verificationAttempt.status === 'complete') {
        if (verificationAttempt.createdSessionId) {
          await setActive({ session: verificationAttempt.createdSessionId });
        }

        toast.success('Registration complete! Redirecting to your dashboard.');
        navigate('/deals', { replace: true });
      } else {
        toast.error('We could not verify your email. Please try again.');
      }
    } catch (error) {
      toast.error(parseClerkError(error));
    } finally {
      setIsVerifying(false);
    }
  };

  const resendVerification = async () => {
    if (!isLoaded || !signUp) {
      toast.error('Unable to resend verification email right now.');
      return;
    }

    try {
      await signUp.prepareEmailAddressVerification({ strategy: 'email_code' });
      toast.success('Verification email resent. Check your inbox.');
    } catch (error) {
      toast.error(parseClerkError(error));
    }
  };

  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-4 text-gray-600">
          <Loader2 className="h-8 w-8 animate-spin" aria-hidden="true" />
          <p className="text-sm">Preparing secure registration…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-16">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] items-start">
          <Card className="shadow-xl">
            <CardHeader>
              <CardTitle className="text-3xl font-bold text-gray-900">Create your account</CardTitle>
              <CardDescription className="text-base text-gray-600">
                Join 156+ M&A professionals accelerating deal flow with 100 Days &amp; Beyond.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {step === 'form' ? (
                <Form {...form}>
                  <form className="space-y-6" onSubmit={form.handleSubmit(handleRegistration)}>
                    <div className="grid gap-4 sm:grid-cols-2">
                      <FormField
                        control={form.control}
                        name="firstName"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>First name</FormLabel>
                            <FormControl>
                              <Input placeholder="Jane" autoComplete="given-name" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="lastName"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Last name</FormLabel>
                            <FormControl>
                              <Input placeholder="Smith" autoComplete="family-name" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    <FormField
                      control={form.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Work email</FormLabel>
                          <FormControl>
                            <Input type="email" placeholder="you@firm.com" autoComplete="email" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="company"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Firm (optional)</FormLabel>
                          <FormControl>
                            <Input placeholder="Firm or practice name" {...field} />
                          </FormControl>
                          <FormDescription>Helps us customise onboarding and deal templates.</FormDescription>
                        </FormItem>
                      )}
                    />

                    <div className="grid gap-4 sm:grid-cols-2">
                      <FormField
                        control={form.control}
                        name="password"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Password</FormLabel>
                            <FormControl>
                              <Input type="password" autoComplete="new-password" placeholder="Create a strong password" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="confirmPassword"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Confirm password</FormLabel>
                            <FormControl>
                              <Input type="password" autoComplete="new-password" placeholder="Re-enter password" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    <div className="rounded-lg border border-gray-100 bg-gray-50/60 p-4">
                      <p className="mb-2 text-sm font-medium text-gray-700 flex items-center gap-2">
                        <ShieldCheck className="h-4 w-4 text-blue-600" aria-hidden="true" />
                        Password requirements
                      </p>
                      <ul className="grid gap-1 text-sm text-gray-600 sm:grid-cols-2">
                        {checklist.map((item) => (
                          <li key={item.label} className={item.passed ? 'text-green-600' : 'text-gray-500'}>
                            <span className="mr-2">{item.passed ? '✓' : '•'}</span>
                            {item.label}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <Button type="submit" className="w-full" disabled={isSubmitting}>
                      {isSubmitting ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
                          Creating account…
                        </>
                      ) : (
                        'Create account'
                      )}
                    </Button>
                  </form>
                </Form>
              ) : (
                <Form {...verificationForm}>
                  <form className="space-y-6" onSubmit={verificationForm.handleSubmit(handleVerification)}>
                    <div className="rounded-lg border border-blue-100 bg-blue-50/60 p-4 text-blue-900">
                      <div className="flex items-start gap-3">
                        <MailCheck className="mt-1 h-5 w-5 text-blue-600" aria-hidden="true" />
                        <div>
                          <p className="font-semibold">Check your email</p>
                          <p className="text-sm">
                            We sent a verification code to <span className="font-medium">{pendingEmail}</span>. Enter it below to activate
                            your account.
                          </p>
                        </div>
                      </div>
                    </div>

                    <FormField
                      control={verificationForm.control}
                      name="code"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Verification code</FormLabel>
                          <FormControl>
                            <Input inputMode="numeric" maxLength={6} placeholder="123456" {...field} />
                          </FormControl>
                          <FormDescription>Didn’t receive the code? Check your spam folder or resend below.</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <Button type="button" variant="outline" onClick={resendVerification} className="sm:w-auto">
                        Resend verification email
                      </Button>
                      <Button type="submit" className="sm:w-auto" disabled={isVerifying}>
                        {isVerifying ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
                            Verifying…
                          </>
                        ) : (
                          'Confirm account'
                        )}
                      </Button>
                    </div>
                  </form>
                </Form>
              )}
            </CardContent>
          </Card>

          <div className="space-y-6">
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-semibold text-gray-900">Enterprise-grade security</h2>
              <p className="mt-3 text-sm text-gray-600">
                We use Clerk for authentication, enforce strong passwords, and require email verification so your workspace stays secure.
              </p>
              <ul className="mt-4 space-y-2 text-sm text-gray-700">
                <li>• SOC 2 Type II infrastructure</li>
                <li>• Automated email verification</li>
                <li>• Single Sign-On ready</li>
              </ul>
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-semibold text-gray-900">Need help?</h2>
              <p className="mt-3 text-sm text-gray-600">
                Email <a href="mailto:support@100daysandbeyond.com" className="text-blue-600 hover:underline">support@100daysandbeyond.com</a> for onboarding assistance or enterprise provisioning.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignUpPage;
