#!/usr/bin/python3.7
import re
import glog as log
from typing import List

FakeCalleeAddr = -2
InvalidAddr = -1
CodeSegLogName = 'EmptyCodeSeg.err'


def evalHexAddSubExpr(expr: str) -> int:
    val, op, curr = None, None, 0
    for (i, c) in enumerate(expr):
        if c in ['+', '-']:
            if val is None:
                val = curr
            else:
                val = (val + curr) if op is '+' else (val - curr)

            curr = 0
            op = c
        elif c is not 'h' and c is not ' ':
            curr = curr * 16 + int(c, 16)

    if op is None:
        return curr
    else:
        return (val + curr) if op is '+' else (val - curr)


def baseAddrInExpr(expr: str) -> int:
    curr = 0
    for (i, c) in enumerate(expr):
        if c in ['+', '-', '*', '/', 'h', ' ']:
            break

        curr = curr * 16 + int(c, 16)

    return curr


def findAddrInOperators(operators: List[str]) -> int:
    hexPattern = re.compile(r'[0-9A-Fa-f]+h?([\+\-\*\/][0-9A-Fa-f]+)?$')
    for item in operators:
        for part in item.split('_'):
            if hexPattern.match(part) is not None:
                log.debug(f'Convert "{part}" in {operators} to hex')
                return baseAddrInExpr(part)

    log.debug(f'"{operators}" is NOT convertiable to hex int')
    return FakeCalleeAddr


def delCodeSegLog() -> None:
    with open(CodeSegLogName, 'w') as errFile:
        errFile.write('binaryId\n')


def addCodeSegLog(binaryId) -> None:
    with open(CodeSegLogName, 'a') as errFile:
        errFile.write('%s\n' % binaryId)
