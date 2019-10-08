import re, os, sys, shutil
import problemparser


def get_contest_name_and_date():
    contest_cfg = os.path.join(os.getcwd(), 'contest.cfg')
    if not os.path.isfile(contest_cfg):
        raise FileNotFoundError("There's no contest.cfg in {}.".format(os.getcwd()))

    date = '.'.join(re.findall('(\d{2})', os.getcwd())[:3][::-1])
    with open(contest_cfg, 'r') as f:
        for line in map(lambda x: x.strip(), f):
            if line.startswith('#'):
                continue
            regex_result = re.findall('^ContestName *:= *(.*)$', line.split('#')[0])
            if regex_result:
                return regex_result[0].strip(), date

    raise NameError("Unable to locate contest name in {}.".format(contest_cfg))


def get_problemset():
    problemset_cfg = os.path.join(os.getcwd(), 'problemset.cfg')
    if not os.path.isfile(problemset_cfg):
        raise FileNotFoundError("There's no problemset.cfg in {}.".format(os.getcwd()))

    problemset = []
    with open(problemset_cfg, 'r') as f:
        for line in map(lambda x: x.strip(), f):
            problem_type = problemparser.problem_type(line)
            if problem_type is None:
                continue
            problemset.append(problemparser.create(line, problem_type))

    return problemset


def main():
    script_path = os.path.dirname(os.path.realpath(sys.argv[0]))

    contest_info = os.path.join(script_path, 'temp', 'contest_info.tex')
    with open(contest_info, 'w') as w:
        contest_name, contest_date = get_contest_name_and_date()
        print('\def\\ID{{}}', file = w)
        print('\def\\NAME{{{}}}%'.format(contest_name), file = w)
        print('\def\\WHERE{Санкт-Петербургский Государственный Университет}%', file = w)
        print('\def\\DATE{{{}}}%'.format(contest_date), file = w)

    problemset_info = os.path.join(script_path, 'temp', 'problemset_info.tex')
    with open(problemset_info, 'w') as w:
        problemset = get_problemset()
        print('\Section{{{}}}{{{}}}'.format('limegreen', 'Easy'), file = w)
        print('\n'.join(map(lambda x : x.latex(), problemset)), file = w)

    shutil.copy(os.path.join(script_path, 'src', 'statement.tex'),
                os.path.join(script_path, 'temp', 'statement.tex'))

main()
