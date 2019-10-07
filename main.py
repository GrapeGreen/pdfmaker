import re, os
import problemparser


def get_contest_name_and_date():
    contest_cfg = os.path.join(os.curdir, 'contest.cfg')
    if not os.path.isfile(contest_cfg):
        raise FileNotFoundError("There's no contest.cfg in {}.".format(os.curdir))

    date = '.'.join(re.findall('(\d{2})', '190711a')[:3][::-1])
    with open(contest_cfg, 'r') as f:
        for line in map(lambda x: x.strip(), f):
            if line.startswith('#'):
                continue
            regex_result = re.findall('^ContestName *:= *(.*)$', line.split('#')[0])
            if regex_result:
                return regex_result[0], date

    raise NameError("Unable to locate contest name in {}.".format(contest_cfg))


def get_problemset():
    problemset_cfg = os.path.join(os.curdir, 'problemset.cfg')
    if not os.path.isfile(problemset_cfg):
        raise FileNotFoundError("There's no problemset.cfg in {}.".format(os.curdir))

    problemset = []
    with open(problemset_cfg, 'r') as f:
        for line in map(lambda x: x.strip(), f):
            problem_type = problemparser.problem_type(line)
            if problem_type is None:
                continue
            problemset.append(problemparser.create(line, problem_type))

    return problemset


def main():
    problemset = get_problemset()
    print(get_contest_name_and_date())
    print('\Section{{{}}}{{{}}}'.format('limegreen', 'Easy'))
    print('\n'.join(map(lambda x : x.latex(), problemset)))


main()