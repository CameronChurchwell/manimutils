from manim import *
from typing import Any

class BentArrow(Arrow):

    def __init__(
        self,
        *args: Any,
        stroke_width: float = 4,
        buff: float = SMALL_BUFF*0.5,
        max_tip_length_to_length_ratio: float = 0.25,
        max_stroke_width_to_length_ratio: float = 5,
        **kwargs: Any,
    ) -> None:
        self.max_tip_length_to_length_ratio = max_tip_length_to_length_ratio
        self.max_stroke_width_to_length_ratio = max_stroke_width_to_length_ratio
        tip_shape = kwargs.pop("tip_shape", ArrowTriangleFilledTip)
        super(Arrow, self).__init__(*list(args)[-2:], buff=buff, stroke_width=stroke_width, **kwargs)  # type: ignore[misc]

        args = np.array(args).round(6)
        self.set_points_as_corners(args)
        self._account_for_buff(buff)

        # TODO, should this be affected when
        # Arrow.set_stroke is called?
        self.initial_stroke_width = self.stroke_width
        self.add_tip(tip_shape=tip_shape, tip_width=0.125, tip_length=0.125)
        self._set_stroke_width_from_length()

    def _set_stroke_width_from_length(self):
        pass

    def put_start_and_end_on(self, start, end):
        self.points[0] = np.asarray(start)
        self.points[-1] = np.asarray(end)
        return self
    
    def _account_for_buff(self, buff: float) -> None:
        if buff <= 0:
            return

        points = self.get_anchors()

        first, second = points[0], points[1]
        direction = second-first
        norm = np.linalg.norm(direction)
        if norm > buff:
            direction = direction / norm
            points[0] = first + buff * direction

        first, second = points[-1], points[-2]
        direction = second-first
        norm = np.linalg.norm(direction)
        if norm > buff:
            direction = direction / norm
            points[-1] = first + buff * direction

        self.set_points_as_corners(points)
        return

        length0 = np.linalg.norm(points[1] - points[0])
        buff_proportion_0 = buff / length0
        length1 = np.linalg.norm(points[-1] - points[-2])
        buff_proportion_1 = buff / length1

        
        if buff_proportion_1 > 1 or buff_proportion_0 > 1:
            return
        print(buff_proportion_0, 1-buff_proportion_1)
        if buff_proportion_0 > 1-buff_proportion_1:
            return
        self.pointwise_become_partial(self.copy(), buff_proportion_0, 1 - buff_proportion_1) # This fixes a bug in manim
        return

    def get_length(self) -> float:
        return float(np.linalg.norm(np.diff(np.array(self.get_anchors()), axis=0), axis=1).sum())
