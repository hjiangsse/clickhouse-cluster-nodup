from clickhouse_driver import Client

subs = [
	("127.0.0.1"," 9001"),
	("127.0.0.1"," 9002"),
	("127.0.0.1"," 9003"),
	("127.0.0.1"," 9004"),
	("127.0.0.1"," 9005"),
	("127.0.0.1"," 9006"),
	("127.0.0.1"," 9007"),
	("127.0.0.1"," 9008"),
	("127.0.0.1"," 9009"),
	("127.0.0.1"," 9010"),
	("127.0.0.1"," 9011"),
	("127.0.0.1"," 9012"),
	("127.0.0.1"," 9013"),
	("127.0.0.1"," 9014"),
	("127.0.0.1"," 9015"),
	("127.0.0.1"," 9016"),
	("127.0.0.1"," 9017"),
	("127.0.0.1"," 9018"),
	("127.0.0.1"," 9019"),
	("127.0.0.1"," 9020"),
	("127.0.0.1"," 9021"),
	("127.0.0.1"," 9022"),
	("127.0.0.1"," 9023"),
	("127.0.0.1"," 9024"),
	("127.0.0.1"," 9025"),
	("127.0.0.1"," 9026"),
	("127.0.0.1"," 9027"),
	("127.0.0.1"," 9028"),
	("127.0.0.1"," 9029"),
	("127.0.0.1"," 9030"),
]
master = ("127.0.0.1", "9000")

if __name__ == "__main__":
    database_name = "mydb"
    table_name = "mar11"

    for sub in subs:
        client = Client(sub[0], port=sub[1])
        client.execute("CREATE DATABASE IF NOT EXISTS " + database_name)
        client.execute('''CREATE TABLE IF NOT EXISTS my_table (
                          timestamp String,
                          parameter String,
                          value Float64)
                          ENGINE = MergeTree()
                          PARTITION BY parameter
                          ORDER BY (timestamp, parameter)'''.replace("my_table", database_name + "." + table_name))
    
    client = Client(master[0], port=master[1])
    client.execute("CREATE DATABASE IF NOT EXISTS " + database_name)
    master_create_query = '''CREATE TABLE IF NOT EXISTS my_table(
                      timestamp String,
                      parameter String,
                      value Float64)
                      ENGINE = Distributed(example_cluster, database_name, table_name, rand())'''.replace("my_table", database_name + "." + table_name)
    master_create_query = master_create_query.replace("database_name", database_name)
    master_create_query = master_create_query.replace("table_name", table_name)
    client.execute(master_create_query)