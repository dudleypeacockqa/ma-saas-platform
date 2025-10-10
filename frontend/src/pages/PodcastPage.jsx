import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { MoreHorizontal, PlusCircle, PlayCircle, Rss } from 'lucide-react'

const PodcastPage = () => {
  const episodes = [
    { id: 1, title: "The Art of the Term Sheet", status: "Published", duration: "32:15", publishedDate: "2025-10-01", downloads: 1258 },
    { id: 2, title: "Navigating Due Diligence", status: "Published", duration: "45:30", publishedDate: "2025-09-24", downloads: 2103 },
    { id: 3, title: "Post-Merger Integration Strategies", status: "Scheduled", duration: "38:00", publishedDate: "2025-10-08", downloads: 0 },
    { id: 4, title: "Interview with a PE Titan", status: "Draft", duration: "55:00", publishedDate: "", downloads: 0 },
  ]

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Podcast Management</h1>
          <p className="text-muted-foreground">Manage your "100 Days and Beyond" podcast episodes.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Rss className="mr-2 h-4 w-4" />
            RSS Feed
          </Button>
          <Button>
            <PlusCircle className="mr-2 h-4 w-4" />
            New Episode
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Episodes</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Published Date</TableHead>
                <TableHead>Downloads</TableHead>
                <TableHead><span className="sr-only">Actions</span></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {episodes.map(episode => (
                <TableRow key={episode.id}>
                  <TableCell className="font-medium">{episode.title}</TableCell>
                  <TableCell>
                    <Badge variant={episode.status === 'Published' ? 'default' : 'secondary'}>{episode.status}</Badge>
                  </TableCell>
                  <TableCell>{episode.duration}</TableCell>
                  <TableCell>{episode.publishedDate}</TableCell>
                  <TableCell>{episode.downloads.toLocaleString()}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon">
                      <PlayCircle className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

export default PodcastPage
