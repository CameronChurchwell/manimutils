import os
from pathlib import Path

from manim import *
import manim
from manim_slides import Slide
from manim_slides.slide.animation import Wipe

import scipy
import scipy.io

from tqdm import tqdm
import shutil
import platform

import moviepy as mpy

from manim_slides.config import BaseSlideConfig, PresentationConfig, PreSlideConfig, SlideConfig
from manim_slides.utils import concatenate_video_files, merge_basenames, reverse_video_file

class AudioSlide(Slide):

    def next_slide(self, *args, audio_file=None, **kwargs):
        super().next_slide(*args, **kwargs)
        # you can't stop me
        # I will monkey patch you
        if audio_file is not None:
            self._slides[-1].__dict__['audio_file'] = audio_file

    def _save_slides(  # noqa: C901
        self,
        use_cache: bool = True,
        flush_cache: bool = False,
        skip_reversing: bool = False,
    ) -> None:
        """
        Save slides, optionally using cached files.

        .. warning:
            Caching files only work with Manim.
        """
        self._add_last_slide()

        files_folder: Path = self._output_folder / "files"

        scene_name = str(self)
        scene_files_folder = files_folder / scene_name

        if flush_cache and scene_files_folder.exists():
            shutil.rmtree(scene_files_folder)

        scene_files_folder.mkdir(parents=True, exist_ok=True)

        files: list[Path] = self._partial_movie_files

        # We must filter slides that end before the animation offset
        if offset := self._start_at_animation_number:
            self._slides = [
                slide for slide in self._slides if slide.end_animation > offset
            ]
            for slide in self._slides:
                slide.start_animation = max(0, slide.start_animation - offset)
                slide.end_animation -= offset

        slides: list[SlideConfig] = []

        for pre_slide_config in tqdm(
            self._slides,
            desc=f"Concatenating animations to '{scene_files_folder}' and generating reversed animations",
            leave=self._leave_progress_bar,
            ascii=True if platform.system() == "Windows" else None,
            disable=not self._show_progress_bar,
            unit=" slides",
        ):
            if pre_slide_config.skip_animations:
                continue
            if pre_slide_config.src:
                slide_files = [pre_slide_config.src]
            else:
                slide_files = files[pre_slide_config.slides_slice]

            try:
                file = merge_basenames(slide_files)
            except ValueError as e:
                raise ValueError(
                    f"Failed to merge basenames of files for slide: {pre_slide_config!r}"
                ) from e
            dst_file = scene_files_folder / file.name
            rev_file = scene_files_folder / f"{file.stem}_reversed{file.suffix}"

            # We only concat animations if it was not present
            if not use_cache or not dst_file.exists() or hasattr(pre_slide_config, 'audio_file'):
                concatenate_video_files(slide_files, dst_file)

            if hasattr(pre_slide_config, 'audio_file'):
                video = mpy.VideoFileClip(dst_file)
                sr, _audio = scipy.io.wavfile.read(pre_slide_config.audio_file)
                sr = int(sr)
                if len(_audio.shape) == 1:
                    _audio = _audio[..., None]
                    _audio = np.tile(_audio, (1, 2))
                _audio = _audio.astype(np.float32) / abs(_audio).max()
                audio = mpy.AudioArrayClip(_audio, fps=sr)
                bed = mpy.AudioClip(lambda t: np.array([0.0, 0.0]), duration=video.duration, fps=44100)
                audio = mpy.CompositeAudioClip([bed, audio.with_start(0)]).with_duration(video.duration)

                video: mpy.VideoFileClip = video.with_audio(audio)
                video.write_videofile(dst_file.with_suffix('.tmp.mp4'), fps=video.fps, audio=True, audio_fps=sr)

                os.replace(dst_file.with_suffix('.tmp.mp4'), dst_file)


            # We only reverse video if it was not present
            if not use_cache or not rev_file.exists():
                if skip_reversing:
                    rev_file = dst_file
                else:
                    reverse_video_file(
                        dst_file,
                        rev_file,
                        max_segment_duration=self.max_duration_before_split_reverse,
                        num_processes=self.num_processes,
                        leave=self._leave_progress_bar,
                        ascii=True if platform.system() == "Windows" else None,
                        disable=not self._show_progress_bar,
                    )

            slides.append(
                SlideConfig.from_pre_slide_config_and_files(
                    pre_slide_config, dst_file, rev_file
                )
            )

        logger.info(
            f"Generated {len(slides)} slides to '{scene_files_folder.absolute()}'"
        )

        slide_path = self._output_folder / f"{scene_name}.json"

        PresentationConfig(
            slides=slides,
            resolution=self._resolution,
            background_color=self._background_color,
        ).to_file(slide_path)

        logger.info(
            f"Slide '{scene_name}' configuration written in '{slide_path.absolute()}'"
        )