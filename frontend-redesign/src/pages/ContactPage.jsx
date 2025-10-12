import { Button } from '@/components/ui/button'
import { Phone, Mail, MapPin, Clock } from 'lucide-react'

const ContactPage = () => {
  return (
    <div className="min-h-screen bg-white pt-16">
      <section className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl sm:text-5xl font-bold text-slate-900 mb-6">
            Contact Our Sales Team
          </h1>
          <p className="text-xl text-slate-600 mb-8 max-w-3xl mx-auto">
            Ready to transform your M&A process? Get in touch with our experts.
          </p>
        </div>
      </section>
    </div>
  )
}

export default ContactPage
