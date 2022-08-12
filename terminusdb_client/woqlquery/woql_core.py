# helper functions for WOQLCore
import re


def _split_at(op, tokens):
    results = []
    stack = []
    paren_depth = 0
    brace_depth = 0
    for token in tokens:
        if token == ")":
            paren_depth -= 1
            stack.append(token)
        elif token == "(":
            paren_depth += 1
            stack.append(token)
        elif token == "}":
            brace_depth -= 1
            stack.append(token)
        elif token == "{":
            brace_depth += 1
            stack.append(token)
        elif paren_depth == 0 and brace_depth == 0 and token == op:
            results.append(stack)
            stack = []
        else:
            stack.append(token)

    if paren_depth < 0 or brace_depth < 0:
        raise SyntaxError(f"Unbalanced parenthesis or braces in path pattern {tokens}")

    results.append(stack)
    return results


def _path_tokens_to_json(tokens):
    seqs = _split_at(",", tokens)
    phrases = []
    for seq in seqs:
        phrases.append(_path_or_parser(seq))
    # In the degenerate case where there is only one operand
    # we just return the operand (and(q) == q)
    if len(phrases) == 1:
        return phrases[0]
    else:
        return {"@type": "PathSequence", "sequence": phrases}


def _path_or_parser(tokens):
    ors = _split_at("|", tokens)
    phrases = []
    for or_tokens in ors:
        phrases.append(_phrase_parser(or_tokens))
    # In the degenerate case where there is only one operand
    # we just return the operand (or(q) == q)
    if len(phrases) == 1:
        return phrases[0]
    else:
        return {"@type": "PathOr", "or": phrases}


def _group(tokens):
    group = []
    depth = 0

    while depth >= 0 and not (tokens == []):
        tok = tokens.pop(0)
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1

        group.append(tok)

    if depth < 1:
        tokens.append(group.pop())
    return group


def _phrase_parser(tokens):
    result = None
    while not (tokens == []):
        token = tokens.pop(0)
        if token == "(":
            group = _group(tokens)
            result = _path_tokens_to_json(group)
        elif token == ")":
            return result
        elif token == "<":
            token = tokens.pop(0)
            result = {"@type": "InversePathPredicate", "predicate": token}
        elif token == ">":
            result = result
        elif token == ".":
            result = {"@type": "PathPredicate"}
        elif token == "*" and result is not None:
            result = {"@type": "PathStar", "star": result}
        elif token == "+" and result is not None:
            result = {"@type": "PathPlus", "plus": result}
        elif token == "{" and result is not None:
            n = int(tokens.pop(0))
            comma = tokens.pop(0)
            if not comma == ",":
                raise ValueError("incorrect separation in braced path pattern")
            m = int(tokens.pop(0))
            close_brace = tokens.pop(0)
            if not close_brace == "}":
                raise ValueError("no matching brace in path pattern")
            result = {"@type": "PathTimes", "from": n, "to": m, "times": result}
        else:
            result = {"@type": "PathPredicate", "predicate": token}
    return result


def _path_tokenize(pat):
    """Tokenizes the pattern into a sequence of tokens which may be clauses or operators"""
    lexer = r"[@:_\w'%]+|[\.\|\+\*\{\}\,\(\)<>]"
    return re.findall(lexer, pat)


def _copy_dict(orig, rollup=None):
    if type(orig) is list:
        return orig
    if rollup:
        if orig.get("@type") == "And":
            if not orig.get("and") or not len(orig["and"]):
                return {}
            if len(orig["and"]) == 1:
                return _copy_dict(orig["and"][0], rollup)
        if orig.get("@type") == "Or":
            if not orig.get("or") or not len(orig["or"]):
                return {}
            if len(orig["or"]) == 1:
                return _copy_dict(orig["or"][0], rollup)
        if "query" in orig and orig["@type"] != "Comment":
            if type(orig["query"]) is tuple:
                orig["query"] = orig["query"][0].to_dict()
            if not orig["query"].get("@type"):
                return {}
        if "consequent" in orig:
            if not orig["consequent"].get("@type"):
                return {}
    nuj = {}
    for key, part in orig.items():
        if type(part) is list:
            nupart = []
            for item in part:
                if type(item) is dict:
                    sub = _copy_dict(item, rollup)
                    if sub:
                        nupart.append(sub)
                else:
                    nupart.append(item)
            nuj[key] = nupart
        elif type(part) is dict:
            query = _copy_dict(part, rollup)
            if query:
                nuj[key] = query
        else:
            nuj[key] = part
    return nuj
