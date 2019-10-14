import re, os
from enum import Enum


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
        for curr_folder, dirs, files in os.walk(root_link):
            # TODO: search everywhere and not only in the first occurrence.
            if 'statement' in curr_folder:
                files = [x for x in files if x.endswith('.tex')]
                if len(files) == 0:
                    continue
                if len(files) == 1:
                    return os.path.join(curr_folder, files[0])
                if len(files) > 1:
                    raise NotImplementedError("There is more than one statement "
                                              "file for problem {}. Currently we "
                                              "are unable to decide on such cases."
                                              .format(self._link))
        raise FileNotFoundError("Couldn't find any statement files"
                                " for problem {}.".format(self._link))

    def latex(self):
        return '\probl{{{}}}{{{}}}{{{} sec}}{{{} mb}}'.format(
            self._name, self._id, self._tl, self._ml)

    def section(self):
        return self._section


class ProblemParserPb(ProblemParser):
    def parse(self, problem_str):
        # TODO: fix parameter parsing to support " and , inside declarations.
        params = [x.strip().strip('"') for x in re.findall('\((.*?)\)', problem_str)[0].split(',')]
        self._id = params[0]
        self._name = params[2]
        print('Parsing problem {}: {}'.format(self._id, self._name))
        # This particular problem type targets everything under burunduk1/problems/yyyy-mm/<problem>.
        self._link = os.path.join('burunduk1', 'problems', params[3], params[2])
        self._tl = ProblemParser.normalize_tl(params[-2])
        self._ml = ProblemParser.normalize_ml(params[-1])


class ProblemParserProbdef(ProblemParser):
    def parse(self, problem_str):
        # TODO: fix parameter parsing to support " and , inside declarations.
        params = [x.strip().strip('"') for x in re.findall('\((.*?)\)', problem_str)[0].split(',')]
        # Trim " where applicable.
        self._id = params[0]
        self._name = re.split(r'[\\\/]', params[2])[-1]
        self._link = params[2]
        print('Parsing problem {}: {}'.format(self._id, self._name))
        self._tl = ProblemParser.normalize_tl(params[-2])
        self._ml = ProblemParser.normalize_ml(params[-1])
