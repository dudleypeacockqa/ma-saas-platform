import { SignUp } from '@clerk/clerk-react';

const SignUpPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Join M&A Platform
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Start your professional M&A journey
          </p>
        </div>
        <SignUp
          redirectUrl="/deals"
          appearance={{
            elements: {
              formButtonPrimary: 'bg-blue-600 hover:bg-blue-700',
              card: 'shadow-lg',
            },
          }}
        />
      </div>
    </div>
  );
};

export default SignUpPage;
