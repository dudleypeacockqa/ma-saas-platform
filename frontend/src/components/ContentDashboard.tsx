import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  FileText,
  Podcast,
  Share2,
  Mail,
  PlusCircle,
  Sparkles,
  Eye,
  Edit,
  Trash2,
  Download,
  TrendingUp,
  CheckCircle2,
  Clock,
  AlertCircle
} from 'lucide-react';

interface Content {
  id: number;
  title: string;
  content_type: string;
  status: string;
  content_body: string;
  metadata?: any;
  created_at: string;
  updated_at: string;
}

interface PodcastEpisode {
  id: number;
  episode_number?: number;
  episode_title: string;
  guest_name?: string;
  guest_company?: string;
  transcript_text?: string;
  created_at: string;
}

export const ContentDashboard: React.FC = () => {
  const [contents, setContents] = useState<Content[]>([]);
  const [episodes, setEpisodes] = useState<PodcastEpisode[]>([]);
  const [selectedContent, setSelectedContent] = useState<Content | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('all');

  // Podcast Episode Form
  const [newEpisode, setNewEpisode] = useState({
    episode_title: '',
    episode_number: '',
    guest_name: '',
    guest_company: '',
    transcript_text: ''
  });

  // Content Generation Forms
  const [showNotesEpisodeId, setShowNotesEpisodeId] = useState('');
  const [socialMediaForm, setSocialMediaForm] = useState({
    source_content_id: '',
    platform: 'linkedin'
  });
  const [blogForm, setBlogForm] = useState({
    topic: '',
    source_content_id: '',
    seo_keywords: ''
  });

  useEffect(() => {
    fetchContents();
    fetchEpisodes();
  }, []);

  const fetchContents = async () => {
    try {
      const response = await fetch('/api/content/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setContents(data);
      }
    } catch (error) {
      console.error('Error fetching contents:', error);
    }
  };

  const fetchEpisodes = async () => {
    try {
      const response = await fetch('/api/content/podcast-episodes', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setEpisodes(data);
      }
    } catch (error) {
      console.error('Error fetching episodes:', error);
    }
  };

  const createPodcastEpisode = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/content/podcast-episodes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          ...newEpisode,
          episode_number: newEpisode.episode_number ? parseInt(newEpisode.episode_number) : null
        })
      });
      if (response.ok) {
        await fetchEpisodes();
        setNewEpisode({
          episode_title: '',
          episode_number: '',
          guest_name: '',
          guest_company: '',
          transcript_text: ''
        });
      }
    } catch (error) {
      console.error('Error creating episode:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateShowNotes = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/content/generate/show-notes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ episode_id: parseInt(showNotesEpisodeId) })
      });
      if (response.ok) {
        await fetchContents();
        setShowNotesEpisodeId('');
      }
    } catch (error) {
      console.error('Error generating show notes:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateSocialMedia = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/content/generate/social-media', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          source_content_id: parseInt(socialMediaForm.source_content_id),
          platform: socialMediaForm.platform
        })
      });
      if (response.ok) {
        await fetchContents();
        setSocialMediaForm({ source_content_id: '', platform: 'linkedin' });
      }
    } catch (error) {
      console.error('Error generating social media content:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateBlogArticle = async () => {
    setLoading(true);
    try {
      const keywords = blogForm.seo_keywords ? blogForm.seo_keywords.split(',').map(k => k.trim()) : null;
      const response = await fetch('/api/content/generate/blog-article', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          topic: blogForm.topic,
          source_content_id: blogForm.source_content_id ? parseInt(blogForm.source_content_id) : null,
          seo_keywords: keywords
        })
      });
      if (response.ok) {
        await fetchContents();
        setBlogForm({ topic: '', source_content_id: '', seo_keywords: '' });
      }
    } catch (error) {
      console.error('Error generating blog article:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      draft: { color: 'bg-gray-500', icon: Edit },
      pending_review: { color: 'bg-yellow-500', icon: Clock },
      approved: { color: 'bg-green-500', icon: CheckCircle2 },
      published: { color: 'bg-blue-500', icon: TrendingUp },
      archived: { color: 'bg-gray-400', icon: AlertCircle }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft;
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} text-white`}>
        <Icon className="w-3 h-3 mr-1" />
        {status.replace('_', ' ').toUpperCase()}
      </Badge>
    );
  };

  const getContentTypeIcon = (type: string) => {
    const icons = {
      podcast_show_notes: Podcast,
      linkedin_post: Share2,
      twitter_thread: Share2,
      youtube_description: Share2,
      instagram_caption: Share2,
      blog_article: FileText,
      email_newsletter: Mail
    };
    return icons[type as keyof typeof icons] || FileText;
  };

  const filteredContents = activeTab === 'all'
    ? contents
    : contents.filter(c => c.content_type === activeTab);

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Content Creation Dashboard</h1>
          <p className="text-muted-foreground">AI-powered content generation for M&A insights</p>
        </div>
        <div className="flex gap-2">
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <PlusCircle className="w-4 h-4 mr-2" />
                New Episode
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create Podcast Episode</DialogTitle>
                <DialogDescription>Add a new podcast episode to generate content from</DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="episode_title">Episode Title</Label>
                  <Input
                    id="episode_title"
                    value={newEpisode.episode_title}
                    onChange={(e) => setNewEpisode({...newEpisode, episode_title: e.target.value})}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="episode_number">Episode Number</Label>
                    <Input
                      id="episode_number"
                      type="number"
                      value={newEpisode.episode_number}
                      onChange={(e) => setNewEpisode({...newEpisode, episode_number: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label htmlFor="guest_name">Guest Name</Label>
                    <Input
                      id="guest_name"
                      value={newEpisode.guest_name}
                      onChange={(e) => setNewEpisode({...newEpisode, guest_name: e.target.value})}
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="guest_company">Guest Company</Label>
                  <Input
                    id="guest_company"
                    value={newEpisode.guest_company}
                    onChange={(e) => setNewEpisode({...newEpisode, guest_company: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="transcript">Transcript</Label>
                  <Textarea
                    id="transcript"
                    rows={10}
                    value={newEpisode.transcript_text}
                    onChange={(e) => setNewEpisode({...newEpisode, transcript_text: e.target.value})}
                    placeholder="Paste the episode transcript here..."
                  />
                </div>
                <Button onClick={createPodcastEpisode} disabled={loading} className="w-full">
                  Create Episode
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* AI Content Generation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Sparkles className="w-5 h-5 mr-2 text-purple-500" />
              Generate Show Notes
            </CardTitle>
            <CardDescription>AI-powered podcast show notes</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Select value={showNotesEpisodeId} onValueChange={setShowNotesEpisodeId}>
              <SelectTrigger>
                <SelectValue placeholder="Select episode" />
              </SelectTrigger>
              <SelectContent>
                {episodes.map(ep => (
                  <SelectItem key={ep.id} value={ep.id.toString()}>
                    {ep.episode_number ? `Ep ${ep.episode_number}: ` : ''}{ep.episode_title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={generateShowNotes} disabled={!showNotesEpisodeId || loading} className="w-full">
              Generate
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Share2 className="w-5 h-5 mr-2 text-blue-500" />
              Social Media Posts
            </CardTitle>
            <CardDescription>Create platform-specific content</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Select value={socialMediaForm.source_content_id} onValueChange={(val) => setSocialMediaForm({...socialMediaForm, source_content_id: val})}>
              <SelectTrigger>
                <SelectValue placeholder="Select source content" />
              </SelectTrigger>
              <SelectContent>
                {contents.map(c => (
                  <SelectItem key={c.id} value={c.id.toString()}>
                    {c.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={socialMediaForm.platform} onValueChange={(val) => setSocialMediaForm({...socialMediaForm, platform: val})}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="linkedin">LinkedIn</SelectItem>
                <SelectItem value="twitter">Twitter/X</SelectItem>
                <SelectItem value="youtube">YouTube</SelectItem>
                <SelectItem value="instagram">Instagram</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={generateSocialMedia} disabled={!socialMediaForm.source_content_id || loading} className="w-full">
              Generate
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="w-5 h-5 mr-2 text-green-500" />
              Blog Article
            </CardTitle>
            <CardDescription>Long-form SEO-optimized articles</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="Article topic..."
              value={blogForm.topic}
              onChange={(e) => setBlogForm({...blogForm, topic: e.target.value})}
            />
            <Input
              placeholder="SEO keywords (comma-separated)"
              value={blogForm.seo_keywords}
              onChange={(e) => setBlogForm({...blogForm, seo_keywords: e.target.value})}
            />
            <Button onClick={generateBlogArticle} disabled={!blogForm.topic || loading} className="w-full">
              Generate
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Content List */}
      <Card>
        <CardHeader>
          <CardTitle>Content Library</CardTitle>
          <CardDescription>Manage all your generated content</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="all">All Content</TabsTrigger>
              <TabsTrigger value="podcast_show_notes">Show Notes</TabsTrigger>
              <TabsTrigger value="blog_article">Blog Articles</TabsTrigger>
              <TabsTrigger value="linkedin_post">Social Media</TabsTrigger>
            </TabsList>

            <TabsContent value={activeTab} className="space-y-4">
              {filteredContents.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No content yet. Start by creating a podcast episode!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredContents.map(content => {
                    const Icon = getContentTypeIcon(content.content_type);
                    return (
                      <div key={content.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-3 flex-1">
                            <Icon className="w-5 h-5 mt-1 text-muted-foreground" />
                            <div className="flex-1">
                              <h3 className="font-semibold">{content.title}</h3>
                              <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                                {content.content_body.substring(0, 150)}...
                              </p>
                              <div className="flex items-center gap-2 mt-2">
                                {getStatusBadge(content.status)}
                                <span className="text-xs text-muted-foreground">
                                  {new Date(content.created_at).toLocaleDateString()}
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <Button variant="ghost" size="sm" onClick={() => setSelectedContent(content)}>
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Download className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Content Preview Dialog */}
      <Dialog open={!!selectedContent} onOpenChange={() => setSelectedContent(null)}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{selectedContent?.title}</DialogTitle>
            <DialogDescription>
              {selectedContent?.content_type.replace(/_/g, ' ').toUpperCase()}
            </DialogDescription>
          </DialogHeader>
          <div className="prose max-w-none">
            <pre className="whitespace-pre-wrap text-sm">{selectedContent?.content_body}</pre>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ContentDashboard;
