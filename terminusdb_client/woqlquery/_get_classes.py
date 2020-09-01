import pprint as pp

from terminusdb_client import WOQLClient, WOQLLib

server_url = "https://127.0.0.1:6360"
user = "admin"
account = "admin"
key = "root"
dbid = "pybike"
repository = "local"

client = WOQLClient(server_url)
client.connect(user=user, account=account, key=key, db=dbid)

result = WOQLLib().property().execute(client)

pp.pprint(result)
