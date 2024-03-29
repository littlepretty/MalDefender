#!/usr/bin/python3.7
import re
import glob
import glog as log
import pandas as pd
from typing import List, Dict, Set

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
    """
    Find possible address in operators.
    For call/syscall inst, this func may return false positive address;
    the remedy is to do a second check on if addr is invalid,
    in which case the returned addr should be treated as FakeCalleeAddr.
    """
    hexPattern = re.compile(r'[0-9A-Fa-f]+h?([\+\-\*\/][0-9A-Fa-f]+)?$')
    for item in operators:
        for part in item.split('_'):
            if hexPattern.match(part) is not None:
                log.debug(f'[FindAddr] Convert "{part}" in {operators} to hex')
                return baseAddrInExpr(part)

    log.debug(f'[FindAddr] "{operators}" NOT convertiable to hex')
    return FakeCalleeAddr


def delCodeSegLog() -> None:
    with open(CodeSegLogName, 'w') as errFile:
        errFile.write('binaryId\n')


def addCodeSegLog(binaryId) -> None:
    with open(CodeSegLogName, 'a') as errFile:
        errFile.write('%s\n' % binaryId)


def loadBinaryIds(pathPrefix: str,
                  bId2Label: Dict[str, str] = None) -> List[str]:
    """
    Instead of just return @bId2Label.keys(), check if binary file
    do exist under @pathPrefix directory
    """
    binaryIds = []
    for path in glob.glob(pathPrefix + '/*.asm', recursive=False):
        filename = path.split('/')[-1]
        id = filename.split('.')[0]
        binaryIds.append(id)
        if bId2Label is not None:
            assert id in bId2Label

    return binaryIds

def cmpInstDict(trainDictPath: str, testDictPath: str) -> Set[str]:
    trainDf = pd.read_csv(trainDictPath, header=0, dtype={'Inst': str})
    testDf = pd.read_csv(testDictPath, header=0, dtype={'Inst': str})
    trainDict, testDict= set(trainDf['Inst']), set(testDf['Inst'])
    diff = list(testDict.difference(trainDict))
    return sorted(diff)
