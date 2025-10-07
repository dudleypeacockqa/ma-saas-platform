import React, { useState } from 'react'
import { format } from 'date-fns'
import {
  Plus,
  Phone,
  Mail,
  Users,
  FileText,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Calendar,
  MessageSquare,
  Video,
  Loader2,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useDealActivities } from '@/hooks/useDeals'
import type { DealActivity, DealActivityCreate } from '@/services/dealService'
import { cn } from '@/lib/utils'

interface DealTimelineProps {
  dealId: string
}

const activityTypeIcons: Record<string, React.ReactNode> = {
  meeting: <Users className="h-4 w-4" />,
  call: <Phone className="h-4 w-4" />,
  email: <Mail className="h-4 w-4" />,
  note: <MessageSquare className="h-4 w-4" />,
  milestone: <CheckCircle className="h-4 w-4" />,
  stage_change: <TrendingUp className="h-4 w-4" />,
  document_uploaded: <FileText className="h-4 w-4" />,
  team_member_added: <Users className="h-4 w-4" />,
  milestone_created: <Calendar className="h-4 w-4" />,
  milestone_completed: <CheckCircle className="h-4 w-4" />,
  valuation_created: <TrendingUp className="h-4 w-4" />,
  video_call: <Video className="h-4 w-4" />,
  deal_created: <Plus className="h-4 w-4" />,
}

const activityTypeColors: Record<string, string> = {
  meeting: 'bg-blue-100 text-blue-700',
  call: 'bg-green-100 text-green-700',
  email: 'bg-purple-100 text-purple-700',
  note: 'bg-gray-100 text-gray-700',
  milestone: 'bg-yellow-100 text-yellow-700',
  stage_change: 'bg-indigo-100 text-indigo-700',
  document_uploaded: 'bg-orange-100 text-orange-700',
  team_member_added: 'bg-pink-100 text-pink-700',
  milestone_created: 'bg-yellow-100 text-yellow-700',
  milestone_completed: 'bg-green-100 text-green-700',
  valuation_created: 'bg-teal-100 text-teal-700',
  video_call: 'bg-blue-100 text-blue-700',
  deal_created: 'bg-emerald-100 text-emerald-700',
}

const activityFormSchema = z.object({
  activity_type: z.string().min(1, 'Activity type is required'),
  subject: z.string().min(1, 'Subject is required').max(255),
  description: z.string().optional(),
  participants: z.string().optional(),
  outcome: z.string().optional(),
  follow_up_required: z.boolean().default(false),
  follow_up_date: z.string().optional(),
})

type ActivityFormData = z.infer<typeof activityFormSchema>

export const DealTimeline: React.FC<DealTimelineProps> = ({ dealId }) => {
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const { activities, loading, error, createActivity, refetch } = useDealActivities(dealId)

  const form = useForm<ActivityFormData>({
    resolver: zodResolver(activityFormSchema),
    defaultValues: {
      activity_type: 'note',
      subject: '',
      description: '',
      participants: '',
      outcome: '',
      follow_up_required: false,
      follow_up_date: '',
    },
  })

  const handleSubmit = async (data: ActivityFormData) => {
    try {
      setSubmitting(true)

      // Parse participants
      const participantsArray = data.participants
        ? data.participants.split(',').map((p) => p.trim()).filter(Boolean)
        : []

      const activityData: DealActivityCreate = {
        activity_type: data.activity_type,
        subject: data.subject,
        description: data.description || undefined,
        participants: participantsArray.length > 0 ? participantsArray : undefined,
        outcome: data.outcome || undefined,
        follow_up_required: data.follow_up_required,
        follow_up_date: data.follow_up_date || undefined,
      }

      await createActivity(activityData)
      form.reset()
      setIsFormOpen(false)
    } catch (error) {
      console.error('Failed to create activity:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const formatActivityDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)

    if (diffInHours < 24) {
      return format(date, 'h:mm a')
    } else if (diffInHours < 48) {
      return 'Yesterday'
    } else if (diffInHours < 168) {
      return format(date, 'EEEE')
    } else {
      return format(date, 'MMM dd, yyyy')
    }
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="text-center text-muted-foreground">
            <AlertCircle className="h-8 w-8 mx-auto mb-2" />
            <p>Failed to load activities</p>
            <Button onClick={() => refetch()} variant="outline" className="mt-4">
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Activity Timeline</CardTitle>
            <Button onClick={() => setIsFormOpen(true)} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Add Activity
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[600px] pr-4">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            ) : activities.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium">No activities yet</p>
                <p className="text-sm mt-2">Start tracking deal activities and interactions</p>
                <Button onClick={() => setIsFormOpen(true)} variant="outline" className="mt-4">
                  Add First Activity
                </Button>
              </div>
            ) : (
              <div className="relative">
                {/* Timeline line */}
                <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />

                {/* Activities */}
                <div className="space-y-6">
                  {activities.map((activity, index) => (
                    <div key={activity.id} className="relative pl-10">
                      {/* Timeline dot */}
                      <div
                        className={cn(
                          'absolute left-0 top-1 w-8 h-8 rounded-full flex items-center justify-center',
                          activityTypeColors[activity.activity_type] || 'bg-gray-100 text-gray-700'
                        )}
                      >
                        {activityTypeIcons[activity.activity_type] || (
                          <MessageSquare className="h-4 w-4" />
                        )}
                      </div>

                      {/* Activity content */}
                      <div className="bg-card border rounded-lg p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-semibold text-sm">{activity.subject}</h4>
                              <Badge variant="outline" className="text-xs capitalize">
                                {activity.activity_type.replace('_', ' ')}
                              </Badge>
                            </div>

                            {activity.description && (
                              <p className="text-sm text-muted-foreground mt-2">
                                {activity.description}
                              </p>
                            )}

                            {activity.participants && activity.participants.length > 0 && (
                              <div className="flex items-center gap-2 mt-3">
                                <Users className="h-3.5 w-3.5 text-muted-foreground" />
                                <span className="text-xs text-muted-foreground">
                                  {activity.participants.join(', ')}
                                </span>
                              </div>
                            )}

                            {activity.outcome && (
                              <div className="mt-3 p-2 bg-muted rounded text-sm">
                                <span className="font-medium">Outcome: </span>
                                {activity.outcome}
                              </div>
                            )}

                            {activity.follow_up_required && activity.follow_up_date && (
                              <div className="flex items-center gap-2 mt-3 text-sm text-orange-600">
                                <Calendar className="h-3.5 w-3.5" />
                                <span>
                                  Follow-up: {format(new Date(activity.follow_up_date), 'MMM dd, yyyy')}
                                </span>
                              </div>
                            )}
                          </div>

                          <div className="text-right flex-shrink-0">
                            <time className="text-xs text-muted-foreground">
                              {formatActivityDate(activity.activity_date)}
                            </time>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Add Activity Dialog */}
      <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Add Activity</DialogTitle>
            <DialogDescription>
              Record a new activity or interaction for this deal
            </DialogDescription>
          </DialogHeader>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="activity_type"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Activity Type</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select type" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="meeting">Meeting</SelectItem>
                          <SelectItem value="call">Phone Call</SelectItem>
                          <SelectItem value="video_call">Video Call</SelectItem>
                          <SelectItem value="email">Email</SelectItem>
                          <SelectItem value="note">Note</SelectItem>
                          <SelectItem value="milestone">Milestone</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="subject"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Subject</FormLabel>
                      <FormControl>
                        <Input placeholder="Activity subject" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Detailed description of the activity..."
                        className="resize-none h-24"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="participants"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Participants (comma-separated)</FormLabel>
                    <FormControl>
                      <Input placeholder="John Doe, Jane Smith" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="outcome"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Outcome</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="What was the outcome or result?"
                        className="resize-none"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Separator />

              <div className="space-y-4">
                <FormField
                  control={form.control}
                  name="follow_up_required"
                  render={({ field }) => (
                    <FormItem className="flex items-center gap-2">
                      <FormControl>
                        <input
                          type="checkbox"
                          checked={field.value}
                          onChange={field.onChange}
                          className="h-4 w-4"
                        />
                      </FormControl>
                      <FormLabel className="!mt-0">Follow-up required</FormLabel>
                    </FormItem>
                  )}
                />

                {form.watch('follow_up_required') && (
                  <FormField
                    control={form.control}
                    name="follow_up_date"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Follow-up Date</FormLabel>
                        <FormControl>
                          <Input type="date" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                )}
              </div>

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsFormOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={submitting}>
                  {submitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Adding...
                    </>
                  ) : (
                    'Add Activity'
                  )}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </>
  )
}

export default DealTimeline
