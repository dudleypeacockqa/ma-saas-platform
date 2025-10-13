import React, { useState, useRef, useEffect } from 'react';
import {
  Mic,
  MicOff,
  Video,
  VideoOff,
  Monitor,
  MonitorSpeaker,
  Users,
  Settings,
  PlayCircle,
  Square,
  Pause,
  Volume2,
  VolumeX,
  Upload,
  Download,
  Share2,
  Eye,
  Clock,
  Wifi,
  WifiOff,
  Camera,
  CameraOff,
  Phone,
  PhoneCall,
  MessageCircle,
  Zap,
  Film,
  Waveform,
  Radio,
  Cast,
  Globe,
  Youtube,
  Facebook,
  Twitter,
  Linkedin,
  Twitch,
  Instagram,
  Send,
  FileText,
  Scissors,
  Sparkles,
  Brain,
  BarChart3,
  Target,
  Crown,
  Award,
  TrendingUp
} from 'lucide-react';
import { useUser } from '@clerk/clerk-react';
import { toast } from 'sonner';

interface StreamYardGuest {
  id: string;
  name: string;
  email: string;
  avatar: string;
  status: 'connected' | 'disconnected' | 'invited' | 'waiting';
  audioEnabled: boolean;
  videoEnabled: boolean;
  screenShareEnabled: boolean;
  quality: 'HD' | '4K' | 'SD' | 'Poor';
  bandwidth: number;
  location: string;
  role: 'host' | 'co-host' | 'guest';
}

interface LiveStreamPlatform {
  id: string;
  name: string;
  icon: React.ComponentType;
  enabled: boolean;
  viewers: number;
  status: 'live' | 'offline' | 'starting' | 'error';
  rtmpUrl?: string;
  streamKey?: string;
}

interface RecordingSession {
  id: string;
  title: string;
  startTime: Date;
  duration: string;
  status: 'recording' | 'paused' | 'stopped' | 'processing';
  guests: StreamYardGuest[];
  platforms: LiveStreamPlatform[];
  settings: {
    quality: '4K' | 'HD' | 'SD';
    format: 'MP4' | 'WebM' | 'MP3';
    autoTranscription: boolean;
    autoHighlights: boolean;
    aiShowNotes: boolean;
    socialClips: boolean;
    liveStream: boolean;
    multitrack: boolean;
    noiseReduction: boolean;
    autoLeveling: boolean;
  };
  analytics: {
    totalViewers: number;
    peakViewers: number;
    averageWatchTime: string;
    engagement: number;
    chatMessages: number;
  };
}

const StreamYardStudio: React.FC = () => {
  const { user } = useUser();
  const [isRecording, setIsRecording] = useState(false);
  const [isLive, setIsLive] = useState(false);
  const [currentSession, setCurrentSession] = useState<RecordingSession | null>(null);
  const [guests, setGuests] = useState<StreamYardGuest[]>([]);
  const [platforms, setPlatforms] = useState<LiveStreamPlatform[]>([
    { id: 'youtube', name: 'YouTube', icon: Youtube, enabled: true, viewers: 0, status: 'offline' },
    { id: 'facebook', name: 'Facebook Live', icon: Facebook, enabled: false, viewers: 0, status: 'offline' },
    { id: 'linkedin', name: 'LinkedIn Live', icon: Linkedin, enabled: true, viewers: 0, status: 'offline' },
    { id: 'twitter', name: 'X Spaces', icon: Twitter, enabled: false, viewers: 0, status: 'offline' },
    { id: 'twitch', name: 'Twitch', icon: Twitch, enabled: false, viewers: 0, status: 'offline' },
  ]);

  const [activeView, setActiveView] = useState<'studio' | 'guests' | 'stream' | 'analytics' | 'ai'>('studio');
  const [micEnabled, setMicEnabled] = useState(true);
  const [cameraEnabled, setCameraEnabled] = useState(true);
  const [screenShare, setScreenShare] = useState(false);
  const [chatVisible, setChatVisible] = useState(true);

  const videoRef = useRef<HTMLVideoElement>(null);

  // Mock guest data
  useEffect(() => {
    setGuests([
      {
        id: 'host',
        name: user?.fullName || 'Host',
        email: user?.primaryEmailAddress?.emailAddress || '',
        avatar: user?.imageUrl || '',
        status: 'connected',
        audioEnabled: true,
        videoEnabled: true,
        screenShareEnabled: false,
        quality: 'HD',
        bandwidth: 95,
        location: 'London, UK',
        role: 'host'
      }
    ]);
  }, [user]);

  const startRecording = () => {
    if (!currentSession) {
      const newSession: RecordingSession = {
        id: Date.now().toString(),
        title: 'M&A Masterclass - Live Session',
        startTime: new Date(),
        duration: '00:00:00',
        status: 'recording',
        guests: guests,
        platforms: platforms.filter(p => p.enabled),
        settings: {
          quality: 'HD',
          format: 'MP4',
          autoTranscription: true,
          autoHighlights: true,
          aiShowNotes: true,
          socialClips: true,
          liveStream: isLive,
          multitrack: true,
          noiseReduction: true,
          autoLeveling: true,
        },
        analytics: {
          totalViewers: 0,
          peakViewers: 0,
          averageWatchTime: '0:00',
          engagement: 0,
          chatMessages: 0
        }
      };
      setCurrentSession(newSession);
    }

    setIsRecording(true);
    toast.success('🎙️ Recording started - StreamYard quality enabled!');
  };

  const stopRecording = () => {
    setIsRecording(false);
    if (currentSession) {
      setCurrentSession({
        ...currentSession,
        status: 'processing'
      });
    }
    toast.success('🎬 Recording stopped - AI processing started!');
  };

  const goLive = () => {
    if (platforms.filter(p => p.enabled).length === 0) {
      toast.error('Please enable at least one streaming platform');
      return;
    }

    setIsLive(true);
    setPlatforms(prev => prev.map(p =>
      p.enabled ? { ...p, status: 'starting' } : p
    ));

    // Simulate going live
    setTimeout(() => {
      setPlatforms(prev => prev.map(p =>
        p.enabled ? { ...p, status: 'live', viewers: Math.floor(Math.random() * 50) + 10 } : p
      ));
      toast.success('🔴 LIVE on all enabled platforms!');
    }, 2000);
  };

  const stopLive = () => {
    setIsLive(false);
    setPlatforms(prev => prev.map(p =>
      p.enabled ? { ...p, status: 'offline', viewers: 0 } : p
    ));
    toast.info('📡 Live stream ended');
  };

  const inviteGuest = () => {
    const guestEmail = prompt('Enter guest email address:');
    if (guestEmail) {
      const newGuest: StreamYardGuest = {
        id: Date.now().toString(),
        name: guestEmail.split('@')[0],
        email: guestEmail,
        avatar: '/api/placeholder/40/40',
        status: 'invited',
        audioEnabled: false,
        videoEnabled: false,
        screenShareEnabled: false,
        quality: 'HD',
        bandwidth: 0,
        location: 'Unknown',
        role: 'guest'
      };
      setGuests(prev => [...prev, newGuest]);
      toast.success(`📧 Invitation sent to ${guestEmail}`);
    }
  };

  const togglePlatform = (platformId: string) => {
    setPlatforms(prev => prev.map(p =>
      p.id === platformId ? { ...p, enabled: !p.enabled } : p
    ));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      {/* Header */}
      <div className="bg-black/30 backdrop-blur border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-red-600 rounded-xl">
                <Radio className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">StreamYard Pro Studio</h1>
                <p className="text-gray-300">Professional podcast & live streaming</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center text-emerald-400 text-sm">
                <div className="w-2 h-2 bg-emerald-400 rounded-full mr-2 animate-pulse"></div>
                {isLive ? 'LIVE' : isRecording ? 'RECORDING' : 'READY'}
              </div>
              <div className="text-white text-sm">
                {currentSession ? currentSession.duration : '00:00:00'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-black/20 backdrop-blur border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-1 py-2">
            {[
              { id: 'studio', label: '🎬 Studio', icon: Video },
              { id: 'guests', label: '👥 Guests', icon: Users },
              { id: 'stream', label: '📡 Stream', icon: Cast },
              { id: 'analytics', label: '📊 Analytics', icon: BarChart3 },
              { id: 'ai', label: '🤖 AI Tools', icon: Brain }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveView(tab.id as any)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  activeView === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:text-white hover:bg-white/10'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Studio View */}
        {activeView === 'studio' && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Main Video Area */}
            <div className="lg:col-span-3">
              <div className="bg-black rounded-2xl p-6 mb-6">
                <div className="aspect-video bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl flex items-center justify-center relative overflow-hidden">
                  <video
                    ref={videoRef}
                    className="w-full h-full object-cover"
                    autoPlay
                    muted
                    playsInline
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center text-white">
                      <Camera className="w-16 h-16 mx-auto mb-4 opacity-50" />
                      <p className="text-lg mb-2">Camera Ready</p>
                      <p className="text-sm text-gray-400">Click to start preview</p>
                    </div>
                  </div>

                  {/* Recording Indicator */}
                  {isRecording && (
                    <div className="absolute top-4 left-4 bg-red-600 px-3 py-1 rounded-full flex items-center">
                      <div className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></div>
                      <span className="text-white text-sm font-semibold">REC</span>
                    </div>
                  )}

                  {/* Live Indicator */}
                  {isLive && (
                    <div className="absolute top-4 right-4 bg-red-600 px-3 py-1 rounded-full flex items-center">
                      <div className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></div>
                      <span className="text-white text-sm font-semibold">LIVE</span>
                      <span className="text-white text-sm ml-2">
                        {platforms.filter(p => p.enabled).reduce((sum, p) => sum + p.viewers, 0)} viewers
                      </span>
                    </div>
                  )}
                </div>

                {/* Studio Controls */}
                <div className="flex items-center justify-between mt-6">
                  <div className="flex items-center space-x-4">
                    <button
                      onClick={() => setMicEnabled(!micEnabled)}
                      className={`p-3 rounded-xl transition-all ${
                        micEnabled
                          ? 'bg-gray-700 text-white hover:bg-gray-600'
                          : 'bg-red-600 text-white hover:bg-red-700'
                      }`}
                    >
                      {micEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
                    </button>
                    <button
                      onClick={() => setCameraEnabled(!cameraEnabled)}
                      className={`p-3 rounded-xl transition-all ${
                        cameraEnabled
                          ? 'bg-gray-700 text-white hover:bg-gray-600'
                          : 'bg-red-600 text-white hover:bg-red-700'
                      }`}
                    >
                      {cameraEnabled ? <Camera className="w-5 h-5" /> : <CameraOff className="w-5 h-5" />}
                    </button>
                    <button
                      onClick={() => setScreenShare(!screenShare)}
                      className={`p-3 rounded-xl transition-all ${
                        screenShare
                          ? 'bg-blue-600 text-white hover:bg-blue-700'
                          : 'bg-gray-700 text-white hover:bg-gray-600'
                      }`}
                    >
                      <Monitor className="w-5 h-5" />
                    </button>
                  </div>

                  <div className="flex items-center space-x-4">
                    {!isRecording ? (
                      <button
                        onClick={startRecording}
                        className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-xl flex items-center font-semibold transition-all hover:scale-105"
                      >
                        <PlayCircle className="w-5 h-5 mr-2" />
                        Start Recording
                      </button>
                    ) : (
                      <button
                        onClick={stopRecording}
                        className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-xl flex items-center font-semibold"
                      >
                        <Square className="w-5 h-5 mr-2" />
                        Stop Recording
                      </button>
                    )}

                    {!isLive ? (
                      <button
                        onClick={goLive}
                        className="bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 text-white px-6 py-3 rounded-xl flex items-center font-semibold transition-all hover:scale-105"
                      >
                        <Radio className="w-5 h-5 mr-2" />
                        Go Live
                      </button>
                    ) : (
                      <button
                        onClick={stopLive}
                        className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-xl flex items-center font-semibold"
                      >
                        <Square className="w-5 h-5 mr-2" />
                        End Live
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* Guest Preview Grid */}
              {guests.filter(g => g.status === 'connected').length > 1 && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {guests.filter(g => g.status === 'connected').slice(1).map((guest) => (
                    <div key={guest.id} className="bg-gray-800 rounded-xl p-4">
                      <div className="aspect-video bg-gray-700 rounded-lg mb-3 flex items-center justify-center">
                        <div className="text-center">
                          <div className="w-12 h-12 bg-gray-600 rounded-full mx-auto mb-2"></div>
                          <p className="text-white text-sm">{guest.name}</p>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-300">{guest.quality}</span>
                        <div className="flex space-x-1">
                          {guest.audioEnabled ? (
                            <Mic className="w-4 h-4 text-green-400" />
                          ) : (
                            <MicOff className="w-4 h-4 text-red-400" />
                          )}
                          {guest.videoEnabled ? (
                            <Camera className="w-4 h-4 text-green-400" />
                          ) : (
                            <CameraOff className="w-4 h-4 text-red-400" />
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Quick Actions */}
              <div className="bg-black/50 rounded-2xl p-6">
                <h3 className="text-white font-semibold mb-4">Quick Actions</h3>
                <div className="space-y-3">
                  <button
                    onClick={inviteGuest}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg flex items-center justify-center"
                  >
                    <Users className="w-4 h-4 mr-2" />
                    Invite Guest
                  </button>
                  <button
                    onClick={() => toast.success('Scene templates loaded!')}
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-lg flex items-center justify-center"
                  >
                    <Film className="w-4 h-4 mr-2" />
                    Scene Templates
                  </button>
                  <button
                    onClick={() => toast.success('Overlays updated!')}
                    className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg flex items-center justify-center"
                  >
                    <Zap className="w-4 h-4 mr-2" />
                    Add Overlays
                  </button>
                </div>
              </div>

              {/* Live Chat Preview */}
              {chatVisible && (
                <div className="bg-black/50 rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-white font-semibold">Live Chat</h3>
                    <MessageCircle className="w-5 h-5 text-gray-400" />
                  </div>
                  <div className="space-y-3 max-h-40 overflow-y-auto">
                    <div className="text-sm">
                      <span className="text-blue-400 font-medium">John_M:</span>
                      <span className="text-gray-300 ml-2">Great insights on M&A valuations!</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-green-400 font-medium">Sarah_PE:</span>
                      <span className="text-gray-300 ml-2">When is the next deal review?</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-purple-400 font-medium">Alex_VC:</span>
                      <span className="text-gray-300 ml-2">🔥 Amazing content as always</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Guests View */}
        {activeView === 'guests' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <div className="bg-black/50 rounded-2xl p-6">
                <h2 className="text-2xl font-bold text-white mb-6">Guest Management</h2>
                <div className="space-y-4">
                  {guests.map((guest) => (
                    <div key={guest.id} className="bg-gray-800 rounded-xl p-4 flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gray-600 rounded-full flex items-center justify-center">
                          <Users className="w-6 h-6 text-gray-400" />
                        </div>
                        <div>
                          <h3 className="text-white font-medium">{guest.name}</h3>
                          <p className="text-gray-400 text-sm">{guest.email}</p>
                          <div className="flex items-center mt-1">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              guest.status === 'connected' ? 'bg-green-600 text-white' :
                              guest.status === 'invited' ? 'bg-yellow-600 text-white' :
                              'bg-red-600 text-white'
                            }`}>
                              {guest.status.toUpperCase()}
                            </span>
                            <span className="text-gray-400 text-xs ml-2">{guest.role}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {guest.audioEnabled ? (
                          <Mic className="w-5 h-5 text-green-400" />
                        ) : (
                          <MicOff className="w-5 h-5 text-red-400" />
                        )}
                        {guest.videoEnabled ? (
                          <Camera className="w-5 h-5 text-green-400" />
                        ) : (
                          <CameraOff className="w-5 h-5 text-red-400" />
                        )}
                        <div className="text-white text-sm">
                          {guest.quality}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <button
                  onClick={inviteGuest}
                  className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl flex items-center justify-center font-semibold"
                >
                  <Users className="w-5 h-5 mr-2" />
                  Invite New Guest
                </button>
              </div>
            </div>

            <div>
              <div className="bg-black/50 rounded-2xl p-6">
                <h3 className="text-white font-semibold mb-4">Guest Controls</h3>
                <div className="space-y-4">
                  <div>
                    <label className="text-gray-300 text-sm">Default Guest Role</label>
                    <select className="w-full mt-1 bg-gray-700 text-white rounded-lg p-2">
                      <option>Guest</option>
                      <option>Co-host</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-gray-300 text-sm">Auto-admit Guests</label>
                    <select className="w-full mt-1 bg-gray-700 text-white rounded-lg p-2">
                      <option>Require approval</option>
                      <option>Auto-admit</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-gray-300 text-sm">Guest Quality</label>
                    <select className="w-full mt-1 bg-gray-700 text-white rounded-lg p-2">
                      <option>HD</option>
                      <option>4K</option>
                      <option>Auto</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Stream View */}
        {activeView === 'stream' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <div className="bg-black/50 rounded-2xl p-6">
                <h2 className="text-2xl font-bold text-white mb-6">Live Stream Platforms</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {platforms.map((platform) => {
                    const IconComponent = platform.icon;
                    return (
                      <div key={platform.id} className="bg-gray-800 rounded-xl p-6">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center">
                            <IconComponent className="w-6 h-6 text-white mr-3" />
                            <h3 className="text-white font-medium">{platform.name}</h3>
                          </div>
                          <button
                            onClick={() => togglePlatform(platform.id)}
                            className={`w-12 h-6 rounded-full transition-colors ${
                              platform.enabled ? 'bg-blue-600' : 'bg-gray-600'
                            }`}
                          >
                            <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                              platform.enabled ? 'translate-x-6' : 'translate-x-1'
                            }`}></div>
                          </button>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                            platform.status === 'live' ? 'bg-red-600 text-white' :
                            platform.status === 'starting' ? 'bg-yellow-600 text-white' :
                            platform.status === 'error' ? 'bg-red-700 text-white' :
                            'bg-gray-600 text-white'
                          }`}>
                            {platform.status.toUpperCase()}
                          </span>

                          {platform.status === 'live' && (
                            <div className="text-white text-sm">
                              <Eye className="w-4 h-4 inline mr-1" />
                              {platform.viewers} viewers
                            </div>
                          )}
                        </div>

                        {platform.enabled && platform.status === 'offline' && (
                          <div className="mt-4 space-y-2">
                            <input
                              type="password"
                              placeholder="Stream Key"
                              className="w-full bg-gray-700 text-white rounded-lg p-2 text-sm"
                            />
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            <div>
              <div className="bg-black/50 rounded-2xl p-6 mb-6">
                <h3 className="text-white font-semibold mb-4">Stream Settings</h3>
                <div className="space-y-4">
                  <div>
                    <label className="text-gray-300 text-sm">Stream Quality</label>
                    <select className="w-full mt-1 bg-gray-700 text-white rounded-lg p-2">
                      <option>1080p HD</option>
                      <option>4K Ultra HD</option>
                      <option>720p</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-gray-300 text-sm">Bitrate</label>
                    <select className="w-full mt-1 bg-gray-700 text-white rounded-lg p-2">
                      <option>Auto</option>
                      <option>6000 kbps</option>
                      <option>4500 kbps</option>
                      <option>3000 kbps</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-gray-300 text-sm">Frame Rate</label>
                    <select className="w-full mt-1 bg-gray-700 text-white rounded-lg p-2">
                      <option>30 fps</option>
                      <option>60 fps</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="bg-black/50 rounded-2xl p-6">
                <h3 className="text-white font-semibold mb-4">Live Analytics</h3>
                {isLive ? (
                  <div className="space-y-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Total Viewers:</span>
                      <span className="text-white">{platforms.filter(p => p.enabled).reduce((sum, p) => sum + p.viewers, 0)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Peak Viewers:</span>
                      <span className="text-white">127</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Chat Messages:</span>
                      <span className="text-white">42</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Engagement:</span>
                      <span className="text-green-400">85%</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-gray-400 py-8">
                    <Cast className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>Go live to see analytics</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Analytics View */}
        {activeView === 'analytics' && (
          <div className="space-y-6">
            <div className="bg-black/50 rounded-2xl p-6">
              <h2 className="text-2xl font-bold text-white mb-6">Podcast Analytics</h2>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-gray-800 rounded-xl p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-400 text-sm">Total Downloads</p>
                      <p className="text-2xl font-bold text-white">15,420</p>
                      <p className="text-emerald-400 text-sm">+12.5% vs last month</p>
                    </div>
                    <BarChart3 className="w-8 h-8 text-emerald-400" />
                  </div>
                </div>

                <div className="bg-gray-800 rounded-xl p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-400 text-sm">Avg. Watch Time</p>
                      <p className="text-2xl font-bold text-white">42m 15s</p>
                      <p className="text-blue-400 text-sm">78% completion rate</p>
                    </div>
                    <Clock className="w-8 h-8 text-blue-400" />
                  </div>
                </div>

                <div className="bg-gray-800 rounded-xl p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-400 text-sm">Live Viewers</p>
                      <p className="text-2xl font-bold text-white">8,750</p>
                      <p className="text-purple-400 text-sm">Peak: 12,340</p>
                    </div>
                    <Eye className="w-8 h-8 text-purple-400" />
                  </div>
                </div>

                <div className="bg-gray-800 rounded-xl p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-400 text-sm">Lead Generation</p>
                      <p className="text-2xl font-bold text-white">245</p>
                      <p className="text-yellow-400 text-sm">From CTAs</p>
                    </div>
                    <Target className="w-8 h-8 text-yellow-400" />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-white font-semibold mb-4">Top Episodes</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-300">M&A Valuation Masterclass</span>
                      <span className="text-white">3,200 downloads</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Due Diligence Deep Dive</span>
                      <span className="text-white">2,850 downloads</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Private Equity Trends 2025</span>
                      <span className="text-white">2,640 downloads</span>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-white font-semibold mb-4">Platform Performance</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-300">YouTube</span>
                      <span className="text-white">45% of traffic</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Apple Podcasts</span>
                      <span className="text-white">28% of traffic</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Spotify</span>
                      <span className="text-white">18% of traffic</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Others</span>
                      <span className="text-white">9% of traffic</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* AI Tools View */}
        {activeView === 'ai' && (
          <div className="space-y-6">
            <div className="bg-black/50 rounded-2xl p-6">
              <div className="flex items-center mb-6">
                <Brain className="w-8 h-8 text-purple-400 mr-3" />
                <h2 className="text-2xl font-bold text-white">AI-Powered Content Suite</h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl p-6">
                  <div className="flex items-center mb-4">
                    <FileText className="w-6 h-6 text-white mr-2" />
                    <h3 className="text-white font-semibold">Auto Transcription</h3>
                  </div>
                  <p className="text-blue-100 text-sm mb-4">
                    AI-powered transcription with speaker identification and timestamps
                  </p>
                  <button className="bg-white text-blue-600 px-4 py-2 rounded-lg font-semibold hover:bg-blue-50">
                    Generate Transcript
                  </button>
                </div>

                <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-xl p-6">
                  <div className="flex items-center mb-4">
                    <Sparkles className="w-6 h-6 text-white mr-2" />
                    <h3 className="text-white font-semibold">Show Notes</h3>
                  </div>
                  <p className="text-green-100 text-sm mb-4">
                    Automatically generate detailed show notes with key takeaways
                  </p>
                  <button className="bg-white text-green-600 px-4 py-2 rounded-lg font-semibold hover:bg-green-50">
                    Create Show Notes
                  </button>
                </div>

                <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-xl p-6">
                  <div className="flex items-center mb-4">
                    <Scissors className="w-6 h-6 text-white mr-2" />
                    <h3 className="text-white font-semibold">Social Clips</h3>
                  </div>
                  <p className="text-purple-100 text-sm mb-4">
                    Extract viral moments and create social media clips automatically
                  </p>
                  <button className="bg-white text-purple-600 px-4 py-2 rounded-lg font-semibold hover:bg-purple-50">
                    Generate Clips
                  </button>
                </div>

                <div className="bg-gradient-to-br from-red-600 to-red-800 rounded-xl p-6">
                  <div className="flex items-center mb-4">
                    <Mail className="w-6 h-6 text-white mr-2" />
                    <h3 className="text-white font-semibold">Newsletter</h3>
                  </div>
                  <p className="text-red-100 text-sm mb-4">
                    Create email newsletter content from podcast highlights
                  </p>
                  <button className="bg-white text-red-600 px-4 py-2 rounded-lg font-semibold hover:bg-red-50">
                    Draft Newsletter
                  </button>
                </div>

                <div className="bg-gradient-to-br from-yellow-600 to-yellow-800 rounded-xl p-6">
                  <div className="flex items-center mb-4">
                    <Globe className="w-6 h-6 text-white mr-2" />
                    <h3 className="text-white font-semibold">Blog Post</h3>
                  </div>
                  <p className="text-yellow-100 text-sm mb-4">
                    Transform episodes into SEO-optimized blog posts
                  </p>
                  <button className="bg-white text-yellow-600 px-4 py-2 rounded-lg font-semibold hover:bg-yellow-50">
                    Create Blog Post
                  </button>
                </div>

                <div className="bg-gradient-to-br from-indigo-600 to-indigo-800 rounded-xl p-6">
                  <div className="flex items-center mb-4">
                    <TrendingUp className="w-6 h-6 text-white mr-2" />
                    <h3 className="text-white font-semibold">SEO Optimization</h3>
                  </div>
                  <p className="text-indigo-100 text-sm mb-4">
                    Optimize content for search engines and discovery
                  </p>
                  <button className="bg-white text-indigo-600 px-4 py-2 rounded-lg font-semibold hover:bg-indigo-50">
                    Optimize Content
                  </button>
                </div>
              </div>

              <div className="mt-8 bg-gray-800 rounded-xl p-6">
                <h3 className="text-white font-semibold mb-4">AI Processing Status</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Episode Transcription</span>
                    <span className="text-emerald-400">✓ Complete</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Show Notes Generation</span>
                    <span className="text-yellow-400">⏳ Processing...</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Social Clips Creation</span>
                    <span className="text-gray-400">⚪ Queued</span>
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

export default StreamYardStudio;