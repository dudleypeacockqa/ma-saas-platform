import React, { useState, useEffect, useRef } from 'react'
import { useUser, useOrganization } from '@clerk/clerk-react'
import {
  MessageSquare,
  Video,
  FileText,
  Calendar,
  Users,
  Bell,
  Search,
  Send,
  Phone,
  MoreHorizontal,
  Pin,
  Edit,
  Trash2,
  Download,
  Share,
  Settings,
  Plus,
  Filter,
  Hash,
  Lock,
  Globe,
  Paperclip,
  Smile,
  Mic,
  Camera,
  Screen,
  Clock,
  CheckCircle,
  Star,
  BookOpen,
  Archive,
  PlusCircle,
  Minus,
  X
} from 'lucide-react'

import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Input } from './ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './ui/dropdown-menu'
import { ScrollArea } from './ui/scroll-area'
import { Separator } from './ui/separator'
import { Textarea } from './ui/textarea'
import { Switch } from './ui/switch'
import { Label } from './ui/label'

// Types
interface Channel {
  id: string
  team_id: string
  name: string
  description?: string
  channel_type: 'general' | 'announcements' | 'project' | 'random' | 'private'
  is_private: boolean
  member_count: number
  message_count: number
  unread_count: number
  last_message?: Message
  created_at: string
}

interface Message {
  id: string
  channel_id: string
  sender_id: string
  sender_name: string
  sender_avatar?: string
  content: string
  message_type: 'text' | 'image' | 'file' | 'system'
  reply_to_id?: string
  attachments?: Array<{
    id: string
    name: string
    url: string
    type: string
    size: number
  }>
  reactions?: Array<{
    emoji: string
    users: string[]
    count: number
  }>
  created_at: string
  updated_at?: string
  is_pinned?: boolean
}

interface Meeting {
  id: string
  team_id: string
  title: string
  description?: string
  meeting_type: 'standup' | 'planning' | 'review' | 'sync' | 'presentation'
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled'
  scheduled_start: string
  scheduled_end: string
  actual_start?: string
  actual_end?: string
  meeting_url?: string
  attendees: Array<{
    user_id: string
    name: string
    avatar?: string
    status: 'accepted' | 'declined' | 'tentative' | 'no_response'
  }>
  agenda?: Array<{
    item: string
    duration: number
    presenter?: string
  }>
  recording_url?: string
  notes?: string
}

interface Document {
  id: string
  name: string
  description?: string
  type: 'document' | 'spreadsheet' | 'presentation' | 'pdf' | 'image'
  url: string
  shared_with: string[]
  permissions: Record<string, 'view' | 'comment' | 'edit' | 'admin'>
  version: number
  size: number
  last_modified: string
  modified_by: string
  is_collaborative: boolean
  active_collaborators: number
}

interface Notification {
  id: string
  type: 'message' | 'meeting' | 'document' | 'task' | 'mention'
  title: string
  message: string
  from_user?: string
  team_id?: string
  channel_id?: string
  related_id?: string
  is_read: boolean
  created_at: string
}

const CollaborationHub: React.FC = () => {
  const { user, isLoaded: userLoaded } = useUser()
  const { organization, isLoaded: orgLoaded } = useOrganization()

  // State
  const [channels, setChannels] = useState<Channel[]>([])
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [meetings, setMeetings] = useState<Meeting[]>([])
  const [documents, setDocuments] = useState<Document[]>([])
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newMessage, setNewMessage] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('chat')
  const [showNotifications, setShowNotifications] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Mock data for development
  useEffect(() => {
    if (userLoaded && orgLoaded) {
      // Mock channels
      const mockChannels: Channel[] = [
        {
          id: '1',
          team_id: 'team-1',
          name: 'general',
          description: 'General team discussion',
          channel_type: 'general',
          is_private: false,
          member_count: 8,
          message_count: 142,
          unread_count: 3,
          created_at: '2024-01-01T00:00:00Z'
        },
        {
          id: '2',
          team_id: 'team-1',
          name: 'techcorp-dd',
          description: 'TechCorp due diligence discussion',
          channel_type: 'project',
          is_private: false,
          member_count: 5,
          message_count: 89,
          unread_count: 1,
          created_at: '2024-01-15T00:00:00Z'
        },
        {
          id: '3',
          team_id: 'team-1',
          name: 'announcements',
          description: 'Important team announcements',
          channel_type: 'announcements',
          is_private: false,
          member_count: 8,
          message_count: 12,
          unread_count: 0,
          created_at: '2024-01-01T00:00:00Z'
        },
        {
          id: '4',
          team_id: 'team-1',
          name: 'leadership',
          description: 'Leadership team private channel',
          channel_type: 'private',
          is_private: true,
          member_count: 3,
          message_count: 45,
          unread_count: 2,
          created_at: '2024-02-01T00:00:00Z'
        }
      ]

      // Mock messages
      const mockMessages: Message[] = [
        {
          id: '1',
          channel_id: '1',
          sender_id: 'user-1',
          sender_name: 'Alice Johnson',
          content: 'Good morning team! Ready for today\'s financial analysis review?',
          message_type: 'text',
          created_at: '2024-07-15T09:00:00Z'
        },
        {
          id: '2',
          channel_id: '1',
          sender_id: 'user-2',
          sender_name: 'Bob Smith',
          content: 'Yes, I\'ve prepared the latest cash flow projections. Will share them in the meeting.',
          message_type: 'text',
          created_at: '2024-07-15T09:05:00Z'
        },
        {
          id: '3',
          channel_id: '1',
          sender_id: 'user-3',
          sender_name: 'Carol Davis',
          content: 'I\'ve uploaded the updated financial model to the shared drive. Please review before the meeting.',
          message_type: 'text',
          attachments: [
            {
              id: 'att-1',
              name: 'Financial_Model_v3.xlsx',
              url: '/files/financial-model.xlsx',
              type: 'spreadsheet',
              size: 2048000
            }
          ],
          created_at: '2024-07-15T09:10:00Z',
          is_pinned: true
        },
        {
          id: '4',
          channel_id: '1',
          sender_id: 'user-1',
          sender_name: 'Alice Johnson',
          content: 'Thanks Carol! The model looks great. I notice we\'re ahead of schedule on the valuation work.',
          message_type: 'text',
          reactions: [
            { emoji: '👍', users: ['user-2', 'user-3'], count: 2 },
            { emoji: '🎉', users: ['user-2'], count: 1 }
          ],
          created_at: '2024-07-15T09:15:00Z'
        }
      ]

      // Mock meetings
      const mockMeetings: Meeting[] = [
        {
          id: '1',
          team_id: 'team-1',
          title: 'Daily Standup',
          description: 'Daily team sync and progress updates',
          meeting_type: 'standup',
          status: 'scheduled',
          scheduled_start: '2024-07-15T14:00:00Z',
          scheduled_end: '2024-07-15T14:30:00Z',
          meeting_url: 'https://meet.example.com/daily-standup',
          attendees: [
            { user_id: 'user-1', name: 'Alice Johnson', status: 'accepted' },
            { user_id: 'user-2', name: 'Bob Smith', status: 'accepted' },
            { user_id: 'user-3', name: 'Carol Davis', status: 'tentative' }
          ]
        },
        {
          id: '2',
          team_id: 'team-1',
          title: 'Financial Review Meeting',
          description: 'Review financial analysis and projections',
          meeting_type: 'review',
          status: 'completed',
          scheduled_start: '2024-07-14T15:00:00Z',
          scheduled_end: '2024-07-14T16:00:00Z',
          actual_start: '2024-07-14T15:05:00Z',
          actual_end: '2024-07-14T16:10:00Z',
          recording_url: 'https://recordings.example.com/financial-review',
          attendees: [
            { user_id: 'user-1', name: 'Alice Johnson', status: 'accepted' },
            { user_id: 'user-2', name: 'Bob Smith', status: 'accepted' },
            { user_id: 'user-4', name: 'David Wilson', status: 'accepted' }
          ],
          notes: 'Discussed Q3 projections and identified areas for improvement.'
        }
      ]

      // Mock documents
      const mockDocuments: Document[] = [
        {
          id: '1',
          name: 'TechCorp Due Diligence Report',
          description: 'Comprehensive due diligence analysis',
          type: 'document',
          url: '/documents/techcorp-dd-report.docx',
          shared_with: ['user-1', 'user-2', 'user-3'],
          permissions: {
            'user-1': 'admin',
            'user-2': 'edit',
            'user-3': 'edit'
          },
          version: 3,
          size: 5242880,
          last_modified: '2024-07-15T08:30:00Z',
          modified_by: 'user-2',
          is_collaborative: true,
          active_collaborators: 2
        },
        {
          id: '2',
          name: 'Financial Model Q3',
          description: 'Updated financial projections and analysis',
          type: 'spreadsheet',
          url: '/documents/financial-model-q3.xlsx',
          shared_with: ['user-1', 'user-2', 'user-3', 'user-4'],
          permissions: {
            'user-1': 'admin',
            'user-2': 'edit',
            'user-3': 'edit',
            'user-4': 'view'
          },
          version: 5,
          size: 2048000,
          last_modified: '2024-07-15T09:10:00Z',
          modified_by: 'user-3',
          is_collaborative: true,
          active_collaborators: 1
        }
      ]

      // Mock notifications
      const mockNotifications: Notification[] = [
        {
          id: '1',
          type: 'message',
          title: 'New message in #techcorp-dd',
          message: 'Carol Davis shared a document',
          from_user: 'user-3',
          team_id: 'team-1',
          channel_id: '2',
          is_read: false,
          created_at: '2024-07-15T09:10:00Z'
        },
        {
          id: '2',
          type: 'meeting',
          title: 'Meeting starting soon',
          message: 'Daily Standup starts in 15 minutes',
          team_id: 'team-1',
          related_id: '1',
          is_read: false,
          created_at: '2024-07-15T13:45:00Z'
        },
        {
          id: '3',
          type: 'document',
          title: 'Document updated',
          message: 'TechCorp Due Diligence Report was updated',
          from_user: 'user-2',
          related_id: '1',
          is_read: true,
          created_at: '2024-07-15T08:30:00Z'
        }
      ]

      setChannels(mockChannels)
      setSelectedChannel(mockChannels[0])
      setMessages(mockMessages)
      setMeetings(mockMeetings)
      setDocuments(mockDocuments)
      setNotifications(mockNotifications)
      setLoading(false)
    }
  }, [userLoaded, orgLoaded])

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Send message
  const sendMessage = () => {
    if (!newMessage.trim() || !selectedChannel) return

    const message: Message = {
      id: Date.now().toString(),
      channel_id: selectedChannel.id,
      sender_id: user?.id || 'current-user',
      sender_name: user?.fullName || 'You',
      content: newMessage,
      message_type: 'text',
      created_at: new Date().toISOString()
    }

    setMessages(prev => [...prev, message])
    setNewMessage('')
  }

  // Handle key press in message input
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // Filter channels by search term
  const filteredChannels = channels.filter(channel =>
    channel.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // Get channel messages
  const channelMessages = messages.filter(msg => msg.channel_id === selectedChannel?.id)

  // Get unread notifications count
  const unreadNotificationsCount = notifications.filter(n => !n.is_read).length

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // Format time
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } else if (days === 1) {
      return 'Yesterday'
    } else {
      return date.toLocaleDateString()
    }
  }

  if (!userLoaded || !orgLoaded) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading collaboration hub...</div>
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-white border-b">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Collaboration Hub</h1>
          <p className="text-gray-600">Team communication and coordination</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowNotifications(!showNotifications)}
            >
              <Bell className="h-4 w-4" />
              {unreadNotificationsCount > 0 && (
                <Badge className="absolute -top-2 -right-2 h-5 w-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center">
                  {unreadNotificationsCount}
                </Badge>
              )}
            </Button>
            {showNotifications && (
              <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-lg shadow-lg border z-50">
                <div className="p-4 border-b">
                  <h3 className="font-medium text-gray-900">Notifications</h3>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`p-3 border-b hover:bg-gray-50 ${
                        !notification.is_read ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900">
                            {notification.title}
                          </p>
                          <p className="text-sm text-gray-500">{notification.message}</p>
                          <p className="text-xs text-gray-400 mt-1">
                            {formatTime(notification.created_at)}
                          </p>
                        </div>
                        {!notification.is_read && (
                          <div className="w-2 h-2 bg-blue-500 rounded-full mt-1"></div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
          <TabsList className="grid w-full grid-cols-4 m-4">
            <TabsTrigger value="chat">Chat</TabsTrigger>
            <TabsTrigger value="meetings">Meetings</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="activity">Activity</TabsTrigger>
          </TabsList>

          {/* Chat Tab */}
          <TabsContent value="chat" className="flex-1 flex m-0">
            <div className="flex-1 flex">
              {/* Channels Sidebar */}
              <div className="w-64 bg-gray-50 border-r flex flex-col">
                <div className="p-4 border-b">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search channels..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <div className="flex-1 overflow-y-auto">
                  <div className="p-2">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-sm font-medium text-gray-700">Channels</h3>
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <Plus className="h-4 w-4" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Create Channel</DialogTitle>
                            <DialogDescription>
                              Create a new channel for team communication.
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div>
                              <Label>Channel Name</Label>
                              <Input placeholder="e.g., project-alpha" />
                            </div>
                            <div>
                              <Label>Description</Label>
                              <Textarea placeholder="What's this channel about?" />
                            </div>
                            <div className="flex items-center space-x-2">
                              <Switch id="private" />
                              <Label htmlFor="private">Private channel</Label>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                    <div className="space-y-1">
                      {filteredChannels.map((channel) => (
                        <div
                          key={channel.id}
                          className={`flex items-center justify-between p-2 rounded cursor-pointer transition-colors ${
                            selectedChannel?.id === channel.id
                              ? 'bg-blue-100 text-blue-900'
                              : 'hover:bg-gray-100'
                          }`}
                          onClick={() => setSelectedChannel(channel)}
                        >
                          <div className="flex items-center space-x-2">
                            {channel.is_private ? (
                              <Lock className="h-4 w-4 text-gray-400" />
                            ) : (
                              <Hash className="h-4 w-4 text-gray-400" />
                            )}
                            <span className="text-sm font-medium">{channel.name}</span>
                          </div>
                          {channel.unread_count > 0 && (
                            <Badge className="bg-red-500 text-white text-xs">
                              {channel.unread_count}
                            </Badge>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Chat Area */}
              <div className="flex-1 flex flex-col">
                {selectedChannel ? (
                  <>
                    {/* Chat Header */}
                    <div className="p-4 border-b bg-white">
                      <div className="flex items-center justify-between">
                        <div>
                          <h2 className="text-lg font-medium text-gray-900 flex items-center">
                            {selectedChannel.is_private ? (
                              <Lock className="h-5 w-5 mr-2 text-gray-400" />
                            ) : (
                              <Hash className="h-5 w-5 mr-2 text-gray-400" />
                            )}
                            {selectedChannel.name}
                          </h2>
                          <p className="text-sm text-gray-500">
                            {selectedChannel.description} • {selectedChannel.member_count} members
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button variant="outline" size="sm">
                            <Video className="h-4 w-4 mr-2" />
                            Call
                          </Button>
                          <Button variant="outline" size="sm">
                            <Users className="h-4 w-4 mr-2" />
                            Members
                          </Button>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent>
                              <DropdownMenuItem>
                                <Settings className="h-4 w-4 mr-2" />
                                Channel Settings
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Pin className="h-4 w-4 mr-2" />
                                Pinned Messages
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Archive className="h-4 w-4 mr-2" />
                                View Files
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>
                      </div>
                    </div>

                    {/* Messages */}
                    <ScrollArea className="flex-1 p-4">
                      <div className="space-y-4">
                        {channelMessages.map((message) => (
                          <div key={message.id} className="group">
                            <div className="flex items-start space-x-3">
                              <Avatar className="h-8 w-8">
                                <AvatarImage src={message.sender_avatar} />
                                <AvatarFallback>
                                  {message.sender_name.split(' ').map(n => n[0]).join('')}
                                </AvatarFallback>
                              </Avatar>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center space-x-2">
                                  <span className="text-sm font-medium text-gray-900">
                                    {message.sender_name}
                                  </span>
                                  <span className="text-xs text-gray-500">
                                    {formatTime(message.created_at)}
                                  </span>
                                  {message.is_pinned && (
                                    <Pin className="h-3 w-3 text-blue-500" />
                                  )}
                                </div>
                                <div className="mt-1">
                                  <p className="text-sm text-gray-900">{message.content}</p>

                                  {/* Attachments */}
                                  {message.attachments && message.attachments.length > 0 && (
                                    <div className="mt-2 space-y-2">
                                      {message.attachments.map((attachment) => (
                                        <div
                                          key={attachment.id}
                                          className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg border"
                                        >
                                          <FileText className="h-6 w-6 text-blue-500" />
                                          <div className="flex-1">
                                            <p className="text-sm font-medium text-gray-900">
                                              {attachment.name}
                                            </p>
                                            <p className="text-xs text-gray-500">
                                              {formatFileSize(attachment.size)}
                                            </p>
                                          </div>
                                          <Button variant="outline" size="sm">
                                            <Download className="h-4 w-4" />
                                          </Button>
                                        </div>
                                      ))}
                                    </div>
                                  )}

                                  {/* Reactions */}
                                  {message.reactions && message.reactions.length > 0 && (
                                    <div className="flex items-center space-x-2 mt-2">
                                      {message.reactions.map((reaction, index) => (
                                        <button
                                          key={index}
                                          className="flex items-center space-x-1 px-2 py-1 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
                                        >
                                          <span>{reaction.emoji}</span>
                                          <span className="text-xs text-gray-600">{reaction.count}</span>
                                        </button>
                                      ))}
                                    </div>
                                  )}
                                </div>
                              </div>
                              <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                                <DropdownMenu>
                                  <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" size="sm">
                                      <MoreHorizontal className="h-4 w-4" />
                                    </Button>
                                  </DropdownMenuTrigger>
                                  <DropdownMenuContent>
                                    <DropdownMenuItem>
                                      <Smile className="h-4 w-4 mr-2" />
                                      Add Reaction
                                    </DropdownMenuItem>
                                    <DropdownMenuItem>
                                      <Pin className="h-4 w-4 mr-2" />
                                      Pin Message
                                    </DropdownMenuItem>
                                    <DropdownMenuItem>
                                      <Edit className="h-4 w-4 mr-2" />
                                      Edit
                                    </DropdownMenuItem>
                                    <DropdownMenuItem className="text-red-600">
                                      <Trash2 className="h-4 w-4 mr-2" />
                                      Delete
                                    </DropdownMenuItem>
                                  </DropdownMenuContent>
                                </DropdownMenu>
                              </div>
                            </div>
                          </div>
                        ))}
                        <div ref={messagesEndRef} />
                      </div>
                    </ScrollArea>

                    {/* Message Input */}
                    <div className="p-4 border-t bg-white">
                      <div className="flex items-center space-x-2">
                        <div className="flex-1 relative">
                          <Textarea
                            placeholder={`Message #${selectedChannel.name}`}
                            value={newMessage}
                            onChange={(e) => setNewMessage(e.target.value)}
                            onKeyPress={handleKeyPress}
                            className="min-h-[40px] max-h-32 resize-none pr-20"
                          />
                          <div className="absolute right-2 bottom-2 flex items-center space-x-1">
                            <Button variant="ghost" size="sm">
                              <Paperclip className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Smile className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                        <Button
                          onClick={sendMessage}
                          disabled={!newMessage.trim()}
                          size="sm"
                        >
                          <Send className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex items-center justify-center">
                    <div className="text-center">
                      <MessageSquare className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                      <p className="text-lg font-medium text-gray-900">Select a Channel</p>
                      <p className="text-gray-500">Choose a channel to start messaging</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </TabsContent>

          {/* Meetings Tab */}
          <TabsContent value="meetings" className="flex-1 p-4">
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium text-gray-900">Meetings</h2>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Schedule Meeting
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {meetings.map((meeting) => (
                  <Card key={meeting.id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="text-lg">{meeting.title}</CardTitle>
                          <CardDescription>{meeting.description}</CardDescription>
                        </div>
                        <Badge
                          className={
                            meeting.status === 'scheduled'
                              ? 'bg-blue-100 text-blue-800'
                              : meeting.status === 'in_progress'
                              ? 'bg-green-100 text-green-800'
                              : meeting.status === 'completed'
                              ? 'bg-gray-100 text-gray-800'
                              : 'bg-red-100 text-red-800'
                          }
                        >
                          {meeting.status.replace('_', ' ')}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Calendar className="h-4 w-4" />
                          <span>
                            {new Date(meeting.scheduled_start).toLocaleDateString()} •{' '}
                            {new Date(meeting.scheduled_start).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit'
                            })} -{' '}
                            {new Date(meeting.scheduled_end).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Users className="h-4 w-4" />
                          <span>{meeting.attendees.length} attendees</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          {meeting.status === 'scheduled' && (
                            <>
                              <Button size="sm">
                                <Video className="h-4 w-4 mr-2" />
                                Join
                              </Button>
                              <Button variant="outline" size="sm">
                                <Edit className="h-4 w-4 mr-2" />
                                Edit
                              </Button>
                            </>
                          )}
                          {meeting.status === 'completed' && meeting.recording_url && (
                            <Button variant="outline" size="sm">
                              <Video className="h-4 w-4 mr-2" />
                              View Recording
                            </Button>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </TabsContent>

          {/* Documents Tab */}
          <TabsContent value="documents" className="flex-1 p-4">
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium text-gray-900">Shared Documents</h2>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Upload Document
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {documents.map((document) => (
                  <Card key={document.id}>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-3">
                          <FileText className="h-8 w-8 text-blue-500" />
                          <div>
                            <CardTitle className="text-base">{document.name}</CardTitle>
                            <CardDescription>{document.description}</CardDescription>
                          </div>
                        </div>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent>
                            <DropdownMenuItem>
                              <Edit className="h-4 w-4 mr-2" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Share className="h-4 w-4 mr-2" />
                              Share
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Download className="h-4 w-4 mr-2" />
                              Download
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-500">Version</span>
                          <span className="text-gray-900">v{document.version}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-500">Size</span>
                          <span className="text-gray-900">{formatFileSize(document.size)}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-500">Modified</span>
                          <span className="text-gray-900">{formatTime(document.last_modified)}</span>
                        </div>
                        {document.is_collaborative && (
                          <div className="flex items-center space-x-2 text-sm">
                            <Users className="h-4 w-4 text-green-500" />
                            <span className="text-green-600">
                              {document.active_collaborators} active
                            </span>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </TabsContent>

          {/* Activity Tab */}
          <TabsContent value="activity" className="flex-1 p-4">
            <div className="space-y-6">
              <h2 className="text-lg font-medium text-gray-900">Team Activity</h2>

              <div className="space-y-4">
                {/* Activity items would be rendered here */}
                <div className="flex items-center space-x-4 p-4 border rounded-lg">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback>CD</AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">
                      <span className="font-medium">Carol Davis</span> updated{' '}
                      <span className="font-medium">Financial Model Q3</span>
                    </p>
                    <p className="text-xs text-gray-500">2 hours ago</p>
                  </div>
                </div>

                <div className="flex items-center space-x-4 p-4 border rounded-lg">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback>BS</AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">
                      <span className="font-medium">Bob Smith</span> completed{' '}
                      <span className="font-medium">Cash Flow Analysis</span> task
                    </p>
                    <p className="text-xs text-gray-500">4 hours ago</p>
                  </div>
                </div>

                <div className="flex items-center space-x-4 p-4 border rounded-lg">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback>AJ</AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">
                      <span className="font-medium">Alice Johnson</span> scheduled{' '}
                      <span className="font-medium">Financial Review Meeting</span>
                    </p>
                    <p className="text-xs text-gray-500">Yesterday</p>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default CollaborationHub