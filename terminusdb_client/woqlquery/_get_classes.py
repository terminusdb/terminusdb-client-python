from terminusdb_client import WOQLQuery, WOQLLib, WOQLClient

import pprint as pp

server_url = "https://127.0.0.1:6360"
user = "admin"
account = "admin"
key = "root"
dbid = "pybike"
repository = "local"

client = WOQLClient(server_url)
client.connect(user=user,account=account,key=key,db=dbid)

result = WOQLLib().property().execute(client)

pp.pprint(result)
