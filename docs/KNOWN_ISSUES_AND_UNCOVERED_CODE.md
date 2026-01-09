# Known Issues and Uncovered Code

**Status**: Documentation of bugs, peculiarities, and technical debt for future iteration in the Python client
**Date**: January 2026

This document comes from improving test coverage in the python client and exists to document issues that remain to be addressed. 

## Overview

This document catalogs known issues, bugs, peculiarities, and uncovered code paths in the TerminusDB Python client. Issues are organized by category and client area to facilitate future systematic fixes.

---

## 1. Known Bugs

### 1.1 Query Builder - Args Introspection Issues

**Area**: `woqlquery/woql_query.py`  
**Severity**: Medium  
**Lines**: 1056, 1092, 1128, 1775, 1807

**Issue**: Quad methods (`quad`, `added_quad`, `removed_quad`, `delete_quad`, `add_quad`) attempt to call `.append()` or `.concat()` on `WOQLQuery` objects when handling args introspection which is a deprecated feature that is inconsistently implemented across javascript and python (disabled in the javascript client).

**Details**:
- When `sub == "args"`, methods call `triple()` which returns a `WOQLQuery` object
- Code then tries: `return arguments.append("graph")` or `return arguments.concat(["graph"])`
- `WOQLQuery` objects don't have `append()` or `concat()` methods
- Should return a list like: `return triple_args + ["graph"]`

**Blocked Tests**:
- `test_woql_graph_operations.py::test_removed_quad_with_args_subject`
- `test_woql_graph_operations.py::test_added_quad_with_args_subject`
- `test_woql_path_operations.py::test_quad_with_special_args_subject`

**Impact**: Args introspection feature doesn't work for quad operations

---

### 1.2 Query Builder - Missing Method

**Area**: `woqlquery/woql_query.py`  
**Severity**: Medium  
**Line**: 3230

**Issue**: `graph()` method calls non-existent `_set_context()` method.

**Details**:
- Line 3230: `return self._set_context({"graph": g})`
- Method `_set_context()` is not defined in the class
- Should directly set context: `self._triple_builder_context["graph"] = g`

**Blocked Tests**:
- `test_woql_graph_operations.py::test_graph_method_basic`
- `test_woql_graph_operations.py::test_graph_with_subquery`
- `test_woql_graph_operations.py::test_multiple_graph_operations`

**Impact**: Graph context setting is completely broken

---

### 1.3 Query Validation - Unreachable Logic

**Area**: `woqlquery/woql_query.py`  
**Severity**: High  
**Lines**: 784-785, 821-822

**Issue**: Logically impossible validation conditions prevent proper error handling.

**Details**:
```python
# Line 784 in select() method:
if queries != [] and not queries:
    raise ValueError("Select must be given a list of variable names")

# Line 821-822 in distinct() method:
if queries != [] and not queries:
    raise ValueError("Distinct must be given a list of variable names")
```

**Analysis**:
- After `queries = list(args)`, queries is always a list
- If `queries == []`, then `queries != []` is False
- If `queries != []`, then `not queries` is False
- Condition can never be True, so ValueError is never raised
- Should be: `if not queries:` or `if len(queries) == 0:`

Same issue across both. Probably `select()` should allow to have no variables (to verify against terminusdb), and `distinct()` should have at least one variable (it can't be distinct otherwise…).

**Blocked Tests**:
- `test_woql_schema_validation.py::test_select_with_no_arguments_should_raise_error`

**Impact**: Invalid queries with no arguments are not properly validated

---

### 1.4 From Method - Cursor Wrapping Edge Case

**Area**: `woqlquery/woql_query.py`  
**Severity**: Low  
**Line**: 907

**Issue**: The `woql_from()` method's cursor wrapping logic is not covered by tests.

**Details**:
```python
# Line 906-907 in woql_from() method:
if self._cursor.get("@type"):
    self._wrap_cursor_with_and()  # Line 907 - uncovered
```

**Analysis**:
- Line 907 wraps the existing cursor with an `And` operation when the cursor already has a `@type`
- This is defensive programming to handle chaining `from()` after other operations
- JavaScript client has identical logic: `if (this.cursor['@type']) this.wrapCursorWithAnd();`
- Test attempts `query.limit(10).start(5)` but doesn't test `from()` with existing cursor

**Correct Test Scenario**:
```python
query = WOQLQuery()
query.triple("v:X", "v:P", "v:O")  # Set cursor @type
result = query.woql_from("admin/mydb")  # Should trigger line 907
```

**Blocked Tests**:
- `test_woql_advanced_features.py::test_subquery_with_limit_offset` (incorrectly named/implemented)

**Impact**: Low - defensive code path, basic functionality works

---

## 2. Deprecated Code (Technical Debt)

### 2.1 Data Value List Method

**Area**: `woqlquery/woql_query.py`  
**Severity**: Low (Dead Code)  
**Lines**: 357-361

**Issue**: `_data_value_list()` method is never called anywhere in the codebase.

**Details**:
- Method exists but has no callers
- Similar functionality exists in `_value_list()` which is actively used
- Originally had a bug (called `clean_data_value` instead of `_clean_data_value`)
- Bug was fixed but method remains unused

**Blocked Tests**:
- `test_woql_path_operations.py::test_data_value_list_with_various_types`
- `test_woql_query_builder.py::test_data_value_list_with_mixed_items`

**Recommendation**: Remove in future major version after deprecation period

---

## 3. Uncovered Edge Cases

### 3.1 Args Introspection Paths

**Area**: `woqlquery/woql_query.py`  
**Lines**: 907, 1572, 1693, 2301, 2560, 2562, 2584, 2586, 2806, 2832, 2836, 2877, 2897, 2932, 2957, 2959, 3001, 3008, 3015, 3021, 3062, 3065, 3108, 3135, 3137, 3157, 3159, 3230

**Issue**: Args introspection feature (when first param == "args") is not covered by tests for many methods.

**Details**:
- Args introspection allows API discovery by passing "args" as first parameter
- Methods return list of parameter names instead of executing
- Many methods have this feature but it's not tested
- Tests exist in `test_woql_remaining_edge_cases.py` but some paths remain uncovered

**Methods Affected**:
- `woql_or()` (907)
- `start()` (1572)
- `comment()` (1693)
- `limit()` (2301)
- `get()` (2560)
- `put()` (2562)
- `file()` (2584)
- `remote()` (2586)
- Math operations: `minus()`, `divide()`, `div()` (2806, 2832, 2836)
- Comparison: `less()`, `lte()` (2877, 2897)
- Logical: `once()`, `count()`, `cast()` (2932, 2957, 2959)
- Type operations: `type_of()`, `order_by()`, `group_by()`, `length()` (3001, 3008, 3015, 3021)
- String operations: `lower()`, `pad()` (3062, 3065)
- Regex: `split()`, `regexp()`, `like()` (3108, 3135, 3137)
- Substring operations (3157, 3159)
- `trim()` (3230)

**Impact**: Low - feature works but lacks test coverage

---

### 3.2 As() Method Edge Cases

**Area**: `woqlquery/woql_query.py`  
**Lines**: 1490-1495, 1501, 1508

**Issue**: Complex argument handling in `woql_as()` method not fully covered.

**Details**:
- Lines 1490-1495: List of lists with optional type parameter
- Line 1501: XSD prefix in second argument
- Line 1508: Objects with `to_dict()` method

**Impact**: Low - basic functionality tested, edge cases uncovered

---

### 3.3 Cursor Wrapping Edge Cases

**Area**: `woqlquery/woql_query.py`  
**Lines**: 2652, 2679, 2713

**Issue**: `_wrap_cursor_with_and()` calls when cursor already has @type.

**Details**:
- `join()` line 2652
- `sum()` line 2679
- `slice()` line 2713

**Impact**: Low - defensive programming, rarely triggered

---

### 3.4 Utility Method Edge Cases

**Area**: `woqlquery/woql_query.py`  
**Lines**: 3247-3254, 3280-3283, 3328-3358

**Issue**: Complex utility methods with uncovered branches.

**Details**:
- Lines 3247-3254: `_find_last_subject()` with And query iteration
- Lines 3280-3283: `_same_entry()` dictionary comparison
- Lines 3328-3358: `_add_partial()` triple builder context logic

**Impact**: Low - internal utilities, basic paths covered

---

### 3.5 Vocabulary and Type Handling

**Area**: `woqlquery/woql_query.py`  
**Lines**: 338, 706, 785, 3389

**Issue**: Specific edge cases in type and vocabulary handling.

**Details**:
- Line 338: `_clean_arithmetic()` with dict having `to_dict` method
- Line 706: Vocabulary extraction with prefixed terms
- Line 785: Select validation (see bug 1.3)
- Line 3389: Final line of file (likely closing brace or comment)

**Impact**: Very Low - rare edge cases

---

## 4. Infrastructure and Integration Issues

### 4.1 Cloud Infrastructure Tests

**Area**: `integration_tests/`  
**Severity**: N/A (External Dependency)

**Issue**: TerminusX cloud infrastructure no longer operational (use DFRNT.com instead)

**Skipped Tests**:
- `test_client.py::test_diff_ops_no_auth`
- `test_client.py::test_terminusx`
- `test_client.py::test_terminusx_crazy_path`
- `test_scripts.py::test_script_happy_path`

**Impact**: Cannot test cloud integration features

---

### 4.2 JWT Authentication Tests

**Area**: `integration_tests/test_client.py`  
**Severity**: N/A (Optional Feature)

**Issue**: JWT tests require environment variable `TERMINUSDB_TEST_JWT=1`.

**Skipped Tests**:
- `test_client.py::test_jwt`

**Impact**: JWT authentication not tested in CI

---

## 5. Schema and Type System Peculiarities

### 5.1 Relaxed Type Checking

**Area**: `test_Schema.py`  
**Severity**: N/A (Design Decision)

**Issue**: Type constraints intentionally relaxed.

**Skipped Tests**:
- `test_Schema.py::test_abstract_class`
- `test_Schema.py::test_type_check`

**Details**: Tests skipped with reason "Relaxing type constraints" and "relaxing type checking"

**Impact**: Type system is more permissive than originally designed

---

### 5.2 Backend-Dependent Features

**Area**: `test_Schema.py`  
**Severity**: N/A (Backend Dependency)

**Issue**: Import objects feature requires backend implementation.

**Skipped Tests**:
- `test_Schema.py::test_import_objects`

**Impact**: Cannot test object import without backend

---

### 5.3 Client Triple Retrieval

**Area**: `test_Client.py`  
**Severity**: N/A (Temporarily Unavailable)

**Issue**: Triple retrieval features temporarily unavailable.

**Skipped Tests**:
- `test_Client.py::test_get_triples`
- `test_Client.py::test_get_triples_with_enum`

**Impact**: Cannot test triple retrieval functionality

---

## 6. Summary Statistics

### Coverage Metrics
- **Total Lines**: 1478
- **Covered Lines**: 1388
- **Uncovered Lines**: 90
- **Coverage**: 94%

### Test Metrics
- **Total Tests**: 1356 passing
- **Skipped Tests**: 20
- **Test Files**: 50+

### Issue Breakdown
- **Critical Bugs**: 3 (validation logic, missing method, args introspection)
- **Deprecated Code**: 1 (dead code to remove)
- **Uncovered Edge Cases**: 60+ lines (mostly args introspection)
- **Infrastructure Issues**: 5 (cloud/JWT tests)
- **Design Decisions**: 4 (relaxed constraints, backend dependencies)

---

## 7. Recommendations for Future Iteration

### High Priority
1. **Fix validation logic** (lines 784-785, 821-822) - Critical for query correctness
2. **Implement `_set_context()` or fix `graph()` method** (line 3230) - Broken feature
3. **Fix quad args introspection** (lines 1056, 1092, 1128, 1775, 1807) - Consistent API

### Medium Priority
4. **Add tests for args introspection** - Improve coverage to 95%+
5. **Investigate subquery limit/offset** (line 903) - Unknown issue
6. **Document type system decisions** - Clarify relaxed constraints

### Low Priority
7. **Remove deprecated `_data_value_list()`** - Clean up dead code
8. **Add edge case tests** - Cover remaining utility methods
9. **Document cloud infrastructure status** - Update integration test docs

### Future Considerations
10. **JWT test automation** - Add to CI pipeline
11. **Backend integration tests** - Coordinate with backend team
12. **Triple retrieval feature** - Investigate "temporarily unavailable" status

---

## 8. Maintenance Notes

**Last Updated**: January 2026  
**Next Review**: After addressing high-priority bugs  

**Note**: This document should be updated whenever:
- Bugs are fixed (move to resolved section)
- New issues are discovered
- Coverage improves
- Design decisions change
