import os, re


class Section:
    def __init__(self, section_str):
        params = [x.strip() for x in section_str.replace('#--', '').split('#')[0].split(',')]
        if len(params) == 2:
            self._name, self._color = params
        elif len(params) == 1:
            self._name = params[0]
            if self._name not in Section.predefined_sections:
                raise AssertionError('Section {} does not specify a color.'.format(self._name))
            self._color = Section.predefined_sections[self._name]
        else:
            raise AssertionError('Expected 1 or 2 arguments in Section declaration, found {}.'.format(len(params)))

        if self._color not in Section.palette:
            raise AssertionError('Color {} is not defined in colors.tex'.format(self._color))

    def latex(self):
        return '\Section{{{}}}{{{}}}'.format(self._color, self._name)

    def __eq__(self, other):
        return self.latex() == other.latex()

    @staticmethod
    def is_section(section_str):
        return section_str.startswith('#--')

    @staticmethod
    def default_section():
        return Section('Easy')

    @staticmethod
    def init_palette(script_path):
        colors_tex = os.path.join(script_path, 'src', 'colors.tex')
        with open(colors_tex, 'r') as f:
            for line in map(lambda x: x.strip(), f):
                Section.palette.add(re.findall('definecolor{(.*?)}', line)[0])

    predefined_sections = {'Easy' : 'limegreen',
                           'Medium' : 'royalblue',
                           'Hard' : 'pumpkin'}

    palette = set()
