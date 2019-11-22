import re, os, sys, shutil, subprocess
import problemparser, colors
import traceback
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--upload', '-u', help = 'upload to /trains', action = 'store_true')
args = parser.parse_args()


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
            regex_result = re.findall('^ContestName\s*:=\s*(.*)$', line.split('#')[0])
            if regex_result:
                return regex_result[0].strip(), date

    raise NameError("Unable to locate contest name in {}.".format(contest_cfg))


def get_problemset():
    problemset_cfg = os.path.join(os.getcwd(), 'problemset.cfg')
    if not os.path.isfile(problemset_cfg):
        raise FileNotFoundError("There's no problemset.cfg in {}.".format(os.getcwd()))

    problemset = []
    section = colors.Section.default_section()
    with open(problemset_cfg, 'r', encoding = '866') as f:
        for line in map(lambda x: x.strip(), f):
            if colors.Section.is_section(line):
                section = colors.Section(line)
            problem_type = problemparser.ProblemType.get_problem_type(line)
            if problem_type is None:
                continue
            problemset.append(problemparser.ProblemParser.create(line, problem_type, section))

    return problemset


def create_contest_info(script_path):
    contest_info = os.path.join(script_path, 'temp', 'contest_info.tex')
    with open(contest_info, 'w', encoding = 'utf8') as w:
        contest_name, contest_date = get_contest_name_and_date()
        print('\def\\ID{{}}', file = w)
        print('\def\\NAME{{{}}}%'.format(contest_name), file = w)
        print('\def\\WHERE{Санкт-Петербургский Государственный Университет}%', file = w)
        print('\def\\DATE{{{}}}%'.format(contest_date), file = w)


def remove_includegraphics(file_path):
    with open(file_path, 'r', encoding='utf8') as f:
        data = f.read()
    with open(file_path, 'w', encoding='utf8') as w:
        print(re.sub(r'\\includegraphics\s*{.*?}', '', data), file=w)


def create_problemset_info(script_path):
    colors.Section.init_palette(script_path)

    problemset_info = os.path.join(script_path, 'temp', 'problemset_info.tex')
    with open(problemset_info, 'w', encoding = 'utf8') as w:
        problemset = get_problemset()
        if not problemset:
            raise AssertionError('No problems found?')
        print(problemset[0].section().latex(), file = w)
        print(problemset[0].latex(), file = w)
        for i in range(1, len(problemset)):
            if problemset[i - 1].section() != problemset[i].section():
                print(problemset[i].section().latex(), file = w)
            print(problemset[i].latex(), file = w)
        for problem in problemset:
            dest = os.path.join(
                script_path, 'temp', 'problems', '{}.{}.tex'.format(problem.id(), problem.name()))
            shutil.copy(problem.statements(), dest)
            remove_includegraphics(dest)


def copy_sources(script_path):
    for file in ['statement.tex', 'colors.tex', 'olymp.sty']:
        src, dest = [os.path.join(script_path, x, file) for x in ['src', 'temp']]
        shutil.copy(src, dest)


def create_pdf(script_path):
    source_dir = os.path.join(script_path, 'temp')
    subprocess.run("cd {} && echo 'X' | pdflatex statement.tex > nul".format(source_dir),
                       shell = True)
    subprocess.run("cd {} && echo 'X' | pdflatex statement.tex | grep 'Output written'".format(source_dir),
                   shell = True)
    if not os.path.isfile(os.path.join(script_path, 'temp', 'statement.pdf')):
        raise FileNotFoundError('Unable to create statement.pdf from sources.')
    shutil.move(os.path.join(script_path, 'temp', 'statement.pdf'),
                os.path.join(os.getcwd(), 'statement.pdf'))


def clear_temp(script_path):
    temp_dir = os.path.join(script_path, 'temp')
    shutil.rmtree(temp_dir)


def upload_pdf():
    pdf_src = os.path.join(os.getcwd(), 'statement.pdf')
    date = re.split(r'[\\\/]', os.getcwd())[-1]
    pdf_target = '/var/www/acm/trains/{}.pdf'.format(date)
    print('Uploading {} to {}'.format(pdf_src, pdf_target), file = sys.stderr)
    subprocess.run('pscp -P 220 {} {}@acm.math.spbu.ru:{}'.format(
        pdf_src, os.getlogin(), pdf_target
    ), shell = True)


def main():
    script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    try:
        verify_structure(script_path)
        copy_sources(script_path)
        create_contest_info(script_path)
        create_problemset_info(script_path)
        create_pdf(script_path)
        if args.upload:
            upload_pdf()
    except Exception as e:
        traceback.print_exc()
    finally:
        clear_temp(script_path)


if __name__ == '__main__':
    main()
