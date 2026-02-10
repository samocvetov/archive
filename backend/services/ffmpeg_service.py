import os
import subprocess
import json
import asyncio
from pathlib import Path
from typing import Optional, Tuple
from config import settings

class FFmpegService:
    def __init__(self):
        self.ffmpeg_path = "ffmpeg"
        self.ffprobe_path = "ffprobe"
    
    async def get_video_info(self, filepath: str) -> dict:
        cmd = [
            self.ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            filepath
        ]
        
        try:
            # Run in thread pool to avoid asyncio subprocess issues on Windows
            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
        except subprocess.TimeoutExpired:
            raise Exception("FFprobe timeout")
        except Exception as e:
            raise Exception(f"FFprobe execution error: {str(e)}")
        
        if result.returncode != 0:
            raise Exception(f"FFprobe error: {result.stderr}")
        
        info = json.loads(result.stdout)
        
        duration = float(info['format']['duration'])
        video_stream = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
        
        return {
            'duration': duration,
            'width': video_stream['width'] if video_stream else None,
            'height': video_stream['height'] if video_stream else None,
            'fps': eval(video_stream['r_frame_rate']) if video_stream else None,
            'codec': video_stream['codec_name'] if video_stream else None
        }
    
    async def extract_fragment(
        self,
        input_path: str,
        output_path: str,
        start_time: float,
        end_time: float,
        quality: str = "high"
    ) -> str:
        duration = end_time - start_time
        
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-ss", str(start_time),
            "-i", input_path,
            "-t", str(duration),
            "-c", "copy",
            "-avoid_negative_ts", "1",
            output_path
        ]
        
        result = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        return output_path
    
    async def generate_thumbnail(
        self,
        input_path: str,
        output_path: str,
        timestamp: float = 1.0,
        width: int = 320,
        height: int = 180
    ) -> str:
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-ss", str(timestamp),
            "-i", input_path,
            "-vframes", "1",
            "-vf", f"scale={width}:{height}",
            "-update", "1",
            output_path
        ]
        
        result = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        return output_path
    
    async def concat_fragments(
        self,
        fragment_paths: list,
        output_path: str
    ) -> str:
        concat_file = "/tmp/concat_list.txt"
        with open(concat_file, "w") as f:
            for path in fragment_paths:
                f.write(f"file '{path}'\n")
        
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            output_path
        ]
        
        result = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        os.remove(concat_file)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        return output_path

ffmpeg_service = FFmpegService()
