from manim import *
import numpy as np
import scipy.signal
import scipy
import librosa

class AudioVisualizer(VDict):

    def __init__(self, audio: np.ndarray, sr: int, n_bands: int):
        w = 1/(n_bands*1.5)
        bars = VGroup(
            RoundedRectangle(w*.1, height=1, width=w, color=ORANGE, stroke_width=1., fill_opacity=1.)
            for _ in range(0, n_bands)
        ).arrange(RIGHT, w/2)

        background = SurroundingRectangle(bars, color='#13294B', buff=SMALL_BUFF, corner_radius=SMALL_BUFF*0.9, fill_opacity=1.)

        for r in bars:
            r.stretch_to_fit_height(w)

        bars.set_z_index(background.z_index+1)

        tracker = ValueTracker(0.)

        self.tracker = tracker

        super().__init__({
            'bars': bars,
            'background': background,
        })

        self.original_color = ManimColor('#13294B')

        n_fft = 1024

        f, t, stft = scipy.signal.stft(audio, sr, nperseg=n_fft, noverlap=n_fft//2)

        mag = abs(stft)

        fbank = librosa.filters.mel(sr=sr, n_fft=n_fft, n_mels=n_bands)

        mel = fbank @ mag

        # mel = 20 * np.log10(mel + 1e-12)
        mel = mel ** 0.25

        mel /= mel.max()
        mel = np.maximum(mel, 0.01)
        self.mel = mel
        self.length = mel.shape[-1]
        from matplotlib import pyplot as plt
        plt.pcolormesh(mel)
        plt.colorbar()
        plt.savefig('mel.png')
        plt.close()

        self.duration_in_seconds = len(audio) / sr

        self.add_updater(self._updater)

    def _updater(self, m):
        t = self.tracker.get_value()
        assert t <= 1.

        bg: VMobject = m['background']

        time = self.duration_in_seconds * t

        cutoff = 0.5
        if time < cutoff:
            k = time/cutoff
        elif time > self.duration_in_seconds-cutoff:
            k = (self.duration_in_seconds-time)/cutoff
        else:
            k = 1

        v = np.sin(np.pi*k/2)#**(1/2)

        color = interpolate_color(self.original_color, LIGHT_GREY, (1-v)*.5)
        bg.set_stroke(color)
        bg.set_fill(color)
        bg.set_sheen(0.2*v)
        bg.set_sheen_direction(LEFT).rotate_sheen_direction(-np.pi*t, OUT)


        # if t > 0 and t < 1:
        #     bg.set_opacity(0.75+0.25*v)
        #     # bg.set_stroke(opacity=0.5+0.5*v)
        #     # bg.set_stroke(opacity=0.)



        i = int(t*(self.length-1))
        values = self.mel[:, i]
        for v, r in zip(values, m['bars']):
            h = v*m['background'].height*0.9
            if t == 0. or t == 1.:
                h = 0.01
            r.stretch_to_fit_height(h)
            # r.stretch_to_fit_height(v*m['background'].height*0.9)
        return m

    def play(self):
        return AnimationGroup(
            self.tracker.animate.set_value(1.).build().set_rate_func(rate_functions.linear),
            run_time=self.duration_in_seconds
        )


    @classmethod
    def from_wavfile(cls, audio_file, n_bands: int):
        sr, audio = scipy.io.wavfile.read(audio_file)
        audio: np.ndarray = audio.T # scipy -_-
        audio = audio.astype(float) / audio.max()
        if audio.ndim > 1:
            audio = audio.mean(0)
        # audio = audio[:int(sr)]
        return cls(audio, sr, n_bands)

