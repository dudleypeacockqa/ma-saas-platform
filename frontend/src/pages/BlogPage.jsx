import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowRight } from "lucide-react"

const BlogPage = () => {
  const posts = [
    {
      id: 1,
      title: "M&A Market Outlook for H2 2025",
      description: "An in-depth analysis of the trends and predictions shaping the M&A landscape in the second half of 2025.",
      category: "Market Trends",
      date: "October 7, 2025",
      author: "Manus AI",
      image: "/blog/ma-market-outlook.jpg"
    },
    {
      id: 2,
      title: "The Art of the Term Sheet: A Founder\'s Guide",
      description: "Learn how to navigate term sheet negotiations and secure the best possible terms for your company.",
      category: "Negotiation",
      date: "September 28, 2025",
      author: "Guest Author",
      image: "/blog/term-sheet.jpg"
    },
    {
      id: 3,
      title: "Top 5 Due Diligence Red Flags to Watch Out For",
      description: "Discover the critical red flags to look for during due diligence to avoid costly mistakes.",
      category: "Due Diligence",
      date: "September 15, 2025",
      author: "Manus AI",
      image: "/blog/due-diligence.jpg"
    },
  ]

  return (
    <div className="p-8">
      <div className="text-center mb-16">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6">
          100 Days & Beyond Blog
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
          Insights and analysis for M&A professionals.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-8 max-w-7xl mx-auto">
        {posts.map(post => (
          <Card key={post.id} className="flex flex-col">
            <img src={post.image} alt={post.title} className="rounded-t-lg h-48 object-cover" />
            <CardHeader>
              <Badge variant="secondary" className="mb-2 w-fit">{post.category}</Badge>
              <CardTitle className="text-xl font-bold">{post.title}</CardTitle>
              <CardDescription className="text-sm text-muted-foreground pt-2">
                {post.date} by {post.author}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-grow">
              <p className="text-muted-foreground">{post.description}</p>
            </CardContent>
            <CardFooter>
              <a href="#" className="flex items-center font-semibold text-blue-600 hover:text-blue-800">
                Read More
                <ArrowRight className="ml-2 h-4 w-4" />
              </a>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default BlogPage
