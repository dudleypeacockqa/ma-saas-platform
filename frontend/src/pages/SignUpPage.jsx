import { SignUp } from "@clerk/clerk-react"

const SignUpPage = () => {
  return (
    <div className="flex justify-center items-center min-h-[calc(100vh-128px)]">
      <SignUp path="/sign-up" routing="path" signInUrl="/sign-in" />
    </div>
  )
}

export default SignUpPage
