import datetime
import time

from grammar import grammar
from datalib import fetchData, TimeSeries
from whirlwind.storage import FindQuery


def evaluateTarget(store, requestContext, target):
    tokens = grammar.parseString(target)
    result = evaluateTokens(store, requestContext, tokens)

    if type(result) is TimeSeries:
        return [result]  # we have to return a list of TimeSeries objects

    else:
        return result


def evaluateTokens(store, requestContext, tokens):
    if tokens.expression:
        return evaluateTokens(store, requestContext, tokens.expression)

    elif tokens.pathExpression:
        return fetchData(store, requestContext, tokens.pathExpression)

    elif tokens.call:
        func = SeriesFunctions[tokens.call.funcname]
        args = [evaluateTokens(store, requestContext, arg) for arg in tokens.call.args]
        kwargs = dict([(kwarg.argname, evaluateTokens(store, requestContext, kwarg.args[0]))
                    for kwarg in tokens.call.kwargs])
        return func(requestContext, *args, **kwargs)

    elif tokens.number:
        if tokens.number.integer:
            return int(tokens.number.integer)

        elif tokens.number.float:
            return float(tokens.number.float)

    elif tokens.string:
        return str(tokens.string)[1:-1]

    elif tokens.boolean:
        return tokens.boolean[0] == 'true'


#Avoid import circularities
from functions import SeriesFunctions
