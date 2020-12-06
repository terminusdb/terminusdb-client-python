# Create a Schema

To create a schema you need to add a document type and some
properties. First, connect to an existing database. You will want to
make sure this database was created with a schema (the default) rather
than schema free!  For instance, to connect to a database named
`My_First_Schema` you can write the following:

```python
from terminusdb_client.woqlquery.woql_query import WOQLQuery as WQ
from terminusdb_client.woqlclient.woqlClient import WOQLClient

server_url = "https://127.0.0.1:6363"
user = "admin"
account = "admin"
key = "root"
dbid = "My_First_Schema"
repository = "local"

client = WOQLClient(server_url)
client.connect(user=user,account=account,key=key,db=dbid)
```

If you haven't already created the database, you can do so with the
following query:

```python
client.create_database(dbid, label=label, description=description)
```

Once we have a client object, we can proceed with adding a schema to
the database.

```python
address = WQ().woql_and(
    WQ().doctype("Address")
        .label("An address record")
        .description("Record holding address information")
        .property("street", "xsd:string")
            .label("street")
            .cardinality(1)
        .property("city", "xsd:string")
            .label("city")
            .cardinality(1)
        .property("post_code", "xsd:string")
            .label("post code")
            .max(1)

client.query(address, "Adding Address documents to the database")
```

We now have a schema description of what constitutes an address,
replete with documentation of the elements, and information about the
cardinalities of edges in the database.

The `label` groups with the current schema object we are creating and
gives it a human readable name. We can also use `description` to give
a lengthier destription to any of the created schema objects.

When we use `property` we group it with the current class. This
current class is its domain. It comes together with its range as the
second argument after the name. If we have more complex properties
with overlapping ranges it is necessary to create them seperately.

We can use this document type to connect it to other elements in
the graph. For instance, we can create a new person document type as
follows:

```python
person = WQ().woql_and(
    WQ().doctype("Person")
        .label("A digital human twin")
        .description("Record holding information on an individual")
        .property("forename", "xsd:string")
            .label("forename")
            .cardinality(1)
        .property("surname", "xsd:string")
            .label("surname")
            .cardinality(1)
        .property("address", "Address")
            .label("The address(es) associated with an individual"))

client.query(person, "Adding Person record")
```

Now that we have a schema, it is possible to add information to the
graph by inserting documents or triples - as long as they respect the schema!
