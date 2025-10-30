from manim import *
from typing import Iterable, Callable
from manim.mobject.utils import get_vectorized_mobject_class
import numpy as np

import itertools as it

class MultiTable(Table):

    def __init__(
        self,
        table: Iterable[Iterable[float | str | VMobject]],
        row_labels: Iterable[VMobject] | None = None,
        col_labels: Iterable[VMobject] | None = None,
        top_left_entry: VMobject | None = None,
        v_buff: float = 0.8,
        h_buff: float = 1.3,
        include_outer_lines: bool = False,
        add_background_rectangles_to_entries: bool = False,
        entries_background_color: ParsableManimColor = BLACK,
        include_background_rectangle: bool = False,
        background_rectangle_color: ParsableManimColor = BLACK,
        element_to_mobject: Callable[
            [float | str | VMobject],
            VMobject,
        ] = Paragraph,
        element_to_mobject_config: dict = {},
        arrange_in_grid_config: dict = {},
        line_config: dict = {},
        better_lines: bool = True,
        **kwargs,
    ):
        # super().__init__(
        #     table,
        #     row_labels,
        #     col_labels,
        #     top_left_entry,
        #     v_buff,
        #     h_buff,
        #     include_outer_lines,
        #     add_background_rectangles_to_entries,
        #     entries_background_color,
        #     include_background_rectangle,
        #     background_rectangle_color,
        #     element_to_mobject,
        #     element_to_mobject_config,
        #     arrange_in_grid_config,
        #     line_config,
        #     **kwargs
        # )
        self.row_labels = row_labels
        if not (isinstance(col_labels[0], (tuple, list)) or isinstance(col_labels, np.ndarray)): # convert to multi-indexed
            col_labels = [col_labels]
        self.col_labels = col_labels
        self.top_left_entry = top_left_entry
        self.row_dim = len(table)
        self.col_dim = len(table[0])
        self.v_buff = v_buff
        self.h_buff = h_buff
        self.include_outer_lines = include_outer_lines
        self.add_background_rectangles_to_entries = add_background_rectangles_to_entries
        self.entries_background_color = ManimColor(entries_background_color)
        self.include_background_rectangle = include_background_rectangle
        self.background_rectangle_color = ManimColor(background_rectangle_color)
        self.element_to_mobject = element_to_mobject
        self.element_to_mobject_config = element_to_mobject_config
        self.arrange_in_grid_config = arrange_in_grid_config
        self.line_config = line_config

        for row in table:
            if len(row) == len(table[0]):
                pass
            else:
                raise ValueError("Not all rows in table have the same length.")

        super(Table, self).__init__(**kwargs)
        mob_table = self._table_to_mob_table(table)
        self.elements_without_labels = VGroup(*it.chain(*mob_table))
        mob_table = self._add_labels(mob_table)
        self._organize_mob_table(mob_table)
        self.elements = VGroup(*it.chain(*mob_table))

        if len(self.elements[0].get_all_points()) == 0:
            self.elements.remove(self.elements[0])

        self.add(self.elements)
        self.center()
        self.mob_table = mob_table
        self._add_horizontal_lines(better_lines)
        if not better_lines:
            self._add_vertical_lines()
        if self.add_background_rectangles_to_entries:
            self.add_background_to_entries(color=self.entries_background_color)
        if self.include_background_rectangle:
            self.add_background_rectangle(color=self.background_rectangle_color)


    def _add_horizontal_lines(self, better_lines=True):
        """Adds the horizontal lines to the table."""
        anchor_left = self.get_left()[0] - 0.5 * self.h_buff
        anchor_right = self.get_right()[0] + 0.5 * self.h_buff
        line_group = VGroup()
        if self.include_outer_lines or better_lines:
            anchor = self.get_rows()[0].get_top()[1] + 0.5 * self.v_buff
            line = Line(
                [anchor_left, anchor, 0], [anchor_right, anchor, 0], **self.line_config
            )
            line_group.add(line)
            self.add(line)
            anchor = self.get_rows()[-1].get_bottom()[1] - 0.5 * self.v_buff
            line = Line(
                [anchor_left, anchor, 0], [anchor_right, anchor, 0], **self.line_config
            )
            line_group.add(line)
            self.add(line)
        for k in range(len(self.mob_table) - 1):
            if better_lines:
                if self.col_labels is not None:
                    if k != len(self.col_labels) - 1:
                        continue
                else:
                    break
            anchor = self.get_rows()[k + 1].get_top()[1] + 0.5 * (
                self.get_rows()[k].get_bottom()[1] - self.get_rows()[k + 1].get_top()[1]
            )
            line = Line(
                [anchor_left, anchor, 0], [anchor_right, anchor, 0], **self.line_config
            )
            line_group.add(line)
            self.add(line)
        self.horizontal_lines = line_group
        return self

    def _add_labels(self, mob_table):
        if self.row_labels is not None:
            for k in range(len(self.row_labels)):
                mob_table[k] = [self.row_labels[k]] + mob_table[k]
        if self.col_labels is not None:
            multi_col_labels = self.col_labels

            tle = [get_vectorized_mobject_class()()]
            if self.top_left_entry is not None:
                tle = [self.top_left_entry]

            for col_labels in reversed(multi_col_labels):
                col_labels = [self.element_to_mobject(label, **self.element_to_mobject_config) for label in col_labels]
                if self.row_labels is not None:
                    col_labels = tle + col_labels
                    tle = [get_vectorized_mobject_class()()]
                mob_table.insert(0, col_labels)
        return mob_table