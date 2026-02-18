from manim import *
import numpy as np

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
        bracket_submobs = -1
        for i, tex_string in enumerate(self.tex_strings):
            if tex_string == r'\begin{cases}':
                num_submobs = 1
                sub_tex_mob = SingleStringMathTex('')
            elif tex_string.strip() in [r'\\', r'&']: # ignore white spaces
                # TODO is this the best way to handle this?
                continue
            elif tex_string == r'\end{cases}':
                continue
            elif tex_string == r'\left[':
                close_index = self.tex_strings.index(r'\right]', i)
                with_brackets = SingleStringMathTex(''.join(self.tex_strings[i:close_index+1]))
                without_brackets = SingleStringMathTex(''.join(self.tex_strings[i+1:close_index]))
                assert (len(with_brackets.submobjects) - len(without_brackets.submobjects)) % 2 == 0, (len(with_brackets.submobjects) - len(without_brackets.submobjects))
                num_submobs = (len(with_brackets.submobjects) - len(without_brackets.submobjects)) // 2
                sub_tex_mob = SingleStringMathTex('')
                bracket_submobs = num_submobs
            elif tex_string == r'\right]':
                num_submobs = bracket_submobs
                sub_tex_mob = SingleStringMathTex('')
            elif tex_string == r'\begin{matrix}':
                num_submobs = 0
                sub_tex_mob = SingleStringMathTex('')
            elif tex_string == r'\end{matrix}':
                num_submobs = 0
                sub_tex_mob = SingleStringMathTex('')
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

    @staticmethod
    def matrix_to_tex_strings(matrix: np.ndarray):
        assert len(matrix.shape) == 2
        tex_strings = [r'\left[', r'\begin{matrix}']
        for row in matrix:
            for entry in row:
                tex_strings.append(str(entry))
                tex_strings.append(' & ')
            tex_strings[-1] = r' \\ '
        tex_strings[-1] = r'\end{matrix}'
        tex_strings.append(r'\right]')
        return tex_strings