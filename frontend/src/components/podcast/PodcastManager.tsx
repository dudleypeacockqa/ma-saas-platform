import React, { useState, useEffect } from 'react';
import {
  PlayCircle,
  Upload,
  Download,
  Share2,
  Edit3,
  Trash2,
  Eye,
  Clock,
  TrendingUp,
  Users,
  MessageCircle,
  Star,
  Calendar,
  BarChart3,
  Headphones,
  Mic,
  Video,
  FileText,
  Globe,
  Zap,
  Target,
  Mail,
} from 'lucide-react';
import { useUser } from '@clerk/clerk-react';
import { toast } from 'sonner';

interface PodcastEpisode {
  id: string;
  title: string;
  description: string;
  duration: string;
  publishDate: string;
  status: 'draft' | 'processing' | 'published' | 'scheduled';
  thumbnail: string;
  audioUrl?: string;
  videoUrl?: string;
  downloadCount: number;
  viewCount: number;
  engagementRate: number;
  platforms: PlatformStatus[];
  aiGenerated: {
    transcript: boolean;
    showNotes: boolean;
    socialClips: boolean;
    blogPost: boolean;
    newsletter: boolean;
  };
}

interface PlatformStatus {
  platform: string;
  status: 'published' | 'pending' | 'failed';
  url?: string;
  metrics?: {
    plays: number;
    likes: number;
    comments: number;
  };
}

const PodcastManager: React.FC = () => {
  const { user } = useUser();
  const [episodes, setEpisodes] = useState<PodcastEpisode[]>([]);
  const [selectedEpisode, setSelectedEpisode] = useState<PodcastEpisode | null>(null);
  const [activeTab, setActiveTab] = useState<'episodes' | 'analytics' | 'distribution' | 'automation'>('episodes');
  const [loading, setLoading] = useState(true);

  // Mock data for demonstration
  useEffect(() => {
    setTimeout(() => {
      setEpisodes([
        {
          id: '1',
          title: 'M&A Valuation Masterclass: How to Value Any Business',
          description: 'Deep dive into professional M&A valuation techniques used by investment banks.',
          duration: '45:32',
          publishDate: '2025-10-12',
          status: 'published',
          thumbnail: '/podcast-thumbnails/valuation-masterclass.jpg',
          downloadCount: 2847,
          viewCount: 5234,
          engagementRate: 8.7,
          platforms: [
            { platform: 'Apple Podcasts', status: 'published', url: '#', metrics: { plays: 1200, likes: 89, comments: 23 } },
            { platform: 'Spotify', status: 'published', url: '#', metrics: { plays: 980, likes: 67, comments: 15 } },
            { platform: 'YouTube', status: 'published', url: '#', metrics: { plays: 3054, likes: 245, comments: 78 } },
            { platform: 'LinkedIn', status: 'published', url: '#', metrics: { plays: 567, likes: 123, comments: 34 } },
          ],
          aiGenerated: {
            transcript: true,
            showNotes: true,
            socialClips: true,
            blogPost: true,
            newsletter: true,
          },
        },
        {
          id: '2',
          title: 'Private Equity Trends 2025: What Dealmakers Need to Know',
          description: 'Industry expert interview covering the latest PE trends and opportunities.',
          duration: '38:15',
          publishDate: '2025-10-10',
          status: 'published',
          thumbnail: '/podcast-thumbnails/pe-trends.jpg',
          downloadCount: 1923,
          viewCount: 3456,
          engagementRate: 9.2,
          platforms: [
            { platform: 'Apple Podcasts', status: 'published', url: '#' },
            { platform: 'Spotify', status: 'published', url: '#' },
            { platform: 'YouTube', status: 'processing', url: '#' },
            { platform: 'LinkedIn', status: 'published', url: '#' },
          ],
          aiGenerated: {
            transcript: true,
            showNotes: true,
            socialClips: false,
            blogPost: true,
            newsletter: false,
          },
        },
        {
          id: '3',
          title: 'Due Diligence Deep Dive: Red Flags Every Buyer Must Know',
          description: 'Essential due diligence checklist and common red flags in M&A transactions.',
          duration: '52:18',
          publishDate: '2025-10-08',
          status: 'processing',
          thumbnail: '/podcast-thumbnails/due-diligence.jpg',
          downloadCount: 0,
          viewCount: 0,
          engagementRate: 0,
          platforms: [
            { platform: 'Apple Podcasts', status: 'pending' },
            { platform: 'Spotify', status: 'pending' },
            { platform: 'YouTube', status: 'pending' },
            { platform: 'LinkedIn', status: 'pending' },
          ],
          aiGenerated: {
            transcript: false,
            showNotes: false,
            socialClips: false,
            blogPost: false,
            newsletter: false,
          },
        },
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const totalDownloads = episodes.reduce((sum, ep) => sum + ep.downloadCount, 0);
  const totalViews = episodes.reduce((sum, ep) => sum + ep.viewCount, 0);
  const avgEngagement = episodes.length > 0 ? episodes.reduce((sum, ep) => sum + ep.engagementRate, 0) / episodes.length : 0;

  const generateAIContent = (episodeId: string, contentType: string) => {
    toast.success(`Generating ${contentType} with AI...`);

    // Simulate AI processing
    setTimeout(() => {
      setEpisodes(prev => prev.map(ep => {
        if (ep.id === episodeId) {
          return {
            ...ep,
            aiGenerated: {
              ...ep.aiGenerated,
              [contentType]: true,
            },
          };
        }
        return ep;
      }));
      toast.success(`✨ ${contentType} generated successfully!`);
    }, 2000 + Math.random() * 2000);
  };

  const distributeToplatform = (episodeId: string, platform: string) => {
    toast.info(`Publishing to ${platform}...`);

    // Simulate distribution
    setTimeout(() => {
      setEpisodes(prev => prev.map(ep => {
        if (ep.id === episodeId) {
          return {
            ...ep,
            platforms: ep.platforms.map(p =>
              p.platform === platform ? { ...p, status: 'published' as const } : p
            ),
          };
        }
        return ep;
      }));
      toast.success(`🚀 Published to ${platform}!`);
    }, 1500 + Math.random() * 1500);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center text-white">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-400 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold mb-2">Loading Podcast Empire</h2>
          <p className="text-slate-300">Accessing your content library...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-purple-500/20 bg-black/20 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl">
                <Headphones className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-3xl font-bold">Podcast Empire Manager</h1>
                <p className="text-purple-200">AI-powered content creation and distribution</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-2xl font-bold text-emerald-400">{formatNumber(totalDownloads)}</div>
                <div className="text-sm text-slate-300">Total Downloads</div>
              </div>
              <button
                onClick={() => toast.info('New episode wizard launched!')}
                className="bg-gradient-to-r from-purple-500 to-pink-600 px-6 py-3 rounded-xl font-semibold transition-all duration-300 hover:scale-105"
              >
                <Upload className="w-5 h-5 mr-2 inline" />
                Upload Episode
              </button>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex space-x-1 mt-6 bg-black/30 rounded-xl p-2">
            {[
              { id: 'episodes', label: '🎧 Episodes', icon: PlayCircle },
              { id: 'analytics', label: '📊 Analytics', icon: BarChart3 },
              { id: 'distribution', label: '🌐 Distribution', icon: Globe },
              { id: 'automation', label: '⚡ AI Automation', icon: Zap },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center px-6 py-3 rounded-lg font-semibold transition-all duration-300 ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-purple-500 to-pink-600 text-white'
                    : 'text-purple-200 hover:text-white hover:bg-white/10'
                }`}
              >
                <tab.icon className="w-5 h-5 mr-2" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Episodes Tab */}
        {activeTab === 'episodes' && (
          <div className="space-y-6">
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-400 text-sm">Total Episodes</p>
                    <p className="text-2xl font-bold">{episodes.length}</p>
                  </div>
                  <PlayCircle className="w-8 h-8 text-purple-400" />
                </div>
              </div>

              <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-400 text-sm">Total Downloads</p>
                    <p className="text-2xl font-bold">{formatNumber(totalDownloads)}</p>
                  </div>
                  <Download className="w-8 h-8 text-emerald-400" />
                </div>
              </div>

              <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-400 text-sm">Total Views</p>
                    <p className="text-2xl font-bold">{formatNumber(totalViews)}</p>
                  </div>
                  <Eye className="w-8 h-8 text-blue-400" />
                </div>
              </div>

              <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-400 text-sm">Avg Engagement</p>
                    <p className="text-2xl font-bold">{avgEngagement.toFixed(1)}%</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-yellow-400" />
                </div>
              </div>
            </div>

            {/* Episodes List */}
            <div className="space-y-4">
              {episodes.map((episode) => (
                <div
                  key={episode.id}
                  className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 hover:border-purple-500/50 transition-all duration-300"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-xl font-bold">{episode.title}</h3>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
                            episode.status === 'published'
                              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500'
                              : episode.status === 'processing'
                              ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500'
                              : episode.status === 'scheduled'
                              ? 'bg-blue-500/20 text-blue-400 border border-blue-500'
                              : 'bg-slate-500/20 text-slate-400 border border-slate-500'
                          }`}
                        >
                          {episode.status.toUpperCase()}
                        </span>
                      </div>

                      <p className="text-slate-300 mb-4">{episode.description}</p>

                      <div className="flex items-center space-x-6 text-sm text-slate-400">
                        <div className="flex items-center">
                          <Clock className="w-4 h-4 mr-1" />
                          {episode.duration}
                        </div>
                        <div className="flex items-center">
                          <Calendar className="w-4 h-4 mr-1" />
                          {episode.publishDate}
                        </div>
                        <div className="flex items-center">
                          <Download className="w-4 h-4 mr-1" />
                          {formatNumber(episode.downloadCount)}
                        </div>
                        <div className="flex items-center">
                          <Eye className="w-4 h-4 mr-1" />
                          {formatNumber(episode.viewCount)}
                        </div>
                        <div className="flex items-center">
                          <TrendingUp className="w-4 h-4 mr-1" />
                          {episode.engagementRate}%
                        </div>
                      </div>

                      {/* Platform Status */}
                      <div className="flex items-center space-x-2 mt-4">
                        {episode.platforms.map((platform) => (
                          <div
                            key={platform.platform}
                            className={`px-2 py-1 rounded text-xs font-medium ${
                              platform.status === 'published'
                                ? 'bg-emerald-500/20 text-emerald-400'
                                : platform.status === 'pending'
                                ? 'bg-yellow-500/20 text-yellow-400'
                                : 'bg-red-500/20 text-red-400'
                            }`}
                          >
                            {platform.platform}
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center space-x-3 ml-6">
                      <button
                        onClick={() => setSelectedEpisode(episode)}
                        className="p-2 bg-blue-500/20 border border-blue-500 hover:bg-blue-500/30 rounded-lg transition-colors"
                      >
                        <Eye className="w-5 h-5 text-blue-400" />
                      </button>
                      <button
                        onClick={() => toast.info('Episode editor opened')}
                        className="p-2 bg-purple-500/20 border border-purple-500 hover:bg-purple-500/30 rounded-lg transition-colors"
                      >
                        <Edit3 className="w-5 h-5 text-purple-400" />
                      </button>
                      <button
                        onClick={() => toast.success('Shared to social media!')}
                        className="p-2 bg-emerald-500/20 border border-emerald-500 hover:bg-emerald-500/30 rounded-lg transition-colors"
                      >
                        <Share2 className="w-5 h-5 text-emerald-400" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 backdrop-blur border border-purple-500/30 rounded-2xl p-8">
              <h2 className="text-2xl font-bold mb-6">Podcast Performance Analytics</h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white/10 rounded-xl p-6">
                  <h3 className="font-bold text-lg mb-3 text-emerald-400">Growth Metrics</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span>Monthly Growth:</span>
                      <span className="font-bold text-emerald-400">+24%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>New Subscribers:</span>
                      <span className="font-bold">+1,247</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Retention Rate:</span>
                      <span className="font-bold">87%</span>
                    </div>
                  </div>
                </div>

                <div className="bg-white/10 rounded-xl p-6">
                  <h3 className="font-bold text-lg mb-3 text-blue-400">Engagement</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span>Avg Listen Time:</span>
                      <span className="font-bold text-blue-400">34:22</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Completion Rate:</span>
                      <span className="font-bold">76%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Shares per Episode:</span>
                      <span className="font-bold">156</span>
                    </div>
                  </div>
                </div>

                <div className="bg-white/10 rounded-xl p-6">
                  <h3 className="font-bold text-lg mb-3 text-yellow-400">Revenue Impact</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span>Leads Generated:</span>
                      <span className="font-bold text-yellow-400">245</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Conversion Rate:</span>
                      <span className="font-bold">12.3%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Revenue Attribution:</span>
                      <span className="font-bold">£18,500</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Distribution Tab */}
        {activeTab === 'distribution' && (
          <div className="space-y-6">
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-8">
              <h2 className="text-2xl font-bold mb-6">Multi-Platform Distribution</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                  { name: 'Apple Podcasts', status: 'connected', color: 'text-blue-400' },
                  { name: 'Spotify', status: 'connected', color: 'text-emerald-400' },
                  { name: 'YouTube', status: 'connected', color: 'text-red-400' },
                  { name: 'LinkedIn', status: 'connected', color: 'text-blue-400' },
                  { name: 'Google Podcasts', status: 'pending', color: 'text-yellow-400' },
                  { name: 'Twitter Spaces', status: 'pending', color: 'text-purple-400' },
                  { name: 'Facebook', status: 'disconnected', color: 'text-slate-400' },
                  { name: 'TikTok', status: 'disconnected', color: 'text-slate-400' },
                ].map((platform) => (
                  <div key={platform.name} className="bg-slate-700/50 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-bold">{platform.name}</h3>
                      <div className={`w-3 h-3 rounded-full ${
                        platform.status === 'connected' ? 'bg-emerald-400' :
                        platform.status === 'pending' ? 'bg-yellow-400' :
                        'bg-slate-400'
                      }`}></div>
                    </div>

                    <div className={`text-sm font-medium ${platform.color} mb-3 capitalize`}>
                      {platform.status}
                    </div>

                    {platform.status === 'connected' ? (
                      <button
                        onClick={() => toast.info(`Managing ${platform.name} integration`)}
                        className="w-full bg-emerald-500/20 border border-emerald-500 hover:bg-emerald-500/30 px-4 py-2 rounded-lg text-sm transition-colors"
                      >
                        Manage
                      </button>
                    ) : (
                      <button
                        onClick={() => toast.success(`Connecting to ${platform.name}...`)}
                        className="w-full bg-blue-500/20 border border-blue-500 hover:bg-blue-500/30 px-4 py-2 rounded-lg text-sm transition-colors"
                      >
                        Connect
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* AI Automation Tab */}
        {activeTab === 'automation' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 backdrop-blur border border-purple-500/30 rounded-2xl p-8">
              <div className="flex items-center mb-6">
                <Zap className="w-8 h-8 text-yellow-400 mr-3" />
                <h2 className="text-2xl font-bold">AI Content Automation</h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-xl font-bold mb-4 text-purple-400">Automated Content Generation</h3>
                  <div className="space-y-4">
                    {[
                      { name: 'Transcription', desc: 'AI-powered speech-to-text', icon: FileText },
                      { name: 'Show Notes', desc: 'Detailed episode summaries', icon: Edit3 },
                      { name: 'Social Clips', desc: '60-second highlight reels', icon: Video },
                      { name: 'Blog Posts', desc: 'SEO-optimized articles', icon: Globe },
                      { name: 'Email Newsletter', desc: 'Subscriber updates', icon: Mail },
                      { name: 'SEO Keywords', desc: 'Search optimization', icon: Target },
                    ].map((item) => (
                      <div key={item.name} className="bg-white/10 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <item.icon className="w-5 h-5 text-purple-400 mr-3" />
                            <div>
                              <div className="font-medium">{item.name}</div>
                              <div className="text-sm text-purple-200">{item.desc}</div>
                            </div>
                          </div>
                          <button
                            onClick={() => generateAIContent('1', item.name.toLowerCase())}
                            className="bg-purple-500 hover:bg-purple-600 px-3 py-1 rounded text-sm font-medium transition-colors"
                          >
                            Generate
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-bold mb-4 text-emerald-400">Distribution Automation</h3>
                  <div className="space-y-4">
                    {[
                      'Automatic platform publishing',
                      'Social media scheduling',
                      'Email subscriber notifications',
                      'RSS feed updates',
                      'SEO meta tag generation',
                      'Thumbnail optimization',
                    ].map((feature, index) => (
                      <div key={index} className="bg-white/10 rounded-lg p-4 flex items-center">
                        <div className="w-2 h-2 bg-emerald-400 rounded-full mr-3"></div>
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>

                  <div className="mt-6 bg-emerald-500/20 border border-emerald-500 rounded-lg p-4">
                    <div className="font-bold text-emerald-400 mb-2">AI Savings</div>
                    <div className="text-sm text-emerald-200">
                      Automation saves 15+ hours per episode vs manual content creation
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  } else {
    return num.toString();
  }
};

export default PodcastManager;