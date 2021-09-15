# TerminusDB Python Client Release Notes

## v10.0.5

### Bug Fixes / Improvements

- Patch formating for DatabaseError

---


## v10.0.4

### Bug Fixes / Improvements

- URL parse all the user provide parameters that will be put into paths

---

## v10.0.3

### Bug Fixes / Improvements

- `_abstract` is now not inherited
- Forcing Database Error to print out the whole response from backend

---

## v10.0.2

### Bug Fixes / Improvements

- Fixing key problems for self/future referencing: backend currently not support id capture and work around by generate id in the client and suspend the `@key` in the schema

---

## v10.0.1

### Bug Fixes / Improvements

- Fixing key problems in Scaffolding tool

---

## v10.0.0

### New

- WOQLClient:
  - works with new document interface api
- woql_schema:
  - sub-module to create schema in document interface
- scrpits:
  - sub-module to provide CLI and Scaffolding tool for setting up project and working with document interface

### Changes

- WOQLQuery:
  - deprecate `doctype` - use document interface instead
- WOQLLib:
  - deprecated - use document interface instead

### Bug Fixes / Improvements

- WOQLQuery:
  - fix path queries
  - update to work with new version of TerminusDB

---

## v1.1.0

### New

- Add WOQLClient.get_commit_history()

### Changes

- Remove functionality of WOQLClient.commit(), WOQLClient.rollback()
- Make import of pandas and numpy of WOQLDataFrame dynamic

### Bug Fixes / Improvements

- "doc:" prefix fix
- check for database connectivity
- literal option added in WOQLQuery.cast()

---

## v1.0.0 🐮☘️

### New

- Rewrite on WOQLClient to simplify structure
- Minor WOQLClient API changes (may not be compatible with previous versions)

### Changes

- Deprecate WOQLClient.user_account() and WOQLClient.uid()
- WOQLClient.delete_database() requires database name and optional account name
- WOQLClient.db() and WOQLClient.account() no longer takes argument to change setting
- Some of the WOQLClient methods no longer return result from backend API
- change of DatabaseError and APIError attributes, added new Error object
- change of the pull, push, rebase and clone API call

### Bug Fixes / Improvements

- WOQLView now works in non-Jupyter interpreter except for WOQLView().show
- Fix transcriptions of true()
- Better error handling
- Fix WOQLClient.create_graph() and WOQLClient.delete_graph()

---

## v0.6.0

### New

- Adding commit(), close() and rollback() for the WOQLClient

### Bug Fixes / Improvements

- Rewrite of WOQLClient, deprecate connectionConfig and connectionCapabilities

---

## v0.5.0

### New

- Added typeof to python
- Add default commit message of update csv and insert csv
- Adding context path to Using to match with the newest version of TerminusDB
- Add once query type
- Adding update triple and update quad

### Bug Fixes / Improvements

- Fixed iri casting
- Fixed group by and iri by default in third part

---

## v0.4.0

### New

- Added WOQLView
- Added csv io methods in WOQLClient

### Bug Fixes / Improvements

- Warning for using WOQLDataFrame.query_to_df()
- WOQLDataFrame now can handle "xsd:date" datatype from TerminusDB
- Automatically csting datetime.date and datetime.datetime object as "xsd:dateTime" when added to TerminusDB

---

## v0.3.1

### Bug Fixes / Improvements

 - Patch import error

## v0.3.0

### New

- Updated create database to take advantage of default prefixes and schema graph creation happening on server
- Integrated all Revision Control API operations fully
- .vars() method - add v: to woql variables
- Reset allowing you to reset a branch to an arbitrary commit
- Post method for CSV uploads
- Triple endpoint for inserting turtle data directly to a graph
- Count triples functionality added
- [beta] Smart Query which creates and checks all the classes and object in Python

### Bug Fixes / Improvements

- Added 3 varities of ordering specification as optional arguments to order_by
- fixed bug to make order_by("desc") work
- Empty selects no longe error

---
## v0.2.2

### New
- adding boolean method in WOQLQuery
- adding dataType mapping for boolean so now "boolean" will be register as "xsd:boolean" in WOQLQuery

---
## v0.2.1

### Bug fixes
- bug fix for delete_database in WOQLClient

---
## v0.2.0

### New
- added `+` operator for WOQLQuery object.
- update connectionCapabilities to match with TerminusDB 2.0.5

---
## v0.1.5

### Bug fixes

- Remove unwanted `print`

---
## v0.1.4

### New
First release of the WOQL standard library - available via WOQLLib class.
Added working versions of clone, pull, push, fetch to API
Added support for basic auth to remote servers
Added set_db() in WOQLClient

### Bug fixes
Fixed bugs in cardinality operators in WOQL (max, min, card - all now work properly)

Tidied up triplebuilder by eliminating no longer need object.

Fixed transmission of prefixes over API
