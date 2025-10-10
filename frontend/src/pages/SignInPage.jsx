import { SignIn } from "@clerk/clerk-react"

const SignInPage = () => {
  return (
    <div className="flex justify-center items-center min-h-[calc(100vh-128px)]">
      <SignIn path="/sign-in" routing="path" signUpUrl="/sign-up" />
    </div>
  )
}

export default SignInPage
