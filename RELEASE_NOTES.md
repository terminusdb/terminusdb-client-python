# TerminusDB Python Client Release Notes

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
