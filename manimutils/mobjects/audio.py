from manim import *
import numpy as np
from copy import deepcopy, copy
import scipy
import scipy.io.wavfile
import scipy.signal
import scipy.fft
import scipy.ndimage
import torch

from matplotlib import pyplot as plt
from matplotlib.colors import PowerNorm, LinearSegmentedColormap
from matplotlib.backends.backend_agg import FigureCanvasAgg
# import tqdm

from manimutils.mobjects.grid import Grid
from manimutils.animations import *

class Waveform(VDict):

    def __init__(self, audio, sr, normalize=True, frame_size=None, hop_size=None, axes_kwargs={}, curve_kwargs={}):
        """Takes `audio` in `CxT` or `T` format""" \
        """and sample rate `sr` and constructs a Waveform mobject"""
        if frame_size is None:
            frame_size = sr // 200 # 5ms
        if hop_size is None:
            hop_size = frame_size // 16
        if isinstance(audio, torch.Tensor):
            audio = audio.cpu().detach().numpy()
        if len(audio.shape) == 2:
            audio = audio.mean(0)
        if normalize:
            audio = audio / abs(audio).max()

        self.axes_kwargs = axes_kwargs
        self.curve_kwargs = curve_kwargs

        # print(frame_size, hop_size)

        # b, a = scipy.signal.butter(8, sr//8, fs=sr)
        # audio = scipy.signal.lfilter(b, a, audio)
        downsample_factor = 8
        # audio = scipy.signal.resample_poly(audio, up=1, down=downsample_factor)

        # print(audio.shape)

        peaks, _ = scipy.signal.find_peaks(abs(audio), distance=64)
        upper_contour = np.interp(
            np.arange(0, audio.shape[-1]//downsample_factor),
            peaks/downsample_factor,
            abs(audio)[peaks]
        )
        # upper_contour = scipy.ndimage.gaussian_filter1d(audio, sigma=1)
        # upper_contour = scipy.ndimage.uniform_filter1d(audio, 40)
        # upper_contour = scipy.signal.resample_poly(upper_contour, up=1, down=downsample_factor)

        # upper_contour = np.lib.stride_tricks.sliding_window_view(
        #     np.where(audio>0, audio, 0),
        #     frame_size//downsample_factor,
        #     axis=0,
        # )[::1].max(1)

        # upper_contour = 
        # upper_contour = abs(audio)
        # for i in range(0, 4):
        #     upper_contour = np.lib.stride_tricks.sliding_window_view(
        #         np.where(upper_contour>0, upper_contour, 0),
        #         4,
        #         axis=0,
        #     )[::2].mean(1)
        # )[::hop_size].max(1)

        print(upper_contour.shape)
        # upper_contour = scipy.signal.savgol_filter(audio, 21, 2)

        axes = Axes(
            x_range=[0, upper_contour.shape[-1]-1],
            y_range=[-1, 1, 0.25],
            axis_config={'include_tip': False},
            x_axis_config={'include_ticks': False},
            **axes_kwargs
        )

        upper_curve = axes.plot(
            (lambda x: upper_contour[round(x)]),
            **curve_kwargs
        )
        lower_curve = axes.plot(
            (lambda x: -upper_contour[round(x)]),
            **curve_kwargs
        )
        if 'color' in curve_kwargs:
            color=curve_kwargs['color']
        else:
            color=upper_curve.get_color()
        area = axes.get_area(upper_curve, bounded_graph=lower_curve, color=color)
        curve = VDict({
            'upper': upper_curve,
            'lower': lower_curve,
            'area': area
        })

        x_label = axes.get_x_axis_label('Time', UR, UR)
        x_label.shift(0.5*RIGHT)
        y_label = axes.get_y_axis_label('Amplitude')
        labels = VGroup(x_label, y_label)
        axes = VDict({
            'labels': labels,
            'axes': axes
        })

        super().__init__({
            'axes': axes,
            'curve': curve
        })
        self.audio = audio
        self.sr = sr

    @classmethod
    def from_wavfile(cls, file):
        sr, audio = scipy.io.wavfile.read(file)
        audio = audio.T # scipy -_-
        return cls(audio, sr)

    @override_animation(Write)
    def _write(self, **kwargs):
        axes_kwargs = copy(kwargs)
        curve_kwargs = copy(kwargs)
        if 'run_time' in kwargs:
            axes_kwargs['run_time'] = kwargs['run_time'] / 5
            curve_kwargs['run_time'] = kwargs['run_time'] / 5 * 4
        return AnimationGroup(
            Write(self['axes'], **axes_kwargs),
            AnimationGroup(
                AnimationGroup(
                    Write(self['curve']['upper']),
                    Write(self['curve']['lower']),
                    **curve_kwargs
                ),
                FadeIn(self['curve']['area']),
                lag_ratio=0.5,
            ),
            lag_ratio=1.,
            **kwargs
        )

    def spectrogram(
        self,
        n_fft,
        window_size,
        hop_size,
        **kwargs
    ):
        return Spectrogram.from_audio(
            audio=self.audio,
            sr=self.sr,
            n_fft=n_fft,
            window_size=window_size,
            hop_size=hop_size,
            **kwargs
        )

    @override_animate(spectrogram)
    def animate_spectrogram(
        self,
        n_fft,
        window_size,
        hop_size,
        anim_args,
        **kwargs
    ):
        spec = self.spectrogram(
            n_fft=n_fft,
            window_size=window_size,
            hop_size=hop_size,
            **kwargs
        )
        animations = []
        previous_residual_waveform = self
        for i in range(0, spec.spec.shape[0]):
            filtered = spec.spec.copy()
            filtered[:i] = 0
            filtered[i+1:] = 0
            _, filtered_audio = scipy.signal.istft(
                filtered,
                fs=self.sr,
                nperseg=window_size,
                nfft=n_fft,
                noverlap=window_size-hop_size,
                # input_onesided=True,
                # boundary=None
            )


            filtered_waveform = Waveform(filtered_audio, self.sr, normalize=False, curve_kwargs=self.curve_kwargs) # TODO copy styling?
            scalefactor = self['axes'].get_width() / filtered_waveform['axes'].get_width()
            filtered_waveform.scale(scalefactor)
            filtered_waveform.move_to(self)

            residual = spec.spec.copy()
            residual[:i+1] = 0
            _, residual_audio = scipy.signal.istft(
                residual,
                fs=self.sr,
                nperseg=window_size,
                nfft=n_fft,
                noverlap=window_size-hop_size,
            )
            residual_waveform = Waveform(residual_audio, self.sr, normalize=False, curve_kwargs=self.curve_kwargs)
            residual_waveform.scale(scalefactor)
            residual_waveform.move_to(self)

            animations.append(AnimationGroup(
                ReplacementTransform(previous_residual_waveform['curve'], residual_waveform['curve']),
                TransformFromCopy(previous_residual_waveform['curve'], filtered_waveform['curve'])
            ))
            previous_residual_waveform = residual_waveform
            if i > 2:
                break

        # spec = Circle(4)
        # spec.move_to(self)
        # self['curve'].align_points(spec)
        # if 'lag_ratio' not in anim_args:
        # anim_args['lag_ratio'] = 1
        # return AnimationGroup(
        #     FadeOut(self['axes']),
        #     # AnimationGroup(
        #     #     Transform(self['curve'], filtered_waveform['curve'], **anim_args)
        #     # )
        #     *animations,
        #     **anim_args
        # )
        return [FadeOut(self['axes'])] + animations

# class Spectrogram(Grid):

#     def __init__(self, spec, square_size=0.05, powernorm=0.5, low_color=WHITE, high_color=ManimColor.from_rgb((0., 0.15, 0.4))):
#         """Takes a spectrogram in FxT format"""
#         if isinstance(spec, torch.Tensor):
#             spec = spec.cpu().detach().numpy()
#         self.spec = spec
#         spec = spec[::-1]

#         spec = spec ** powernorm

#         magspec = abs(spec)

#         N = spec.shape[0]
#         M = spec.shape[1]
#         colors = np.empty((spec.shape[0], spec.shape[1]), dtype=object)
#         for i in range(N):
#             for j in range(M):
#                 colors[i, j] = (1-magspec[i, j]) * low_color + magspec[i, j] * high_color
#                 # colors[i, j] = high_color

#         super().__init__(N, M, square_size=square_size)

#         for i in range(N):
#             for j in range(M):
#                 self[i, j].set_fill(colors[i, j], 1)
#                 self[i, j].set_color(colors[i, j])

#     @classmethod
#     def from_audio(
#         cls,
#         audio,
#         sr,
#         n_fft,
#         window_size,
#         hop_size,
#         powernorm=0.5,
#         normalize=True,
#         square_size=0.05,
#         low_color=WHITE,
#         high_color=ManimColor.from_rgb((0., 0.15, 0.4))
#     ):
#         if isinstance(audio, torch.Tensor):
#             audio = audio.cpu().detach().numpy()
#         if len(audio.shape) == 2:
#             audio = audio.mean(0)
#         if normalize:
#             audio = audio / abs(audio).max()
#         _, _, spec = scipy.signal.stft(
#             audio,
#             sr,
#             nperseg=window_size,
#             noverlap=window_size-hop_size,
#             nfft=n_fft,
#             # boundary=None,
#             # padded=False,
#         )
#         return cls(
#             spec,
#             square_size=square_size,
#             low_color=low_color,
#             high_color=high_color,
#         )

#     @classmethod
#     def from_wavfile(cls, file, n_fft, window_size, hop_size, normalize=True):
#         sr, audio = scipy.io.wavfile.read(file)
#         audio = audio.T # scipy -_-
#         return cls.from_audio(audio, sr, n_fft, window_size, hop_size, normalize=normalize)

class Spectrogram(ImageMobject):

    def __init__(self, time, freq, spec, aspect_ratio=4/3, powernorm=0.5, low_color=WHITE, high_color=ManimColor.from_rgb((0., 0.15, 0.4)), scale_y=True):
        """Takes a spectrogram in FxT format"""
        if isinstance(spec, torch.Tensor):
            spec = spec.cpu().detach().numpy()
        self.spec = spec
        # spec = spec[::-1]

        # spec = spec ** powernorm

        magspec = abs(spec)

        # N = spec.shape[0]
        # M = spec.shape[1]
        # colors = np.empty((N, M, 4), np.uint8)
        # for i in range(N):
        #     for j in range(M):
        #         value = magspec[i, j]
        #         c: ManimColor = (1-value) * low_color + value * high_color
        #         colors[i, j, :] = c.to_int_rgba()

        cmap = LinearSegmentedColormap.from_list(
            'WhBu',
            [
                low_color.to_rgba(),
                high_color.to_rgba()
            ],
            N=256,
            gamma=1.0
        )

        # fig = plt.figure(frameon=False)
        # ax = fig.add_axes((0.1,0.1,0.9,0.9))
        # # ax = fig.add_axes()
        # ax.set_axis_off()
        fig, ax = plt.subplots()
        fig.set_size_inches(4*aspect_ratio, 4)

        # fig.patch.set_facecolor('black')
        # ax.set_facecolor('black')
        fig.patch.set_alpha(0)       # Transparent figure background
        ax.set_facecolor('none')     # Transparent axes background

        # Set axes spines, ticks, and labels to white
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')
        ax.title.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')

        if not scale_y:
            freq_arg = np.arange(0, len(freq))
        else:
            freq_arg = freq
        ax.pcolormesh(time, freq_arg, magspec, cmap=cmap, norm=PowerNorm(gamma=powernorm))

        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Frequency (Hz)')

        if not scale_y:
            indices = np.linspace(0, len(freq)-1, num=10, endpoint=True, dtype=int)
            ax.set_yticks(indices, np.round(freq[indices]).astype(int))
            plt.savefig('mel_output.png')

        fig.tight_layout(pad=0)

        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        width, height = canvas.get_width_height()
        argb = np.frombuffer(canvas.tostring_argb(), dtype=np.uint8).reshape((height, width, 4))
        rgba = argb[:, :, [1, 2, 3, 0]]
        plt.close(fig)

        super().__init__(rgba)

    @classmethod
    def from_audio(
        cls,
        audio,
        sr,
        n_fft,
        window_size,
        hop_size,
        powernorm=0.5,
        normalize=True,
        # square_size=0.05,
        low_color=WHITE,
        high_color=ManimColor.from_rgb((0., 0.15, 0.4))
    ):
        if isinstance(audio, torch.Tensor):
            audio = audio.cpu().detach().numpy()
        if len(audio.shape) == 2:
            audio = audio.mean(0)
        if normalize:
            audio = audio / abs(audio).max()
        _, _, spec = scipy.signal.stft(
            audio,
            sr,
            nperseg=window_size,
            noverlap=window_size-hop_size,
            nfft=n_fft,
            # boundary=None,
            # padded=False,
        )
        return cls(
            spec,
            # square_size=square_size,
            low_color=low_color,
            high_color=high_color,
            powernorm=powernorm,
        )

    @classmethod
    def from_wavfile(cls, file, n_fft, window_size, hop_size, normalize=True):
        sr, audio = scipy.io.wavfile.read(file)
        audio = audio.T # scipy -_-
        return cls.from_audio(audio, sr, n_fft, window_size, hop_size, normalize=normalize)