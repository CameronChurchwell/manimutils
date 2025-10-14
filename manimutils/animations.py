from manim import *
from manimutils.mobjects import *
from typing import Callable, Sequence

# TODO there has to be a better way to do this...
class IndicationTransform(Transform):

    def __init__(
        self,
        mobject: Mobject | None,
        target_mobject: Mobject | None = None,
        scale_factor: float = 1.1,
        path_func = None,
        path_arc: float = 0,
        path_arc_axis: np.ndarray = OUT,
        path_arc_centers: np.ndarray = None,
        replace_mobject_with_target_in_scene: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(
            mobject,
            target_mobject,
            path_func,
            path_arc,
            path_arc_axis,
            path_arc_centers,
            replace_mobject_with_target_in_scene,
            **kwargs
        )
        self.indication_copy = mobject.copy().scale(scale_factor)

    def interpolate_mobject(self, alpha: float) -> None:
        """Interpolates the mobject of the :class:`Animation` based on alpha value.

        Parameters
        ----------
        alpha
            A float between 0 and 1 expressing the ratio to which the animation
            is completed. For example, alpha-values of 0, 0.5, and 1 correspond
            to the animation being completed 0%, 50%, and 100%, respectively.
        """
        tc = self.target_copy
        s = self.starting_mobject
        if alpha < 0.5:
            self.starting_mobject = s
            self.target_copy = self.indication_copy
            alpha = alpha * 2
        else:
            self.starting_mobject = self.indication_copy
            self.target_copy = tc
            alpha = (alpha - 0.5) * 2
        retval = super().interpolate_mobject(alpha)
        self.target_copy = tc
        self.starting_mobject = s
        return retval

def TransformSubmobjects(first: Mobject, second: Mobject):
    assert len(first.submobjects) == len(second.submobjects)
    return AnimationGroup(
        *[Transform(f, s) for f, s in zip(first.submobjects, second.submobjects)]
    )

def ReplacementTransformSubmobjects(first: Mobject, second: Mobject):
    assert len(first.submobjects) == len(second.submobjects)
    return AnimationGroup(
        *[ReplacementTransform(f, s) for f, s in zip(first.submobjects, second.submobjects)]
    )

# TODO This animation is... dumb. You don't need this. I should remove it at some point
class TransformMatchingTexInOrder(TransformMatchingTex):
    def get_shape_map(self, mobject: Mobject) -> dict:
        shape_map = {}
        for i, sm in enumerate(self.get_mobject_parts(mobject)):
            key = i
            if key not in shape_map:
                shape_map[key] = VGroup()
            shape_map[key].add(sm)
        return shape_map

class TrueReplacementTransform(ReplacementTransform):
    def begin(self) -> None:
        # Use a copy of target_mobject for the align_data
        # call so that the actual target_mobject stays
        # preserved.
        self.target_mobject = self.create_target()
        self.target_copy = self.target_mobject
        # Note, this potentially changes the structure
        # of both mobject and target_mobject
        self.mobject.align_data(self.target_copy)
        self.starting_mobject = self.mobject
        if self.suspend_mobject_updating:
            # All calls to self.mobject's internal updaters
            # during the animation, either from this Animation
            # or from the surrounding scene, should do nothing.
            # It is, however, okay and desirable to call
            # the internal updaters of self.starting_mobject,
            # or any others among self.get_all_mobjects()
            self.mobject.suspend_updating()
    def is_introducer(self):
        return True

class STFT(Succession):
    def __init__(self, wave: Waveform, spec: Spectrogram, **kwargs):
        boundary_rectangle = Rectangle(
            color=wave['curve']['upper'].get_color(),
            height=spec.height,
            width=spec.width
        )
        boundary_rectangle.move_to(spec)
        upper_lower = VDict({
            'upper': wave['curve']['upper'],
            'lower': wave['curve']['lower']
        })
        super().__init__(
            AnimationGroup(
                FadeOut(wave['curve']['area']),
                Transform(upper_lower, boundary_rectangle),
            ),
            AnimationGroup(
                FadeOut(upper_lower),
                FadeIn(spec),
            )
        )

    # def interpolate_mobject(self, alpha: float):


class WriteOutline(Write):

    def interpolate_submobject(
        self,
        submobject: Mobject,
        starting_submobject: Mobject,
        outline,
        alpha: float,
    ) -> None:  # Fixme: not matching the parent class? What is outline doing here?
        # index, subalpha = integer_interpolate(0, 2, alpha)
        # if index == 0:
        submobject.pointwise_become_partial(outline, 0, alpha)
        submobject.match_style(outline)
        # else:
        #     submobject.interpolate(outline, starting_submobject, subalpha)


class Draw(Animation):
    """Draw the object"""

    def __init__(
        self,
        vmobject: VMobject,
        run_time: float = 2,
        rate_func: Callable[[float], float] = double_smooth,
        introducer: bool = True,
        **kwargs,
    ) -> None:
        self._typecheck_input(vmobject)
        super().__init__(
            vmobject,
            run_time=run_time,
            introducer=introducer,
            rate_func=rate_func,
            **kwargs,
        )

    def _typecheck_input(self, vmobject: VMobject) -> None:
        if not isinstance(vmobject, VMobject):
            raise TypeError(
                f"{self.__class__.__name__} only works for vectorized Mobjects"
            )

    def interpolate_submobject(
        self,
        submobject: Mobject,
        starting_submobject: Mobject,
        alpha: float,
    ) -> None:  # Fixme: not matching the parent class? What is outline doing here?
        submobject.pointwise_become_partial(self.mobject, 0, alpha)
        submobject.match_style(self.mobject)
