/**
 * Comprehensive Unit Tests for Content Creation Studio Component
 * Tests content creation, media upload, and production workflow
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ContentCreationStudio from '../pages/ContentCreationStudio';

// Mock Clerk
jest.mock('@clerk/clerk-react', () => ({
  useUser: () => ({
    user: {
      id: 'creator_123',
      firstName: 'Content',
      lastName: 'Creator',
      emailAddresses: [{ emailAddress: 'creator@example.com' }],
    },
    isSignedIn: true,
    isLoaded: true,
  }),
  useAuth: () => ({
    getToken: jest.fn().mockResolvedValue('creator_token'),
    isSignedIn: true,
    isLoaded: true,
  }),
}));

// Mock file upload
const mockFileUpload = jest.fn();
global.FormData = jest.fn(() => ({
  append: jest.fn(),
  set: jest.fn(),
  get: jest.fn(),
  has: jest.fn(),
}));

// Mock API calls
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock media recorder
global.MediaRecorder = jest.fn().mockImplementation(() => ({
  start: jest.fn(),
  stop: jest.fn(),
  ondataavailable: null,
  onstop: null,
  state: 'inactive',
}));

// Mock URL.createObjectURL
global.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
global.URL.revokeObjectURL = jest.fn();

// Test wrapper
const TestWrapper = ({ children }) => <BrowserRouter>{children}</BrowserRouter>;

describe('Content Creation Studio Component', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    // Mock content series API response
    mockFetch.mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          series: [
            {
              id: 'series_123',
              name: 'M&A Insights Podcast',
              content_type: 'podcast',
              episodes_count: 5,
            },
          ],
          episodes: [
            {
              id: 'episode_123',
              title: 'Getting Started with M&A',
              status: 'published',
              duration: 1800,
            },
          ],
        }),
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Component Rendering', () => {
    test('renders content creation studio without crashing', () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      expect(screen.getByRole('main')).toBeInTheDocument();
    });

    test('displays studio title and navigation', () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
      expect(screen.getByText(/content creation/i)).toBeInTheDocument();
    });

    test('renders content type tabs', () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      expect(screen.getByRole('tab', { name: /podcast/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /video/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /blog/i })).toBeInTheDocument();
    });

    test('displays content creation tools', () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      expect(screen.getByRole('button', { name: /new series/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /new episode/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /record/i })).toBeInTheDocument();
    });
  });

  describe('Content Series Management', () => {
    test('displays existing content series', async () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText('M&A Insights Podcast')).toBeInTheDocument();
      });
    });

    test('creates new content series', async () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      const newSeriesButton = screen.getByRole('button', { name: /new series/i });
      fireEvent.click(newSeriesButton);

      // Fill out series form
      const nameInput = screen.getByLabelText(/series name/i);
      const descInput = screen.getByLabelText(/description/i);

      fireEvent.change(nameInput, { target: { value: 'New Podcast Series' } });
      fireEvent.change(descInput, { target: { value: 'A new series about M&A' } });

      const createButton = screen.getByRole('button', { name: /create series/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/content/series'),
          expect.objectContaining({
            method: 'POST',
            body: expect.any(String),
          }),
        );
      });
    });

    test('edits existing series', async () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      await waitFor(() => {
        const editButton = screen.getByRole('button', { name: /edit.*series/i });
        fireEvent.click(editButton);
      });

      const nameInput = screen.getByDisplayValue('M&A Insights Podcast');
      fireEvent.change(nameInput, { target: { value: 'Updated Podcast Series' } });

      const saveButton = screen.getByRole('button', { name: /save/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/series/series_123'),
          expect.objectContaining({ method: 'PUT' }),
        );
      });
    });

    test('deletes series with confirmation', async () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      await waitFor(() => {
        const deleteButton = screen.getByRole('button', { name: /delete.*series/i });
        fireEvent.click(deleteButton);
      });

      // Confirm deletion
      const confirmButton = screen.getByRole('button', { name: /confirm/i });
      fireEvent.click(confirmButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/series/series_123'),
          expect.objectContaining({ method: 'DELETE' }),
        );
      });
    });
  });

  describe('Episode Creation and Management', () => {
    test('creates new episode', async () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      const newEpisodeButton = screen.getByRole('button', { name: /new episode/i });
      fireEvent.click(newEpisodeButton);

      // Fill episode form
      const titleInput = screen.getByLabelText(/episode title/i);
      const seriesSelect = screen.getByLabelText(/series/i);

      fireEvent.change(titleInput, { target: { value: 'New Episode Title' } });
      fireEvent.change(seriesSelect, { target: { value: 'series_123' } });

      const createButton = screen.getByRole('button', { name: /create episode/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/content/episodes'),
          expect.objectContaining({ method: 'POST' }),
        );
      });
    });

    test('displays episode list', async () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText('Getting Started with M&A')).toBeInTheDocument();
        expect(screen.getByText(/published/i)).toBeInTheDocument();
      });
    });

    test('edits episode details', async () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      await waitFor(() => {
        const editButton = screen.getByRole('button', { name: /edit.*episode/i });
        fireEvent.click(editButton);
      });

      const titleInput = screen.getByDisplayValue('Getting Started with M&A');
      fireEvent.change(titleInput, { target: { value: 'Updated Episode Title' } });

      const saveButton = screen.getByRole('button', { name: /save/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/episodes/episode_123'),
          expect.objectContaining({ method: 'PUT' }),
        );
      });
    });
  });

  describe('Media Upload and Recording', () => {
    test('uploads audio file', async () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      const uploadButton = screen.getByRole('button', { name: /upload.*audio/i });
      fireEvent.click(uploadButton);

      // Simulate file selection
      const fileInput = screen.getByLabelText(/choose.*file/i);
      const file = new File(['audio content'], 'podcast.mp3', { type: 'audio/mpeg' });

      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      });

      fireEvent.change(fileInput);

      await waitFor(() => {
        expect(screen.getByText('podcast.mp3')).toBeInTheDocument();
      });

      const confirmUploadButton = screen.getByRole('button', { name: /upload/i });
      fireEvent.click(confirmUploadButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/content/upload'),
          expect.objectContaining({ method: 'POST' }),
        );
      });
    });

    test('uploads video file', async () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      const videoTab = screen.getByRole('tab', { name: /video/i });
      fireEvent.click(videoTab);

      const uploadButton = screen.getByRole('button', { name: /upload.*video/i });
      fireEvent.click(uploadButton);

      const fileInput = screen.getByLabelText(/choose.*file/i);
      const file = new File(['video content'], 'video.mp4', { type: 'video/mp4' });

      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      });

      fireEvent.change(fileInput);

      await waitFor(() => {
        expect(screen.getByText('video.mp4')).toBeInTheDocument();
      });
    });

    test('validates file types', async () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      const uploadButton = screen.getByRole('button', { name: /upload/i });
      fireEvent.click(uploadButton);

      const fileInput = screen.getByLabelText(/choose.*file/i);
      const invalidFile = new File(['text content'], 'document.txt', { type: 'text/plain' });

      Object.defineProperty(fileInput, 'files', {
        value: [invalidFile],
        writable: false,
      });

      fireEvent.change(fileInput);

      await waitFor(() => {
        expect(screen.getByText(/invalid file type/i)).toBeInTheDocument();
      });
    });

    test('handles file size validation', async () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      const uploadButton = screen.getByRole('button', { name: /upload/i });
      fireEvent.click(uploadButton);

      const fileInput = screen.getByLabelText(/choose.*file/i);

      // Mock large file
      const largeFile = new File(['x'.repeat(100000000)], 'large.mp3', { type: 'audio/mpeg' });
      Object.defineProperty(largeFile, 'size', { value: 100000000 });

      Object.defineProperty(fileInput, 'files', {
        value: [largeFile],
        writable: false,
      });

      fireEvent.change(fileInput);

      await waitFor(() => {
        expect(screen.getByText(/file too large/i)).toBeInTheDocument();
      });
    });

    test('records audio directly', async () => {
      // Mock getUserMedia
      global.navigator.mediaDevices = {
        getUserMedia: jest.fn().mockResolvedValue({
          getTracks: () => [{ stop: jest.fn() }],
        }),
      };

      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      const recordButton = screen.getByRole('button', { name: /record/i });
      fireEvent.click(recordButton);

      await waitFor(() => {
        expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({
          audio: true,
        });
      });

      expect(screen.getByRole('button', { name: /stop.*recording/i })).toBeInTheDocument();
    });
  });

  describe('AI-Powered Content Features', () => {
    test('generates episode description with AI', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            description: 'AI-generated episode description about M&A strategies',
          }),
      });

      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      const aiButton = screen.getByRole('button', { name: /generate.*description/i });
      fireEvent.click(aiButton);

      const titleInput = screen.getByLabelText(/title/i);
      fireEvent.change(titleInput, { target: { value: 'M&A Due Diligence' } });

      const generateButton = screen.getByRole('button', { name: /generate/i });
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/ai/generate-description'),
          expect.objectContaining({ method: 'POST' }),
        );
      });

      await waitFor(() => {
        expect(screen.getByText(/AI-generated episode description/i)).toBeInTheDocument();
      });
    });

    test('generates show notes from transcript', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            show_notes: 'AI-generated show notes with key points',
          }),
      });

      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      const showNotesButton = screen.getByRole('button', { name: /generate.*notes/i });
      fireEvent.click(showNotesButton);

      const transcriptInput = screen.getByLabelText(/transcript/i);
      fireEvent.change(transcriptInput, {
        target: { value: 'This is a sample transcript...' },
      });

      const generateButton = screen.getByRole('button', { name: /generate/i });
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/ai/generate-show-notes'),
          expect.objectContaining({ method: 'POST' }),
        );
      });
    });

    test('transcribes audio file', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            transcript: 'Transcribed audio content...',
            status: 'completed',
          }),
      });

      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      const transcribeButton = screen.getByRole('button', { name: /transcribe/i });
      fireEvent.click(transcribeButton);

      const audioUrlInput = screen.getByLabelText(/audio.*url/i);
      fireEvent.change(audioUrlInput, {
        target: { value: 'https://example.com/audio.mp3' },
      });

      const startButton = screen.getByRole('button', { name: /start.*transcription/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/ai/transcribe'),
          expect.objectContaining({ method: 'POST' }),
        );
      });
    });
  });

  describe('Content Publishing and Distribution', () => {
    test('publishes episode to platforms', async () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      await waitFor(() => {
        const publishButton = screen.getByRole('button', { name: /publish/i });
        fireEvent.click(publishButton);
      });

      // Select platforms
      const spotifyCheckbox = screen.getByLabelText(/spotify/i);
      const applePodcastsCheckbox = screen.getByLabelText(/apple podcasts/i);

      fireEvent.click(spotifyCheckbox);
      fireEvent.click(applePodcastsCheckbox);

      const confirmPublishButton = screen.getByRole('button', { name: /confirm.*publish/i });
      fireEvent.click(confirmPublishButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/content/publish'),
          expect.objectContaining({
            method: 'POST',
            body: expect.stringContaining('spotify'),
          }),
        );
      });
    });

    test('schedules episode publication', async () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      const scheduleButton = screen.getByRole('button', { name: /schedule/i });
      fireEvent.click(scheduleButton);

      const dateInput = screen.getByLabelText(/publish date/i);
      const timeInput = screen.getByLabelText(/publish time/i);

      fireEvent.change(dateInput, { target: { value: '2024-06-01' } });
      fireEvent.change(timeInput, { target: { value: '09:00' } });

      const scheduleConfirmButton = screen.getByRole('button', { name: /schedule.*publication/i });
      fireEvent.click(scheduleConfirmButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/content/schedule'),
          expect.objectContaining({ method: 'POST' }),
        );
      });
    });

    test('displays publication status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            status: 'published',
            platforms: {
              spotify: 'published',
              apple_podcasts: 'pending',
              youtube: 'failed',
            },
          }),
      });

      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      await waitFor(() => {
        const statusButton = screen.getByRole('button', { name: /view.*status/i });
        fireEvent.click(statusButton);
      });

      await waitFor(() => {
        expect(screen.getByText(/spotify.*published/i)).toBeInTheDocument();
        expect(screen.getByText(/apple.*pending/i)).toBeInTheDocument();
        expect(screen.getByText(/youtube.*failed/i)).toBeInTheDocument();
      });
    });
  });

  describe('Content Analytics', () => {
    test('displays content performance metrics', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            total_views: 15420,
            total_downloads: 8950,
            engagement_rate: 78.5,
            top_episodes: [{ title: 'Getting Started with M&A', views: 3200 }],
          }),
      });

      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      const analyticsTab = screen.getByRole('tab', { name: /analytics/i });
      fireEvent.click(analyticsTab);

      await waitFor(() => {
        expect(screen.getByText('15,420')).toBeInTheDocument(); // Total views
        expect(screen.getByText('8,950')).toBeInTheDocument(); // Downloads
        expect(screen.getByText('78.5%')).toBeInTheDocument(); // Engagement
      });
    });

    test('shows episode-specific analytics', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            views: 3200,
            downloads: 1850,
            completion_rate: 85.2,
            audience_retention: [
              { time: 0, retention: 100 },
              { time: 300, retention: 92 },
              { time: 600, retention: 85 },
            ],
          }),
      });

      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      await waitFor(() => {
        const episodeAnalyticsButton = screen.getByRole('button', { name: /episode.*analytics/i });
        fireEvent.click(episodeAnalyticsButton);
      });

      await waitFor(() => {
        expect(screen.getByText('3,200')).toBeInTheDocument(); // Episode views
        expect(screen.getByText('85.2%')).toBeInTheDocument(); // Completion rate
      });
    });
  });

  describe('Error Handling and Edge Cases', () => {
    test('handles upload failures gracefully', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Upload failed'));

      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      const uploadButton = screen.getByRole('button', { name: /upload/i });
      fireEvent.click(uploadButton);

      const fileInput = screen.getByLabelText(/choose.*file/i);
      const file = new File(['content'], 'test.mp3', { type: 'audio/mpeg' });

      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      });

      fireEvent.change(fileInput);

      const confirmButton = screen.getByRole('button', { name: /upload/i });
      fireEvent.click(confirmButton);

      await waitFor(() => {
        expect(screen.getByText(/upload failed/i)).toBeInTheDocument();
      });
    });

    test('handles network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network Error'));

      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });
    });

    test('handles empty content state', () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ series: [], episodes: [] }),
      });

      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      expect(screen.getByText(/no content yet/i)).toBeInTheDocument();
      expect(screen.getByText(/create your first/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility and Usability', () => {
    test('supports keyboard navigation', () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      const firstButton = screen.getByRole('button', { name: /new series/i });
      firstButton.focus();

      expect(document.activeElement).toBe(firstButton);

      fireEvent.keyDown(firstButton, { key: 'Tab' });
      expect(document.activeElement).not.toBe(firstButton);
    });

    test('has proper ARIA attributes', () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByRole('tablist')).toBeInTheDocument();
      expect(screen.getByLabelText(/content creation studio/i)).toBeInTheDocument();
    });

    test('provides screen reader announcements', async () => {
      render(
        <TestWrapper>
          <ContentCreationStudio />
        </TestWrapper>,
      );

      const newSeriesButton = screen.getByRole('button', { name: /new series/i });
      fireEvent.click(newSeriesButton);

      await waitFor(() => {
        expect(screen.getByRole('status')).toBeInTheDocument();
      });
    });
  });
});

describe('Content Creation Studio Integration Tests', () => {
  test('complete content creation workflow', async () => {
    render(
      <TestWrapper>
        <ContentCreationStudio />
      </TestWrapper>,
    );

    // 1. Studio loads
    expect(screen.getByRole('main')).toBeInTheDocument();

    // 2. Create new series
    fireEvent.click(screen.getByRole('button', { name: /new series/i }));

    fireEvent.change(screen.getByLabelText(/series name/i), {
      target: { value: 'Test Series' },
    });

    fireEvent.click(screen.getByRole('button', { name: /create series/i }));

    // 3. Create episode
    await waitFor(() => {
      fireEvent.click(screen.getByRole('button', { name: /new episode/i }));
    });

    fireEvent.change(screen.getByLabelText(/episode title/i), {
      target: { value: 'Test Episode' },
    });

    fireEvent.click(screen.getByRole('button', { name: /create episode/i }));

    // 4. Upload media
    const uploadButton = screen.getByRole('button', { name: /upload/i });
    fireEvent.click(uploadButton);

    // 5. Publish content
    await waitFor(() => {
      const publishButton = screen.getByRole('button', { name: /publish/i });
      if (publishButton) {
        fireEvent.click(publishButton);
      }
    });

    // Complete workflow should execute without errors
    expect(screen.getByRole('main')).toBeInTheDocument();
  });
});
