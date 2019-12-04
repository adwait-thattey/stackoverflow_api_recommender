import random


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def debug(*args, **kwargs):
    module = kwargs["module"] if "module" in kwargs else "-"
    r = random.randint(1, 9)
    end = "\n"
    if "end" in kwargs:
        end = kwargs['end']

    message = " ".join([str(arg) for arg in args])
    messages = message.split('\n')
    for m in messages:
        print(bcolors.WARNING, end="")
        print('{:20}'.format(f'[DEBUG][{module.upper()}][{r}]'), ': ', end="")
        print(bcolors.ENDC, end="")
        print(m.strip(), end=' ')
    print(end=end)


def log(*args, **kwargs):
    module = kwargs["module"] if "module" in kwargs else "-"
    r = random.randint(1, 9)
    end = "\n"
    if "end" in kwargs:
        end = kwargs['end']

    message = " ".join([str(arg) for arg in args])
    messages = message.split('\n')
    for m in messages:
        print(bcolors.OKBLUE, end="")
        print('{:20}'.format(f'[LOG][{module.upper()}][{r}]'), ': ', end="")
        print(bcolors.ENDC, end="")
        print(m.lstrip(), end=' ')
    print(end=end)


def success(*args, **kwargs):
    module = kwargs["module"] if "module" in kwargs else "-"
    r = random.randint(1, 9)
    end = "\n"
    if "end" in kwargs:
        end = kwargs['end']

    message = " ".join([str(arg) for arg in args])
    messages = message.split('\n')
    for m in messages:
        print(bcolors.OKGREEN, end="")
        print('{:20}'.format(f'[SUCCESS][{module.upper()}][{r}]'), ': ', end="")
        print(bcolors.ENDC, end="")
        print(m.lstrip(), end=' ')
    print(end=end)


def warn(*args, **kwargs):
    module = kwargs["module"] if "module" in kwargs else "-"
    r = random.randint(1, 9)
    end = "\n"
    if "end" in kwargs:
        end = kwargs['end']

    message = " ".join([str(arg) for arg in args])
    messages = message.split('\n')
    for m in messages:
        print(bcolors.FAIL, end="")
        print('{:20}'.format(f'[WARN][{module.upper()}][{r}]'), ': ', end="")
        print(bcolors.ENDC, end="")
        print(m.lstrip(), end=' ')
    print(end=end)


def fail(*args, **kwargs):
    module = kwargs["module"] if "module" in kwargs else "-"
    r = random.randint(1, 9)
    end = "\n"
    if "end" in kwargs:
        end = kwargs['end']

    message = " ".join([str(arg) for arg in args])
    messages = message.split('\n')
    for m in messages:
        print(bcolors.FAIL, end="")
        print('{:20}'.format(f'[FAIL][{module.upper()}][{r}]'), ': ', end="")
        print(bcolors.ENDC, end="")
        print(m.lstrip(), end=' ')
    print(end=end)
