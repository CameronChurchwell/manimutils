from pathlib import Path

from manim import *
import manim
from manim_slides import Slide
from manim_slides.slide.animation import Wipe
from manimutils import AudioSlide


tex_preamble = r"""
\usepackage[english]{babel}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{dsfont}
\usepackage{setspace}
\usepackage{tipa}
\usepackage{relsize}
\usepackage{textcomp}
\usepackage{mathrsfs}
\usepackage{calligra}
\usepackage{wasysym}
\usepackage{ragged2e}
\usepackage{physics}
\usepackage{xcolor}
\usepackage{microtype}
\usepackage{enumitem}
\DisableLigatures{encoding = *, family = * }
\setlist[itemize]{leftmargin=1em, topsep=0em, itemsep=0em} % First-level itemize indentation
\setlength{\textwidth}{30em}
\usepackage[none]{hyphenat}
\singlespacing
"""

def scale_to_fit(mobject, width, height):
    width_ratio = width / mobject.width
    height_ratio = height / mobject.height
    scale_factor = min(width_ratio, height_ratio)
    return mobject.scale(scale_factor)

def scale_to_fit_region(mobject, region: Rectangle):
    return scale_to_fit(mobject, region.width, region.height)

tex_template = TexTemplate(preamble=tex_preamble)
class CustomSlide(AudioSlide):
    name: str = None

    def __str__(self):
        if self.name is not None:
            return self.name
        else:
            return super().__str__()

    def update_canvas(self):
        if hasattr(self, 'counter'):
            self.counter += 1
            old_slide_number = self.canvas["slide_number"]
            new_slide_number = Text(f"{self.counter}").move_to(old_slide_number)
            return Transform(old_slide_number, new_slide_number, run_time=0.25)
        return Wait(stop_condition=lambda: True)

    def transition(self, future, return_anim=False):
        current = self.mobjects_without_canvas
        anim = Wipe(current, future, run_time=0.5)
        anim = AnimationGroup(anim, self.update_canvas())
        if return_anim:
            return anim
        self.play(anim)

    def play_sequence(self, iterator):
        for anim in iter(iterator):
            self.play(anim)

    def title_region(self, height_ratio=0.1, side_buffer=None):
        if side_buffer is None:
            side_buffer = DEFAULT_MOBJECT_TO_EDGE_BUFFER
        width = manim.config['frame_width'] - 2*side_buffer
        height = manim.config['frame_height'] * height_ratio
        region = Rectangle(height=height, width=width)
        region.to_edge(UP)
        return region

    def footer_region(self, height_ratio=0.05, side_buffer=None):
        if side_buffer is None:
            side_buffer = DEFAULT_MOBJECT_TO_EDGE_BUFFER
        width = manim.config['frame_width'] - 2*side_buffer
        height = manim.config['frame_height'] * height_ratio
        region = Rectangle(height=height, width=width)
        region.to_edge(DOWN)
        return region

    def content_region(self, side_buffer=None, top_buffer=None, bottom_buffer=None):
        if side_buffer is None:
            side_buffer = DEFAULT_MOBJECT_TO_EDGE_BUFFER
        if bottom_buffer is None:
            bottom_buffer = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER
        if top_buffer is None:
            top_buffer = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER
        title_region = self.title_region()
        width = manim.config['frame_width'] - 2*side_buffer
        footer_region = self.footer_region()
        # the center of the screen is at (0,0), so the math looks a bit weird when simplified:
        height = (
            title_region.get_bottom()[1]
            - footer_region.get_top()[1]
            # + manim.config['frame_height']/2
            - bottom_buffer
            - top_buffer
        )
        region = Rectangle(height=height, width=width)
        region.next_to(title_region, DOWN, top_buffer)
        return region

    def half_content_region(self, side=LEFT, middle_buffer=None):
        if middle_buffer is None:
            middle_buffer = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER
        content_region = self.content_region()
        region = content_region.copy()
        region.stretch(0.5, 0)
        buffer_factor = (region.width - middle_buffer/2) / region.width
        region.stretch(buffer_factor, 0)
        region.align_to(content_region, side)
        return region

    def demo_layout(self):
        title_region = self.title_region()
        footer_region = self.footer_region()
        content_region = self.content_region()
        left_region = self.half_content_region(LEFT)
        right_region = self.half_content_region(RIGHT)
        self.play(Succession(
            FadeIn(title_region),
            FadeIn(footer_region),
            FadeIn(content_region),
            FadeIn(left_region),
            FadeIn(right_region),
        ))
        self.next_slide()

    def slide_title(self, title, color=ORANGE):
        text = Text(title, font_size=70, color=color)
        region = self.title_region()
        scale_to_fit_region(text, region)
        text.move_to(region)
        text.align_to(region, LEFT)
        return text

    def scale_to_fit(self, mobject, region=None):
        if region is None:
            region = self.content_region()
        return scale_to_fit_region(mobject, region)

    def in_region(self, mobject, region=None):
        if region is None:
            region = self.content_region()
        return self.scale_to_fit(mobject, region).move_to(region)

    def center(self, mobject, region=None):
        if region is None:
            region = self.content_region()
        mobject.move_to(region)

    def bullets(self, *bullets, scale_factor=1, bullets_region=None):
        bullets = list(bullets)

        if bullets_region is None:
            bullets_region = self.content_region()

        colors = {}
        shapes = {}
        i = 0
        while i < len(bullets):
            bullet = bullets[i]
            if isinstance(bullet, ManimColor):
                colors[i] = bullet
                del bullets[i]
            elif isinstance(bullet, VMobject):
                shapes[i] = bullet
                del bullets[i]
            else:
                i += 1

        indentation = []
        for i in range(0, len(bullets)):
            indentation.append(0)
            while bullets[i].startswith('\t'):
                bullets[i] = bullets[i][1:]
                indentation[i] += 1
            bullets[i] = bullets[i].replace('\n', '\\\\')

        bullets = BulletedList(*bullets, buff=MED_SMALL_BUFF)
        bullets.scale(scale_factor)

        for i, shape in shapes.items():
            dot = bullets[i][0]
            shape = shape.copy().move_to(dot)
            shape.scale(scale_factor)
            bullets[i][0].become(shape)
            bullets[i][0].next_to(bullets[i][1:], LEFT, SMALL_BUFF)

        for i, color in colors.items():
            bullets[i].set_color(color)

        bullets.align_to(bullets_region, LEFT)
        bullets.align_to(bullets_region, UP)

        max_allowed = bullets_region.get_right()[0]
        for bullet, ind in zip(bullets.submobjects, indentation):
            for i in range(0, ind):
                bullet.shift(RIGHT*scale_factor)
            if bullet.get_right()[0] > max_allowed:
                breakpoint()
                raise ValueError('bullet with content,', bullet, 'is too long')

        return bullets

    def bullet_slide(self, title, *bullets, auto_show_all=False):
        title = self.slide_title(title)
        if not auto_show_all:
            self.transition(title)
            self.next_slide()

        bullets = self.bullets(*bullets)
        self.scale_to_fit(bullets)
        # bullets.move_to(self.content_region())
        bullets.align_to(self.content_region(), UL)

        if auto_show_all:
            self.transition(VGroup(title, bullets))
            self.next_slide()
        else:
            for bullet in bullets.submobjects:
                self.play(FadeIn(bullet))
                self.next_slide()

    def image(self, image_path, image_region=None):
        assert Path(image_path).exists()
        if image_region is None:
            image_region = self.content_region()
        image = ImageMobject(image_path)
        scale_to_fit_region(image, image_region)
        image.move_to(image_region)
        return image

    def image_slide(self, title, image_path):
        title = self.slide_title(title)
        self.transition(title)
        self.next_slide()
        image = self.image(image_path)
        self.play(FadeIn(image))
        self.next_slide()

    def bullet_image_slide(self, title, *bullets, image_path, image_bullet_index=0):
        title = self.slide_title(title)
        self.transition(title)
        self.next_slide()

        bullets = self.bullets(*bullets, scale_factor=0.8, bullets_region=self.half_content_region(LEFT))
        image = self.image(image_path, image_region=self.half_content_region(RIGHT))

        for i, bullet in enumerate(bullets.submobjects):
            if i == image_bullet_index:
                self.play(FadeIn(bullet, image))
            else:
                self.play(FadeIn(bullet))
            self.next_slide()

    def title_slide(self, title, author, animation=False, return_animation=False):
        self.play(Wait()); self.next_slide(auto_next=animation)
        text = Text(title, font_size=86, color=ORANGE)
        text.scale_to_fit_width(manim.config['frame_width'])
        text.scale(0.8)
        subtext = Text(author, font_size=40)
        subtext.next_to(text, DOWN)
        anim = Succession(
            Write(text),
            Write(subtext),
        )
        if return_animation:
            return anim
        self.play(anim)
        if animation:
            self.next_slide(loop=True)
            self.play(AnimationGroup(
                ApplyWave(text, amplitude=0.02, run_time=2.),
                ApplyWave(subtext, amplitude=0.02, run_time=2.),
                Wait(1),
                lag_ratio=0.2
            ),)
        self.next_slide()

    def enable_slide_numbers(self):
        self.counter = 0
        slide_number = Text("0")
        region = self.footer_region()
        self.scale_to_fit(slide_number, region)
        self.center(slide_number, region)
        slide_number.align_to(region, RIGHT)
        self.add(slide_number)
        self.add_to_canvas(slide_number=slide_number)

    # def play_audio(self, audio_file):
    #     still = self.renderer.get_frame()