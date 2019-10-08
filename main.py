import re, os, sys, shutil, subprocess
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
            problem_type = problemparser.get_problem_type(line)
            if problem_type is None:
                continue
            problemset.append(problemparser.create(line, problem_type))

    return problemset


def create_contest_info(script_path):
    contest_info = os.path.join(script_path, 'temp', 'contest_info.tex')
    with open(contest_info, 'w') as w:
        contest_name, contest_date = get_contest_name_and_date()
        print('\def\\ID{{}}', file = w)
        print('\def\\NAME{{{}}}%'.format(contest_name), file = w)
        print('\def\\WHERE{Санкт-Петербургский Государственный Университет}%', file = w)
        print('\def\\DATE{{{}}}%'.format(contest_date), file = w)


def create_problemset_info(script_path):
    problemset_info = os.path.join(script_path, 'temp', 'problemset_info.tex')
    with open(problemset_info, 'w') as w:
        problemset = get_problemset()
        print('\Section{{{}}}{{{}}}'.format('limegreen', 'Easy'), file = w)
        print('\n'.join(map(lambda x: x.latex(), problemset)), file = w)


def create_pdf(script_path):
    source_dir = os.path.join(script_path, 'temp')
    for _ in range(2):
        subprocess.run("echo 'X' | pdflatex statement.tex 2> /dev/null")


def clear_temp(script_path):
    for file in os.listdir(script_path):
        os.remove(os.path.join(script_path, file))


def main():
    try:
        script_path = os.path.dirname(os.path.realpath(sys.argv[0]))

        create_contest_info(script_path)
        create_problemset_info(script_path)

        shutil.copy(os.path.join(script_path, 'src', 'statement.tex'),
                    os.path.join(script_path, 'temp', 'statement.tex'))

        create_pdf(script_path)

        shutil.move(os.path.join(script_path, 'temp', 'statement.pdf'),
                    os.path.join(os.getcwd(), 'statement.pdf'))

    except:
        pass

    clear_temp(script_path)


main()
