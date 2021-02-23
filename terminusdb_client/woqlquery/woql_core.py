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
    if pat[0] == "+" or pat[0] == "," or pat[0] == "|":
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
        if char in [",", "|", "+", "{"]:
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
            "@type": "woql:PathOr",
            "woql:path_left": _tokens_to_json(left, query),
            "woql:path_right": _tokens_to_json(right, query),
        }
    elif "," in seq:  # binds tighter
        first = seq[: seq.index(",")]
        second = seq[seq.index(",") + 1 :]
        return {
            "@type": "woql:PathSequence",
            "woql:path_first": _tokens_to_json(first, query),
            "woql:path_second": _tokens_to_json(second, query),
        }
    elif seq[1] == "+":  # binds tightest of all
        return {
            "@type": "woql:PathPlus",
            "woql:path_pattern": _tokens_to_json([seq[0]], query),
        }
    elif seq[1][0] == "{":  # binds tightest of all
        meat = seq[1][1:-1].split(",")
        return {
            "@type": "woql:PathTimes",
            "woql:path_minimum": {"@type": "xsd:positiveInteger", "@value": meat[0]},
            "woql:path_maximum": {"@type": "xsd:positiveInteger", "@value": meat[1]},
            "woql:path_pattern": _tokens_to_json([seq[0]], query),
        }
    else:
        query._parameter_error("Pattern error - could not be parsed " + seq[0])
        return {
            "@type": "woql:PathPredicate",
            "rdfs:label": "failed to parse query " + seq[0],
        }


def _compile_predicate(pp, query):
    if "<" in pp and ">" in pp:
        pred = pp[1:-1]
        cleaned = (
            "owl:topObjectProperty"
            if pred == "*"
            else query._clean_path_predicate(pred)
        )
        return {
            "@type": "woql:PathOr",
            "woql:path_left": {
                "@type": "woql:InvertedPathPredicate",
                "woql:path_predicate": {"@id": cleaned},
            },
            "woql:path_right": {
                "@type": "woql:PathPredicate",
                "woql:path_predicate": {"@id": cleaned},
            },
        }
    elif "<" in pp:
        pred = pp[1:]
        cleaned = (
            "owl:topObjectProperty"
            if pred == "*"
            else query._clean_path_predicate(pred)
        )
        return {
            "@type": "woql:InvertedPathPredicate",
            "woql:path_predicate": {"@id": cleaned},
        }
    elif ">" in pp:
        pred = pp[:-1]
        cleaned = (
            "owl:topObjectProperty"
            if pred == "*"
            else query._clean_path_predicate(pred)
        )
        return {"@type": "woql:PathPredicate", "woql:path_predicate": {"@id": cleaned}}
    else:
        pred = "owl:topObjectProperty" if pp == "*" else query._clean_path_predicate(pp)
        return {"@type": "woql:PathPredicate", "woql:path_predicate": {"@id": pred}}


def _copy_dict(orig, rollup=None):
    if type(orig) is list:
        return orig
    if rollup:
        if orig.get("@type") in ["woql:And", "woql:Or"]:
            if not orig.get("woql:query_list") or not len(orig["woql:query_list"]):
                return {}
            if len(orig["woql:query_list"]) == 1:
                return _copy_dict(orig["woql:query_list"][0]["woql:query"], rollup)
        if "woql:query" in orig and orig["@type"] != "woql:Comment":
            if type(orig["woql:query"]) is tuple:
                orig["woql:query"] = orig["woql:query"][0].to_dict()
            if not orig["woql:query"].get("@type"):
                return {}
        if "woql:consequent" in orig:
            if not orig["woql:consequent"].get("@type"):
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
                    nupart = nupart.append(item)
            nuj[key] = nupart
        elif type(part) is dict:
            query = _copy_dict(part, rollup)
            if query:
                nuj[key] = query
        else:
            nuj[key] = part
    return nuj
