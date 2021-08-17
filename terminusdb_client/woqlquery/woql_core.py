# helper functions for WOQLCore


def _get_clause_and_remainder(pat):
    """Breaks a graph pattern up into two parts - the next clause, and the remainder of the string
    Parameters
    ----------
    pat: str
         graph pattern fragment
    """
    pat = pat.strip()
    opening = 1
    # if there is a parentheses, we treat it as a clause and go to the end
    if pat[0] == "(":
        for idx, char in enumerate(pat[1:]):
            if char == "(":
                opening += 1
            elif char == ")":
                opening -= 1
            if opening == 0:
                rem = pat[idx + 2 :].strip()
                if rem:
                    return [pat[1 : idx + 1], rem]
                return _get_clause_and_remainder(pat[1:idx])
                # whole thing surrounded by parentheses, strip them out and reparse
        return []
    if pat[0] == "+" or pat[0] == "*" or pat[0] == "," or pat[0] == "|":
        ret = [pat[0]]
        if pat[1:]:
            ret.append(pat[1:])
        return ret
    if pat[0] == "{":
        close_idx = pat.find("}") + 1
        ret = [pat[:close_idx]]
        if pat[close_idx:]:
            ret.append(pat[close_idx:])
        return ret
    for idx, char in enumerate(pat[1:]):
        if char in [",", "|", "+", "*", "{"]:
            return [pat[: idx + 1], pat[idx + 1 :]]
    return [pat]


def _tokenize(pat):
    """Tokenizes the pattern into a sequence of tokens which may be clauses or operators"""
    parts = _get_clause_and_remainder(pat)
    seq = []
    while len(parts) == 2:
        seq.append(parts[0])
        parts = _get_clause_and_remainder(parts[1])
    seq.append(parts[0])
    return seq


def _tokens_to_json(seq, query):
    """Turns a sequence of tokens into the appropriate JSON-LD
    Parameters
    ----------
    seq: list
    query: WOQLQuery"""
    if len(seq) == 1:  # may need to be further tokenized
        ntoks = _tokenize(seq[0])
        if len(ntoks) == 1:
            tok = ntoks[0].strip()
            return _compile_predicate(tok, query)
        else:
            return _tokens_to_json(ntoks, query)
    elif "|" in seq:  # binds most loosely
        left = seq[: seq.index("|")]
        right = seq[seq.index("|") + 1 :]
        return {
            "@type": "PathOr",
            "or": [_tokens_to_json(left, query), _tokens_to_json(right, query)],
        }
    elif "," in seq:  # binds tighter
        first = seq[: seq.index(",")]
        second = seq[seq.index(",") + 1 :]
        return {
            "@type": "PathSequence",
            "sequence": [_tokens_to_json(first, query), _tokens_to_json(second, query)],
        }
    elif seq[1] == "+":  # binds tightest of all
        return {
            "@type": "PathPlus",
            "plus": _tokens_to_json([seq[0]], query),
        }
    elif seq[1] == "*":  # binds tightest of all
        return {
            "@type": "PathStar",
            "star": _tokens_to_json([seq[0]], query),
        }
    elif seq[1][0] == "{":  # binds tightest of all
        meat = seq[1][1:-1].split(",")
        return {
            "@type": "PathTimes",
            "from": int(meat[0]),
            "to": int(meat[1]),
            "times": _tokens_to_json([seq[0]], query),
        }
    else:
        query._parameter_error("Pattern error - could not be parsed " + seq[0])
        return {
            "@type": "PathPredicate",
            "rdfs:label": "failed to parse query " + seq[0],
        }


def _compile_predicate(pp, query):
    if "<" in pp and ">" in pp:
        pred = pp[1:-1]
        cleaned = query._clean_path_predicate(pred)
        return {
            "@type": "PathOr",
            "or": [
                {
                    "@type": "InversePathPredicate",
                    "predicate": cleaned,
                },
                {
                    "@type": "PathPredicate",
                    "predicate": cleaned,
                },
            ],
        }
    elif "<" in pp:
        pred = pp[1:]
        cleaned = query._clean_path_predicate(pred)
        return {
            "@type": "InversePathPredicate",
            "predicate": cleaned,
        }
    elif ">" in pp:
        pred = pp[:-1]
        cleaned = query._clean_path_predicate(pred)
        return {"@type": "PathPredicate", "predicate": cleaned}
    else:
        pred = query._clean_path_predicate(pp)
        return {"@type": "PathPredicate", "predicate": pred}


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
