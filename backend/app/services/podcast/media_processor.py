"""
Professional-grade media processing for self-hosted podcast platform
Handles audio/video processing, optimization, and distribution preparation
"""

import asyncio
import os
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import subprocess
import json
from dataclasses import dataclass
import hashlib
import aiofiles
import ffmpeg
import numpy as np
from PIL import Image
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class MediaFile:
    """Represents a media file being processed"""
    file_path: Path
    file_type: str  # audio, video
    format: str
    duration: float
    bitrate: int
    sample_rate: int
    channels: int
    resolution: Optional[Tuple[int, int]] = None


@dataclass
class ProcessedEpisode:
    """Represents a fully processed podcast episode"""
    episode_id: str
    original_file: str
    duration: float
    formats: Dict[str, str]  # format_name -> file_path
    metadata: Dict[str, Any]
    transcript_path: Optional[str] = None
    chapters_path: Optional[str] = None
    waveform_path: Optional[str] = None
    thumbnail_path: Optional[str] = None


class MediaProcessor:
    """
    Professional media processing pipeline for podcast content
    Eliminates need for external services like Transistor.fm
    """

    def __init__(self, storage_path: str = "/var/podcast/media"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Audio quality presets (podcast industry standards)
        self.audio_presets = {
            "high": {"bitrate": "256k", "sample_rate": 44100, "codec": "libmp3lame"},
            "standard": {"bitrate": "128k", "sample_rate": 44100, "codec": "libmp3lame"},
            "mobile": {"bitrate": "64k", "sample_rate": 22050, "codec": "libmp3lame"},
            "opus": {"bitrate": "128k", "sample_rate": 48000, "codec": "libopus"}
        }

        # Video quality presets
        self.video_presets = {
            "1080p": {"resolution": "1920x1080", "bitrate": "5000k", "fps": 30},
            "720p": {"resolution": "1280x720", "bitrate": "2500k", "fps": 30},
            "480p": {"resolution": "854x480", "bitrate": "1000k", "fps": 30},
            "360p": {"resolution": "640x360", "bitrate": "500k", "fps": 30}
        }

    async def process_episode(
        self,
        input_file: str,
        episode_id: str,
        episode_metadata: Dict[str, Any]
    ) -> ProcessedEpisode:
        """
        Complete episode processing pipeline
        """

        logger.info(f"Processing episode {episode_id}")

        # Analyze input file
        media_info = await self.analyze_media(input_file)

        # Create episode directory
        episode_dir = self.storage_path / episode_id
        episode_dir.mkdir(exist_ok=True)

        processed_formats = {}

        # Process audio
        if media_info.file_type in ["audio", "video"]:
            logger.info("Processing audio formats")

            # Enhance audio quality
            enhanced_audio = await self.enhance_audio(input_file, episode_dir / "enhanced.wav")

            # Create multiple bitrate versions
            for preset_name, preset_config in self.audio_presets.items():
                output_file = episode_dir / f"audio_{preset_name}.mp3"
                await self.encode_audio(enhanced_audio, output_file, preset_config)
                processed_formats[f"audio_{preset_name}"] = str(output_file)

            # Generate waveform visualization
            waveform_path = await self.generate_waveform(enhanced_audio, episode_dir / "waveform.png")

            # Clean up enhanced file
            enhanced_audio.unlink()

        # Process video if applicable
        if media_info.file_type == "video":
            logger.info("Processing video formats")

            for preset_name, preset_config in self.video_presets.items():
                output_file = episode_dir / f"video_{preset_name}.mp4"
                await self.encode_video(input_file, output_file, preset_config)
                processed_formats[f"video_{preset_name}"] = str(output_file)

            # Create HLS streaming version
            hls_path = await self.create_hls_stream(input_file, episode_dir / "hls")
            processed_formats["hls_playlist"] = str(hls_path)

            # Extract thumbnail
            thumbnail_path = await self.extract_thumbnail(input_file, episode_dir / "thumbnail.jpg")

        # Generate transcript using Whisper
        transcript_path = await self.generate_transcript(input_file, episode_dir / "transcript.vtt")

        # Generate chapter markers
        chapters_path = await self.generate_chapters(
            transcript_path,
            episode_dir / "chapters.json",
            media_info.duration
        )

        # Create promotional clips
        clips = await self.create_promotional_clips(input_file, episode_dir / "clips")
        for i, clip_path in enumerate(clips):
            processed_formats[f"clip_{i+1}"] = str(clip_path)

        logger.info(f"Episode {episode_id} processing complete")

        return ProcessedEpisode(
            episode_id=episode_id,
            original_file=input_file,
            duration=media_info.duration,
            formats=processed_formats,
            metadata={
                **episode_metadata,
                "processing_date": str(datetime.now()),
                "file_sizes": {k: os.path.getsize(v) for k, v in processed_formats.items()}
            },
            transcript_path=str(transcript_path) if transcript_path else None,
            chapters_path=str(chapters_path) if chapters_path else None,
            waveform_path=str(waveform_path) if 'waveform_path' in locals() else None,
            thumbnail_path=str(thumbnail_path) if 'thumbnail_path' in locals() else None
        )

    async def analyze_media(self, input_file: str) -> MediaFile:
        """
        Analyze media file properties using ffprobe
        """

        try:
            probe = ffmpeg.probe(input_file)

            # Extract basic info
            format_info = probe['format']
            duration = float(format_info['duration'])
            bitrate = int(format_info.get('bit_rate', 0))

            # Find audio and video streams
            audio_stream = next(
                (s for s in probe['streams'] if s['codec_type'] == 'audio'),
                None
            )
            video_stream = next(
                (s for s in probe['streams'] if s['codec_type'] == 'video'),
                None
            )

            file_type = "video" if video_stream else "audio"

            media_info = MediaFile(
                file_path=Path(input_file),
                file_type=file_type,
                format=format_info['format_name'],
                duration=duration,
                bitrate=bitrate,
                sample_rate=int(audio_stream['sample_rate']) if audio_stream else 0,
                channels=int(audio_stream['channels']) if audio_stream else 0,
                resolution=(
                    int(video_stream['width']),
                    int(video_stream['height'])
                ) if video_stream else None
            )

            return media_info

        except ffmpeg.Error as e:
            logger.error(f"Error analyzing media file: {e}")
            raise

    async def enhance_audio(self, input_file: str, output_file: Path) -> Path:
        """
        Enhance audio quality using FFmpeg filters
        Professional podcast audio processing
        """

        logger.info("Enhancing audio quality")

        try:
            # Build filter chain for podcast optimization
            filters = [
                # Normalize to -16 LUFS (podcast standard)
                "loudnorm=I=-16:TP=-1.5:LRA=11",

                # High-pass filter to remove rumble
                "highpass=f=80",

                # De-esser to reduce sibilance
                "deesser=i=0.4",

                # Compression for consistent volume
                "compand=0.005,0.1:0.5:0.95,1.0:-12/-12,-6/-3,0/-0.5",

                # EQ optimization for voice
                "equalizer=f=100:t=h:width=200:g=-2,"
                "equalizer=f=3000:t=q:width=0.5:g=3,"
                "equalizer=f=6000:t=h:width=2000:g=-3",

                # Noise gate to remove background noise during silence
                "gate=threshold=-40dB:ratio=10:attack=0.01:release=0.1"
            ]

            # Apply filters
            stream = ffmpeg.input(input_file)
            stream = ffmpeg.filter(stream, 'aformat', 'sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo')

            for filter_cmd in filters:
                stream = ffmpeg.filter(stream, 'aeval', filter_cmd)

            stream = ffmpeg.output(stream, str(output_file), acodec='pcm_s16le')

            # Run ffmpeg command
            await self._run_ffmpeg(stream, "Audio enhancement")

            return output_file

        except Exception as e:
            logger.error(f"Audio enhancement failed: {e}")
            raise

    async def encode_audio(self, input_file: Path, output_file: Path, preset: Dict[str, Any]):
        """
        Encode audio file with specific preset
        """

        logger.info(f"Encoding audio: {preset}")

        try:
            stream = ffmpeg.input(str(input_file))
            stream = ffmpeg.output(
                stream,
                str(output_file),
                acodec=preset['codec'],
                audio_bitrate=preset['bitrate'],
                ar=preset['sample_rate']
            )

            await self._run_ffmpeg(stream, f"Audio encoding ({preset['bitrate']})")

        except Exception as e:
            logger.error(f"Audio encoding failed: {e}")
            raise

    async def encode_video(self, input_file: str, output_file: Path, preset: Dict[str, Any]):
        """
        Encode video file with specific preset
        """

        logger.info(f"Encoding video: {preset}")

        try:
            stream = ffmpeg.input(input_file)
            stream = ffmpeg.output(
                stream,
                str(output_file),
                vcodec='libx264',
                preset='slow',  # Better compression
                crf=23,  # Quality factor
                video_bitrate=preset['bitrate'],
                s=preset['resolution'],
                r=preset['fps'],
                acodec='aac',
                audio_bitrate='128k'
            )

            await self._run_ffmpeg(stream, f"Video encoding ({preset['resolution']})")

        except Exception as e:
            logger.error(f"Video encoding failed: {e}")
            raise

    async def create_hls_stream(self, input_file: str, output_dir: Path) -> Path:
        """
        Create HLS streaming version for adaptive bitrate
        """

        logger.info("Creating HLS stream")
        output_dir.mkdir(exist_ok=True)

        playlist_file = output_dir / "playlist.m3u8"

        try:
            stream = ffmpeg.input(input_file)
            stream = ffmpeg.output(
                stream,
                str(output_dir / "segment_%03d.ts"),
                format='hls',
                hls_time=10,
                hls_playlist_type='vod',
                hls_segment_filename=str(output_dir / "segment_%03d.ts"),
                vcodec='libx264',
                acodec='aac'
            )

            await self._run_ffmpeg(stream, "HLS stream creation")

            return playlist_file

        except Exception as e:
            logger.error(f"HLS creation failed: {e}")
            raise

    async def generate_waveform(self, audio_file: Path, output_file: Path) -> Path:
        """
        Generate waveform visualization
        """

        logger.info("Generating waveform")

        try:
            # Use ffmpeg to generate waveform
            stream = ffmpeg.input(str(audio_file))
            stream = ffmpeg.filter(stream, 'showwavespic', s='1920x1080', colors='#007AFF')
            stream = ffmpeg.output(stream, str(output_file), vframes=1)

            await self._run_ffmpeg(stream, "Waveform generation")

            return output_file

        except Exception as e:
            logger.error(f"Waveform generation failed: {e}")
            raise

    async def extract_thumbnail(self, video_file: str, output_file: Path, time: float = 10) -> Path:
        """
        Extract thumbnail from video
        """

        logger.info("Extracting thumbnail")

        try:
            stream = ffmpeg.input(video_file, ss=time)
            stream = ffmpeg.filter(stream, 'scale', 1920, 1080)
            stream = ffmpeg.output(stream, str(output_file), vframes=1)

            await self._run_ffmpeg(stream, "Thumbnail extraction")

            return output_file

        except Exception as e:
            logger.error(f"Thumbnail extraction failed: {e}")
            raise

    async def generate_transcript(self, media_file: str, output_file: Path) -> Path:
        """
        Generate transcript using Whisper AI (self-hosted)
        """

        logger.info("Generating transcript with Whisper")

        try:
            # Use Whisper for transcription (requires whisper to be installed)
            # This would integrate with self-hosted Whisper model
            import whisper

            model = whisper.load_model("base")  # Can use "large" for better accuracy
            result = model.transcribe(media_file)

            # Convert to WebVTT format
            vtt_content = "WEBVTT\n\n"

            for segment in result["segments"]:
                start = self._seconds_to_vtt_time(segment["start"])
                end = self._seconds_to_vtt_time(segment["end"])
                text = segment["text"].strip()

                vtt_content += f"{start} --> {end}\n{text}\n\n"

            # Save transcript
            async with aiofiles.open(output_file, 'w') as f:
                await f.write(vtt_content)

            return output_file

        except Exception as e:
            logger.error(f"Transcript generation failed: {e}")
            # Return None if transcription fails (non-critical)
            return None

    async def generate_chapters(
        self,
        transcript_path: Optional[Path],
        output_file: Path,
        duration: float
    ) -> Optional[Path]:
        """
        Generate chapter markers from transcript
        """

        if not transcript_path:
            return None

        logger.info("Generating chapter markers")

        try:
            # Simple chapter generation based on transcript
            # In production, use AI to identify topic changes

            chapters = []
            chapter_interval = 300  # 5 minutes

            for i in range(0, int(duration), chapter_interval):
                chapters.append({
                    "start": i,
                    "title": f"Chapter {i // chapter_interval + 1}",
                    "url": ""  # Can add timestamps
                })

            # Save chapters
            async with aiofiles.open(output_file, 'w') as f:
                await f.write(json.dumps(chapters, indent=2))

            return output_file

        except Exception as e:
            logger.error(f"Chapter generation failed: {e}")
            return None

    async def create_promotional_clips(
        self,
        media_file: str,
        output_dir: Path,
        num_clips: int = 3
    ) -> List[Path]:
        """
        Create short promotional clips for social media
        """

        logger.info(f"Creating {num_clips} promotional clips")
        output_dir.mkdir(exist_ok=True)

        clips = []

        try:
            # Analyze media to find interesting segments
            media_info = await self.analyze_media(media_file)
            duration = media_info.duration

            # Create clips at different points
            clip_points = [
                duration * 0.2,  # 20% through
                duration * 0.5,  # Middle
                duration * 0.75  # 75% through
            ]

            for i, start_time in enumerate(clip_points[:num_clips]):
                output_file = output_dir / f"clip_{i+1}.mp4"

                # Create 60-second clip
                stream = ffmpeg.input(media_file, ss=start_time, t=60)

                # Add fade in/out
                stream = ffmpeg.filter(stream, 'fade', type='in', duration=1)
                stream = ffmpeg.filter(stream, 'fade', type='out', duration=1, start_time=59)

                # Optimize for social media (vertical format)
                if media_info.file_type == "video":
                    stream = ffmpeg.filter(stream, 'scale', 1080, 1920)

                stream = ffmpeg.output(
                    stream,
                    str(output_file),
                    vcodec='libx264',
                    preset='fast',
                    crf=23,
                    acodec='aac'
                )

                await self._run_ffmpeg(stream, f"Clip {i+1} creation")
                clips.append(output_file)

            return clips

        except Exception as e:
            logger.error(f"Clip creation failed: {e}")
            return []

    async def _run_ffmpeg(self, stream, description: str):
        """
        Run ffmpeg command asynchronously
        """

        try:
            cmd = ffmpeg.compile(stream)
            logger.info(f"Running: {description}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise Exception(f"FFmpeg failed: {stderr.decode()}")

        except Exception as e:
            logger.error(f"FFmpeg execution failed: {e}")
            raise

    def _seconds_to_vtt_time(self, seconds: float) -> str:
        """
        Convert seconds to WebVTT timestamp format
        """

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60

        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

    async def calculate_storage_cost(self, episode: ProcessedEpisode) -> Dict[str, Any]:
        """
        Calculate storage costs for self-hosted vs external
        """

        total_size = sum(
            os.path.getsize(path) for path in episode.formats.values()
        )

        # Convert to GB
        size_gb = total_size / (1024 ** 3)

        # Self-hosted costs (example: Wasabi S3)
        self_hosted_cost = size_gb * 0.0059  # $0.0059 per GB/month

        # External service costs (example: Transistor.fm)
        external_cost = 99  # $99/month for unlimited

        return {
            "episode_size_gb": size_gb,
            "self_hosted_monthly": self_hosted_cost,
            "external_monthly": external_cost,
            "monthly_savings": external_cost - self_hosted_cost,
            "annual_savings": (external_cost - self_hosted_cost) * 12
        }


# Additional imports
from datetime import datetime

# Global processor instance
media_processor = MediaProcessor()