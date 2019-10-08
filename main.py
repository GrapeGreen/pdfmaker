import re, os, sys, shutil, subprocess
import problemparser


def verify_structure(script_path):
    if not os.path.isdir(os.path.join(script_path, 'temp')):
        os.mkdir(os.path.join(script_path, 'temp'))
    if not os.path.isdir(os.path.join(script_path, 'temp', 'problems')):
        os.mkdir(os.path.join(script_path, 'temp', 'problems'))
    for file in ['statement.tex', 'colors.tex', 'olymp.sty']:
        if not os.path.isfile(os.path.join(script_path, 'src', file)):
            raise FileNotFoundError('No file called {} in {}.'.format(
                file, os.path.join(script_path, 'src')))


def get_contest_name_and_date():
    contest_cfg = os.path.join(os.getcwd(), 'contest.cfg')
    if not os.path.isfile(contest_cfg):
        raise FileNotFoundError("There's no contest.cfg in {}.".format(os.getcwd()))

    date = '.'.join(re.findall('(\d{2})', re.split(r'[\\\/]', os.getcwd())[-1])[:3][::-1])
    with open(contest_cfg, 'r', encoding = '866') as f:
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
    with open(problemset_cfg, 'r', encoding = '866') as f:
        for line in map(lambda x: x.strip(), f):
            problem_type = problemparser.get_problem_type(line)
            if problem_type is None:
                continue
            problemset.append(problemparser.create(line, problem_type))

    return problemset


def create_contest_info(script_path):
    contest_info = os.path.join(script_path, 'temp', 'contest_info.tex')
    with open(contest_info, 'w', encoding = 'utf8') as w:
        contest_name, contest_date = get_contest_name_and_date()
        print('\def\\ID{{}}', file = w)
        print('\def\\NAME{{{}}}%'.format(contest_name), file = w)
        print('\def\\WHERE{Санкт-Петербургский Государственный Университет}%', file = w)
        print('\def\\DATE{{{}}}%'.format(contest_date), file = w)


def create_problemset_info(script_path):
    problemset_info = os.path.join(script_path, 'temp', 'problemset_info.tex')
    with open(problemset_info, 'w', encoding = 'utf8') as w:
        problemset = get_problemset()
        print('\Section{{{}}}{{{}}}'.format('limegreen', 'Easy'), file = w)
        print('\n'.join(map(lambda x: x.latex(), problemset)), file = w)
        for problem in problemset:
            shutil.copy(problem.statements(), os.path.join(
                script_path, 'temp', 'problems', '{}.{}.tex'.format(problem.id(), problem.name())))


def copy_sources(script_path):
    for file in ['statement.tex', 'colors.tex', 'olymp.sty']:
        shutil.copy(os.path.join(script_path, 'src', file),
                    os.path.join(script_path, 'temp', file))


def create_pdf(script_path):
    source_dir = os.path.join(script_path, 'temp')
    for _ in range(2):
        subprocess.run("cd {} && echo 'X' | pdflatex statement.tex".format(source_dir),
                       shell = True)
    if not os.path.isfile(os.path.join(script_path, 'temp', 'statement.pdf')):
        raise FileNotFoundError("Unable to create statement.pdf from sources.")
    shutil.move(os.path.join(script_path, 'temp', 'statement.pdf'),
                os.path.join(os.getcwd(), 'statement.pdf'))


def clear_temp(script_path):
    for file in os.listdir(script_path):
        os.remove(os.path.join(script_path, file))


def main():
    script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    try:
        verify_structure(script_path)
        copy_sources(script_path)
        create_contest_info(script_path)
        create_problemset_info(script_path)
        create_pdf(script_path)
    except Exception as e:
        print(e)

    #clear_temp(script_path)


main()
