import re, os, sys
from enum import Enum
import re_helper


class ProblemType(Enum):
    # Supported problem types.
    pb = 1,
    probdef = 2

    @staticmethod
    def get_problem_type(problem_str):
        # The list of supported types can be found in ProblemType enum.
        for problem_type in ProblemType:
            regex = '{}\d{{0,1}}\s*\("'.format(problem_type.name)
            if re.match(regex, problem_str):
                return problem_type
        return None


class ProblemParser:
    def __init__(self, problem_str, section):
        self._section = section
        self._id, self._name, self._link = ["" for _ in range(3)]
        self._tl, self._ml = [0 for _ in range(2)]
        self.parse(problem_str)
        print('Parsing problem {}: {}\n{}'.format(self._id, self._name, self.latex()), file=sys.stderr)

    def parse(self, problem_str):
        raise NotImplementedError

    @staticmethod
    def create(problem_str, problem_type, section):
        problem_class_name = 'ProblemParser{}'.format(problem_type.name.capitalize())
        if problem_class_name not in globals():
            raise NotImplementedError('No ProblemParser definition for {}.'.format(problem_type.name))
        return globals()[problem_class_name](problem_str, section)

    @staticmethod
    def normalize_tl(tl):
        if len(tl) <= 2:
            return int(tl)
        if int(tl) % 1000 == 0:
            return int(tl) // 1000
        else:
            return float(tl) / 1000

    @staticmethod
    def normalize_ml(ml):
        ml = int(ml)
        if ml > 1024:
            return ml // 1024
        return ml

    def id(self):
        return self._id

    def name(self):
        return self._name

    def statements(self):
        root_link = os.path.join('D:\problems', self._link)
        sources = []
        for curr_folder, dirs, files in os.walk(root_link):
            if 'statement' in curr_folder:
                files = [os.path.join(curr_folder, x) for x in files if x.endswith('.tex')]
                # In case of two source files one of them might be the english translation.
                if len(files) == 2 and any(x.endswith('.en.tex') for x in files):
                    candidates = [x for x in files if not x.endswith('.en.tex')]
                    if candidates:
                        sources.append(os.path.join(curr_folder, candidates[0]))
                else:
                    sources.extend(files)
        if not sources:
            raise FileNotFoundError("Couldn't find any statement files"
                                    " for problem {}.".format(self._link))
        sources.sort()
        if len(sources) == 1:
            return sources[0]
        print('Pdfmaker found more than one tex source for problem {}:'.format(self.id()))
        print('[\n\t{}\n]'.format('\n,\t'.join(sources)))
        print('Input a number from 1 to {} to determine which source to use.'.format(len(sources)))
        return sources[int(input()) - 1]

    def graphics(self):
        link = self.statements()
        with open(link, 'r', encoding = 'utf8') as f:
            pics = [os.path.join(os.path.split(link)[0], x) for x in
                    re.findall(r'\\includegraphics(?:\s*\[.*?\]\s*)*{\s*(.+?)\s*}', f.read())]
            return pics

    def latex(self):
        return '\probl{{{}}}{{{}}}{{{} sec}}{{{} mb}}'.format(
            self._name, self._id, self._tl, self._ml)

    def section(self):
        return self._section


class ProblemParserPb(ProblemParser):
    def parse(self, problem_str):
        match = re_helper.create_regex(
            'pb\d?',
            re_helper.OPENING_BRACKET,
            *([re_helper.QUOTED_STRING,
            re_helper.COMMA] * 4),
            re_helper.INT_VALUE,
            re_helper.COMMA,
            re_helper.INT_VALUE,
            re_helper.CLOSING_BRACKET,
            re_helper.COMMENT
        ).fullmatch(problem_str)
        if match is None:
            raise AssertionError('Line\n{}\nis not formatted correctly.'.format(problem_str))
        self._id, self._name = match.group(1, 3)
        # This particular problem type targets everything under burunduk1/problems/yyyy-mm/<problem>.
        self._link = os.path.join('burunduk1', 'problems', *match.group(4, 3))
        self._tl = ProblemParser.normalize_tl(match.group(5))
        self._ml = ProblemParser.normalize_ml(match.group(6))


class ProblemParserProbdef(ProblemParser):
    def parse(self, problem_str):
        match = re_helper.create_regex(
            'probdef\d?',
            re_helper.OPENING_BRACKET,
            *([re_helper.QUOTED_STRING,
               re_helper.COMMA] * 3),
            re_helper.INT_VALUE,
            re_helper.COMMA,
            re_helper.INT_VALUE,
            re_helper.CLOSING_BRACKET,
            re_helper.COMMENT
        ).fullmatch(problem_str)
        if match is None:
            raise AssertionError('Line\n{}\nis not formatted correctly.'.format(problem_str))
        self._id, self._link = match.group(1, 3)
        self._name = re.split(r'[\\\/]', match.group(3))[-1]
        self._tl = ProblemParser.normalize_tl(match.group(4))
        self._ml = ProblemParser.normalize_ml(match.group(5))
