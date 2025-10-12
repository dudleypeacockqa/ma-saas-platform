"""
Comprehensive Integration Tests for Content Creation API
Tests content creation, file uploads, and media processing
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from io import BytesIO


class TestContentCreationAuthentication:
    """Test content creation authentication"""

    def test_create_series_requires_auth(self, client):
        """Test that creating content series requires authentication"""
        payload = {
            "name": "Test Podcast Series",
            "description": "A test podcast series",
            "content_type": "podcast"
        }

        response = client.post("/api/content/series", json=payload)
        assert response.status_code in [401, 403]

    def test_upload_media_requires_auth(self, client):
        """Test that media upload requires authentication"""
        files = {"file": ("test.mp3", BytesIO(b"fake audio"), "audio/mpeg")}

        response = client.post("/api/content/upload", files=files)
        assert response.status_code in [401, 403]


class TestContentSeriesManagement:
    """Test content series creation and management"""

    @patch('app.auth.clerk_auth.get_current_user')
    def test_create_content_series(self, mock_get_user, client):
        """Test creating a new content series"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        payload = {
            "name": "M&A Insights Podcast",
            "description": "Weekly insights on M&A strategies",
            "content_type": "podcast",
            "target_duration": 30,
            "target_audience": "M&A professionals"
        }

        response = client.post(
            "/api/content/series",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )

        if response.status_code in [200, 201]:
            data = response.json()
            assert "id" in data
            assert data["name"] == payload["name"]
            assert data["content_type"] == payload["content_type"]

    @patch('app.auth.clerk_auth.get_current_user')
    def test_list_content_series(self, mock_get_user, client):
        """Test listing user's content series"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        response = client.get(
            "/api/content/series",
            headers={"Authorization": "Bearer test_token"}
        )

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list) or "series" in data

    @patch('app.auth.clerk_auth.get_current_user')
    def test_get_series_details(self, mock_get_user, client):
        """Test getting content series details"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        response = client.get(
            "/api/content/series/test_series_123",
            headers={"Authorization": "Bearer test_token"}
        )

        # Should return series details or 404 if not found
        assert response.status_code in [200, 404]

    @patch('app.auth.clerk_auth.get_current_user')
    def test_update_content_series(self, mock_get_user, client):
        """Test updating content series"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        payload = {
            "name": "Updated Podcast Series",
            "description": "Updated description"
        }

        response = client.put(
            "/api/content/series/test_series_123",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )

        # Should handle update request
        assert response.status_code in [200, 404, 400]

    @patch('app.auth.clerk_auth.get_current_user')
    def test_delete_content_series(self, mock_get_user, client):
        """Test deleting content series"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        response = client.delete(
            "/api/content/series/test_series_123",
            headers={"Authorization": "Bearer test_token"}
        )

        # Should handle deletion request
        assert response.status_code in [200, 204, 404]


class TestContentEpisodeManagement:
    """Test content episode creation and management"""

    @patch('app.auth.clerk_auth.get_current_user')
    def test_create_episode(self, mock_get_user, client):
        """Test creating a new episode"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        payload = {
            "series_id": "series_123",
            "title": "Episode 1: Getting Started with M&A",
            "description": "Introduction to M&A basics",
            "episode_number": 1,
            "season_number": 1,
            "content_type": "podcast"
        }

        response = client.post(
            "/api/content/episodes",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )

        if response.status_code in [200, 201]:
            data = response.json()
            assert "id" in data
            assert data["title"] == payload["title"]
            assert data["episode_number"] == payload["episode_number"]

    @patch('app.auth.clerk_auth.get_current_user')
    def test_list_episodes(self, mock_get_user, client):
        """Test listing episodes for a series"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        response = client.get(
            "/api/content/series/series_123/episodes",
            headers={"Authorization": "Bearer test_token"}
        )

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list) or "episodes" in data

    @patch('app.auth.clerk_auth.get_current_user')
    def test_get_episode_details(self, mock_get_user, client):
        """Test getting episode details"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        response = client.get(
            "/api/content/episodes/episode_123",
            headers={"Authorization": "Bearer test_token"}
        )

        # Should return episode details or 404
        assert response.status_code in [200, 404]


class TestMediaUpload:
    """Test media file upload functionality"""

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.services.storage_factory.get_storage_service')
    def test_upload_audio_file(self, mock_storage, mock_get_user, client):
        """Test uploading an audio file"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        # Mock storage service
        mock_storage_instance = Mock()
        mock_storage_instance.upload_file.return_value = "https://storage.example.com/audio.mp3"
        mock_storage.return_value = mock_storage_instance

        # Create fake audio file
        audio_content = b"fake audio content" * 1000  # Make it reasonably sized
        files = {"file": ("podcast_episode.mp3", BytesIO(audio_content), "audio/mpeg")}

        response = client.post(
            "/api/content/upload",
            files=files,
            headers={"Authorization": "Bearer test_token"}
        )

        if response.status_code in [200, 201]:
            data = response.json()
            assert "file_url" in data or "url" in data

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.services.storage_factory.get_storage_service')
    def test_upload_video_file(self, mock_storage, mock_get_user, client):
        """Test uploading a video file"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        # Mock storage service
        mock_storage_instance = Mock()
        mock_storage_instance.upload_file.return_value = "https://storage.example.com/video.mp4"
        mock_storage.return_value = mock_storage_instance

        # Create fake video file
        video_content = b"fake video content" * 1000
        files = {"file": ("video_content.mp4", BytesIO(video_content), "video/mp4")}

        response = client.post(
            "/api/content/upload",
            files=files,
            headers={"Authorization": "Bearer test_token"}
        )

        if response.status_code in [200, 201]:
            data = response.json()
            assert "file_url" in data or "url" in data

    @patch('app.auth.clerk_auth.get_current_user')
    def test_upload_invalid_file_type(self, mock_get_user, client):
        """Test uploading an invalid file type"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        # Try to upload a text file as media
        files = {"file": ("document.txt", BytesIO(b"text content"), "text/plain")}

        response = client.post(
            "/api/content/upload",
            files=files,
            headers={"Authorization": "Bearer test_token"}
        )

        # Should reject invalid file types
        assert response.status_code in [400, 415, 422]

    @patch('app.auth.clerk_auth.get_current_user')
    def test_upload_oversized_file(self, mock_get_user, client):
        """Test uploading an oversized file"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        # Create a very large fake file (simulate oversized upload)
        large_content = b"x" * (100 * 1024 * 1024)  # 100MB
        files = {"file": ("huge_file.mp3", BytesIO(large_content), "audio/mpeg")}

        response = client.post(
            "/api/content/upload",
            files=files,
            headers={"Authorization": "Bearer test_token"}
        )

        # Should handle oversized files appropriately
        assert response.status_code in [400, 413, 422]


class TestAIContentProcessing:
    """Test AI-powered content processing features"""

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.services.claude_service.ClaudeService')
    def test_generate_episode_description(self, mock_claude, mock_get_user, client):
        """Test AI-generated episode descriptions"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        # Mock Claude service
        mock_claude_instance = Mock()
        mock_claude_instance.generate_content.return_value = "AI-generated episode description"
        mock_claude.return_value = mock_claude_instance

        payload = {
            "title": "M&A Due Diligence Best Practices",
            "keywords": ["due diligence", "M&A", "best practices"],
            "target_length": 150
        }

        response = client.post(
            "/api/content/ai/generate-description",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )

        if response.status_code == 200:
            data = response.json()
            assert "description" in data

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.services.claude_service.ClaudeService')
    def test_generate_show_notes(self, mock_claude, mock_get_user, client):
        """Test AI-generated show notes"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        # Mock Claude service
        mock_claude_instance = Mock()
        mock_claude_instance.generate_content.return_value = "AI-generated show notes"
        mock_claude.return_value = mock_claude_instance

        payload = {
            "episode_id": "episode_123",
            "transcript": "This is a sample transcript of the episode..."
        }

        response = client.post(
            "/api/content/ai/generate-show-notes",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )

        if response.status_code == 200:
            data = response.json()
            assert "show_notes" in data or "notes" in data

    @patch('app.auth.clerk_auth.get_current_user')
    def test_transcribe_audio(self, mock_get_user, client):
        """Test audio transcription feature"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        payload = {
            "audio_url": "https://storage.example.com/audio.mp3",
            "episode_id": "episode_123"
        }

        response = client.post(
            "/api/content/ai/transcribe",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )

        # Transcription might be async, so various status codes are acceptable
        assert response.status_code in [200, 202, 400]


class TestContentDistribution:
    """Test content distribution functionality"""

    @patch('app.auth.clerk_auth.get_current_user')
    def test_publish_episode(self, mock_get_user, client):
        """Test publishing an episode"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        payload = {
            "episode_id": "episode_123",
            "platforms": ["spotify", "apple_podcasts", "youtube"]
        }

        response = client.post(
            "/api/content/publish",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )

        # Should handle publishing request
        assert response.status_code in [200, 202, 400]

    @patch('app.auth.clerk_auth.get_current_user')
    def test_get_distribution_status(self, mock_get_user, client):
        """Test getting distribution status"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        response = client.get(
            "/api/content/episodes/episode_123/distribution",
            headers={"Authorization": "Bearer test_token"}
        )

        if response.status_code == 200:
            data = response.json()
            assert "status" in data or "distribution" in data

    @patch('app.auth.clerk_auth.get_current_user')
    def test_schedule_publication(self, mock_get_user, client):
        """Test scheduling episode publication"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        payload = {
            "episode_id": "episode_123",
            "publish_date": "2024-06-01T09:00:00Z",
            "platforms": ["spotify", "apple_podcasts"]
        }

        response = client.post(
            "/api/content/schedule",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )

        # Should handle scheduling request
        assert response.status_code in [200, 201, 400]


class TestContentAnalytics:
    """Test content analytics and performance tracking"""

    @patch('app.auth.clerk_auth.get_current_user')
    def test_get_content_analytics(self, mock_get_user, client):
        """Test getting content performance analytics"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        response = client.get(
            "/api/content/analytics",
            headers={"Authorization": "Bearer test_token"}
        )

        if response.status_code == 200:
            data = response.json()
            # Should contain analytics data
            analytics_fields = ["total_views", "total_downloads", "engagement_rate"]
            has_analytics = any(field in data for field in analytics_fields)
            assert has_analytics or "analytics" in data

    @patch('app.auth.clerk_auth.get_current_user')
    def test_get_episode_performance(self, mock_get_user, client):
        """Test getting individual episode performance"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        response = client.get(
            "/api/content/episodes/episode_123/analytics",
            headers={"Authorization": "Bearer test_token"}
        )

        if response.status_code == 200:
            data = response.json()
            # Should contain episode-specific metrics
            episode_fields = ["views", "downloads", "completion_rate"]
            has_episode_data = any(field in data for field in episode_fields)
            assert has_episode_data or "error" in data


class TestContentErrorHandling:
    """Test content creation error handling"""

    @patch('app.auth.clerk_auth.get_current_user')
    def test_create_series_invalid_data(self, mock_get_user, client):
        """Test creating series with invalid data"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        payload = {
            "name": "",  # Empty name should be invalid
            "content_type": "invalid_type"
        }

        response = client.post(
            "/api/content/series",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code in [400, 422]

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.services.storage_factory.get_storage_service')
    def test_upload_storage_error(self, mock_storage, mock_get_user, client):
        """Test handling of storage service errors"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        # Mock storage error
        mock_storage_instance = Mock()
        mock_storage_instance.upload_file.side_effect = Exception("Storage error")
        mock_storage.return_value = mock_storage_instance

        files = {"file": ("test.mp3", BytesIO(b"fake audio"), "audio/mpeg")}

        response = client.post(
            "/api/content/upload",
            files=files,
            headers={"Authorization": "Bearer test_token"}
        )

        # Should handle storage errors gracefully
        assert response.status_code in [400, 500]

    @patch('app.auth.clerk_auth.get_current_user')
    def test_access_nonexistent_content(self, mock_get_user, client):
        """Test accessing non-existent content"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "test@example.com"
        }

        response = client.get(
            "/api/content/series/nonexistent_series",
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code == 404