import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { MoreHorizontal, PlusCircle, Search } from 'lucide-react'

const DealsPage = () => {
  const [searchTerm, setSearchTerm] = useState("")

  const deals = [
    { id: 1, name: "Project Phoenix", stage: "Due Diligence", value: "$50M", closeDate: "2025-12-15", owner: "John Doe" },
    { id: 2, name: "Project Titan", stage: "Negotiation", value: "$120M", closeDate: "2026-02-28", owner: "Jane Smith" },
    { id: 3, name: "Project Nova", stage: "Initial Contact", value: "$25M", closeDate: "2026-01-31", owner: "Peter Jones" },
    { id: 4, name: "Project Galaxy", stage: "Closed - Won", value: "$75M", closeDate: "2025-10-01", owner: "John Doe" },
    { id: 5, name: "Project Comet", stage: "Term Sheet", value: "$30M", closeDate: "2025-11-30", owner: "Alice Williams" },
  ]

  const filteredDeals = deals.filter(deal =>
    deal.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Deals</h1>
          <p className="text-muted-foreground">Manage your M&A deal pipeline.</p>
        </div>
        <Button>
          <PlusCircle className="mr-2 h-4 w-4" />
          Create Deal
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>All Deals</CardTitle>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Search deals..."
                  className="pl-8"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by stage" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Stages</SelectItem>
                  <SelectItem value="initial-contact">Initial Contact</SelectItem>
                  <SelectItem value="due-diligence">Due Diligence</SelectItem>
                  <SelectItem value="negotiation">Negotiation</SelectItem>
                  <SelectItem value="term-sheet">Term Sheet</SelectItem>
                  <SelectItem value="closed-won">Closed - Won</SelectItem>
                  <SelectItem value="closed-lost">Closed - Lost</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Deal Name</TableHead>
                <TableHead>Stage</TableHead>
                <TableHead>Value</TableHead>
                <TableHead>Expected Close Date</TableHead>
                <TableHead>Owner</TableHead>
                <TableHead><span className="sr-only">Actions</span></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredDeals.map(deal => (
                <TableRow key={deal.id}>
                  <TableCell className="font-medium">{deal.name}</TableCell>
                  <TableCell>
                    <Badge variant={deal.stage === 'Closed - Won' ? 'default' : 'secondary'}>{deal.stage}</Badge>
                  </TableCell>
                  <TableCell>{deal.value}</TableCell>
                  <TableCell>{deal.closeDate}</TableCell>
                  <TableCell>{deal.owner}</TableCell>
                  <TableCell>
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

export default DealsPage
