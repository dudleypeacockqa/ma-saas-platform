import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { ArrowRight, FileText, BookOpen, Video } from 'lucide-react'

const ResourcesPage = () => {
  return (
    <div className="min-h-screen bg-white pt-16">
      <section className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl sm:text-5xl font-bold text-slate-900 mb-6">
            M&A Resources & Insights
          </h1>
          <p className="text-xl text-slate-600 mb-8 max-w-3xl mx-auto">
            Case studies, best practices, and industry insights to help you close deals faster.
          </p>
          <Link to="/dashboard">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4">
              Start Free Trial
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  )
}

export default ResourcesPage
