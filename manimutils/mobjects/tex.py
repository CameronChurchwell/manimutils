from manim import *

class BetterSingleStringMathTex(SingleStringMathTex):
    pass

class BetterMathTex(MathTex):

    def _break_up_by_substrings(self):
        """
        Reorganize existing submobjects one layer
        deeper based on the structure of tex_strings (as a list
        of tex_strings)
        """
        new_submobjects = []
        curr_index = 0
        for tex_string in self.tex_strings:
            if tex_string == r'\begin{cases}':
                num_submobs = 1
                sub_tex_mob = SingleStringMathTex('')
            elif tex_string == r'\end{cases}':
                continue
            else:
                sub_tex_mob = SingleStringMathTex(
                    tex_string,
                    tex_environment=self.tex_environment,
                    tex_template=self.tex_template,
                )
                num_submobs = len(sub_tex_mob.submobjects)
            new_index = (
                curr_index + num_submobs + len("".join(self.arg_separator.split()))
            )
            if num_submobs == 0:
                last_submob_index = min(curr_index, len(self.submobjects) - 1)
                sub_tex_mob.move_to(self.submobjects[last_submob_index], RIGHT)
            else:
                sub_tex_mob.submobjects = self.submobjects[curr_index:new_index]
            new_submobjects.append(sub_tex_mob)
            curr_index = new_index
        self.submobjects = new_submobjects
        return self
