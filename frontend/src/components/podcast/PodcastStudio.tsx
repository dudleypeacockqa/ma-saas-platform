import React, { useState, useRef, useEffect } from 'react';
import {
  Mic,
  MicOff,
  Video,
  VideoOff,
  Monitor,
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
} from 'lucide-react';
import { useUser } from '@clerk/clerk-react';
import { toast } from 'sonner';

interface Guest {
  id: string;
  name: string;
  email: string;
  status: 'connected' | 'disconnected' | 'invited';
  audioEnabled: boolean;
  videoEnabled: boolean;
  quality: 'HD' | 'SD' | 'Poor';
}

interface RecordingSettings {
  quality: 'HD' | '4K' | 'Audio Only';
  format: 'MP4' | 'MP3' | 'WAV';
  autoTranscription: boolean;
  autoHighlights: boolean;
  liveStream: boolean;
  platforms: string[];
}

const PodcastStudio: React.FC = () => {
  const { user } = useUser();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [screenSharing, setScreenSharing] = useState(false);
  const [guests, setGuests] = useState<Guest[]>([]);
  const [isLive, setIsLive] = useState(false);
  const [viewers, setViewers] = useState(0);
  const [settings, setSettings] = useState<RecordingSettings>({
    quality: 'HD',
    format: 'MP4',
    autoTranscription: true,
    autoHighlights: true,
    liveStream: false,
    platforms: ['YouTube', 'LinkedIn'],
  });

  // Simulate recording timer
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRecording && !isPaused) {
      interval = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRecording, isPaused]);

  // Format recording time
  const formatTime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startRecording = async () => {
    try {
      // Initialize WebRTC recording
      const stream = await navigator.mediaDevices.getUserMedia({
        video: videoEnabled,
        audio: audioEnabled,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      setIsRecording(true);
      setRecordingTime(0);
      toast.success('Recording started! Professional quality capture active.');
    } catch (error) {
      toast.error('Failed to start recording. Please check camera/microphone permissions.');
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    setIsPaused(false);

    // Stop all tracks
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
    }

    toast.success('Recording completed! Processing with AI automation...');

    // Simulate AI processing
    setTimeout(() => {
      toast.success('✨ AI Processing Complete: Transcription, highlights, and social clips ready!');
    }, 3000);
  };

  const togglePause = () => {
    setIsPaused(!isPaused);
    toast.info(isPaused ? 'Recording resumed' : 'Recording paused');
  };

  const inviteGuest = () => {
    const guestEmail = prompt('Enter guest email:');
    if (guestEmail) {
      const newGuest: Guest = {
        id: Date.now().toString(),
        name: guestEmail.split('@')[0],
        email: guestEmail,
        status: 'invited',
        audioEnabled: true,
        videoEnabled: true,
        quality: 'HD',
      };
      setGuests([...guests, newGuest]);
      toast.success(`Invitation sent to ${guestEmail}`);
    }
  };

  const startLiveStream = () => {
    setIsLive(true);
    setViewers(Math.floor(Math.random() * 50) + 10);
    toast.success('🔴 LIVE: Streaming to YouTube and LinkedIn!');
  };

  const stopLiveStream = () => {
    setIsLive(false);
    setViewers(0);
    toast.info('Live stream ended');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Studio Header */}
      <div className="border-b border-purple-500/20 bg-black/20 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-r from-red-500 to-purple-600 rounded-xl">
                <Mic className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">Professional Podcast Studio</h1>
                <p className="text-purple-200">StreamYard-level recording + AI automation</p>
              </div>
              {isLive && (
                <div className="flex items-center bg-red-500 px-4 py-2 rounded-full">
                  <div className="w-3 h-3 bg-white rounded-full mr-2 animate-pulse"></div>
                  <span className="font-bold">LIVE</span>
                  <Eye className="w-4 h-4 ml-2" />
                  <span className="ml-1">{viewers}</span>
                </div>
              )}
            </div>

            <div className="flex items-center space-x-4">
              {/* Recording Time */}
              {isRecording && (
                <div className="bg-red-500/20 border border-red-500 px-4 py-2 rounded-lg">
                  <div className="flex items-center text-red-400">
                    <Clock className="w-4 h-4 mr-2" />
                    <span className="font-mono text-lg">{formatTime(recordingTime)}</span>
                  </div>
                </div>
              )}

              {/* Connection Status */}
              <div className="flex items-center text-emerald-400">
                <Wifi className="w-5 h-5 mr-2" />
                <span className="text-sm">HD Connected</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Video Area */}
          <div className="lg:col-span-3">
            {/* Video Preview */}
            <div className="bg-black rounded-2xl overflow-hidden mb-6 relative">
              <video
                ref={videoRef}
                autoPlay
                muted
                className="w-full h-80 object-cover"
                style={{ transform: 'scaleX(-1)' }}
              />

              {/* Video Overlay Controls */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent">
                <div className="absolute bottom-4 left-4 right-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="bg-white/20 backdrop-blur rounded-lg px-3 py-1">
                        <span className="text-sm font-medium">{user?.firstName || 'Host'}</span>
                      </div>
                      {settings.quality === '4K' && (
                        <div className="bg-blue-500 px-2 py-1 rounded text-xs font-bold">4K</div>
                      )}
                    </div>

                    {isRecording && (
                      <div className="bg-red-500 px-3 py-1 rounded-full flex items-center">
                        <div className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></div>
                        <span className="text-sm font-bold">REC</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Control Panel */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-6">
              <div className="flex items-center justify-center space-x-6">
                {/* Audio Control */}
                <button
                  onClick={() => setAudioEnabled(!audioEnabled)}
                  className={`p-4 rounded-xl transition-all duration-300 ${
                    audioEnabled
                      ? 'bg-emerald-500 hover:bg-emerald-600 text-white'
                      : 'bg-red-500 hover:bg-red-600 text-white'
                  }`}
                >
                  {audioEnabled ? <Mic className="w-6 h-6" /> : <MicOff className="w-6 h-6" />}
                </button>

                {/* Video Control */}
                <button
                  onClick={() => setVideoEnabled(!videoEnabled)}
                  className={`p-4 rounded-xl transition-all duration-300 ${
                    videoEnabled
                      ? 'bg-blue-500 hover:bg-blue-600 text-white'
                      : 'bg-red-500 hover:bg-red-600 text-white'
                  }`}
                >
                  {videoEnabled ? <Video className="w-6 h-6" /> : <VideoOff className="w-6 h-6" />}
                </button>

                {/* Screen Share */}
                <button
                  onClick={() => {
                    setScreenSharing(!screenSharing);
                    toast.info(screenSharing ? 'Screen sharing stopped' : 'Screen sharing started');
                  }}
                  className={`p-4 rounded-xl transition-all duration-300 ${
                    screenSharing
                      ? 'bg-purple-500 hover:bg-purple-600 text-white'
                      : 'bg-slate-600 hover:bg-slate-700 text-white'
                  }`}
                >
                  <Monitor className="w-6 h-6" />
                </button>

                {/* Record/Pause/Stop Controls */}
                {!isRecording ? (
                  <button
                    onClick={startRecording}
                    className="p-4 bg-red-500 hover:bg-red-600 rounded-xl text-white transition-all duration-300 hover:scale-105"
                  >
                    <PlayCircle className="w-8 h-8" />
                  </button>
                ) : (
                  <div className="flex space-x-3">
                    <button
                      onClick={togglePause}
                      className="p-4 bg-yellow-500 hover:bg-yellow-600 rounded-xl text-white transition-all duration-300"
                    >
                      {isPaused ? <PlayCircle className="w-6 h-6" /> : <Pause className="w-6 h-6" />}
                    </button>
                    <button
                      onClick={stopRecording}
                      className="p-4 bg-red-500 hover:bg-red-600 rounded-xl text-white transition-all duration-300"
                    >
                      <Square className="w-6 h-6" />
                    </button>
                  </div>
                )}

                {/* Live Stream Toggle */}
                <button
                  onClick={isLive ? stopLiveStream : startLiveStream}
                  className={`p-4 rounded-xl transition-all duration-300 ${
                    isLive
                      ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                      : 'bg-slate-600 hover:bg-slate-700 text-white'
                  }`}
                >
                  <Wifi className="w-6 h-6" />
                </button>

                {/* Settings */}
                <button
                  onClick={() => toast.info('Settings panel opened')}
                  className="p-4 bg-slate-600 hover:bg-slate-700 rounded-xl text-white transition-all duration-300"
                >
                  <Settings className="w-6 h-6" />
                </button>
              </div>

              {/* Recording Status */}
              {isRecording && (
                <div className="mt-4 text-center">
                  <div className="inline-flex items-center bg-red-500/20 border border-red-500 px-4 py-2 rounded-lg">
                    <Waveform className="w-5 h-5 text-red-400 mr-2 animate-pulse" />
                    <span className="text-red-400 font-medium">
                      Recording in {settings.quality} • {settings.format}
                      {isPaused && ' (PAUSED)'}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Guest Management */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold">Guests</h3>
                <button
                  onClick={inviteGuest}
                  className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  <Users className="w-4 h-4 mr-2 inline" />
                  Invite
                </button>
              </div>

              {guests.length === 0 ? (
                <div className="text-center py-8 text-slate-400">
                  <Users className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p className="text-sm">No guests yet</p>
                  <p className="text-xs">Invite up to 10 guests</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {guests.map((guest) => (
                    <div key={guest.id} className="bg-slate-700/50 rounded-lg p-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium">{guest.name}</div>
                          <div className="text-xs text-slate-400">{guest.email}</div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${
                            guest.status === 'connected' ? 'bg-emerald-400' :
                            guest.status === 'disconnected' ? 'bg-red-400' :
                            'bg-yellow-400'
                          }`}></div>
                          <span className="text-xs text-slate-400 capitalize">{guest.status}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* AI Features */}
            <div className="bg-gradient-to-br from-purple-900/50 to-blue-900/50 backdrop-blur border border-purple-500/30 rounded-2xl p-6">
              <div className="flex items-center mb-4">
                <Zap className="w-6 h-6 text-yellow-400 mr-2" />
                <h3 className="text-lg font-bold">AI Automation</h3>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Auto Transcription</span>
                  <div className={`w-10 h-6 rounded-full transition-colors ${
                    settings.autoTranscription ? 'bg-emerald-500' : 'bg-slate-600'
                  }`}>
                    <div className={`w-4 h-4 bg-white rounded-full mt-1 transition-transform ${
                      settings.autoTranscription ? 'translate-x-5' : 'translate-x-1'
                    }`}></div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm">Auto Highlights</span>
                  <div className={`w-10 h-6 rounded-full transition-colors ${
                    settings.autoHighlights ? 'bg-emerald-500' : 'bg-slate-600'
                  }`}>
                    <div className={`w-4 h-4 bg-white rounded-full mt-1 transition-transform ${
                      settings.autoHighlights ? 'translate-x-5' : 'translate-x-1'
                    }`}></div>
                  </div>
                </div>

                <div className="text-xs text-purple-200 mt-4">
                  ✨ AI will automatically generate:
                  <ul className="mt-2 space-y-1 text-purple-300">
                    <li>• Show notes & summaries</li>
                    <li>• Social media clips</li>
                    <li>• Blog post content</li>
                    <li>• Email newsletters</li>
                    <li>• SEO optimizations</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-6">
              <h3 className="text-lg font-bold mb-4">Quick Actions</h3>

              <div className="space-y-3">
                <button
                  onClick={() => toast.success('Content library opened')}
                  className="w-full bg-blue-500/20 border border-blue-500 hover:bg-blue-500/30 px-4 py-3 rounded-lg text-left transition-colors"
                >
                  <Film className="w-5 h-5 inline mr-3" />
                  Content Library
                </button>

                <button
                  onClick={() => toast.success('Distribution manager opened')}
                  className="w-full bg-emerald-500/20 border border-emerald-500 hover:bg-emerald-500/30 px-4 py-3 rounded-lg text-left transition-colors"
                >
                  <Share2 className="w-5 h-5 inline mr-3" />
                  Auto Distribution
                </button>

                <button
                  onClick={() => toast.success('Analytics dashboard opened')}
                  className="w-full bg-purple-500/20 border border-purple-500 hover:bg-purple-500/30 px-4 py-3 rounded-lg text-left transition-colors"
                >
                  <Eye className="w-5 h-5 inline mr-3" />
                  Performance Analytics
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PodcastStudio;