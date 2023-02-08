import constraintsolver.solver as S

contracts = None


def check_post(first, second):
    pass


def check_pre(first, second):
    pass


def check_subsumption(first):
    for second in contracts:
        if first != second:
            check_pre(first, second)
            check_post(first, second)


def refine(contracts_):
    global contracts
    contracts = contracts_

    for contract in contracts:
        check_subsumption(contract)
