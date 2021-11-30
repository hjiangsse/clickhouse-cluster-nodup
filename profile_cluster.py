from datetime import timedelta
from datetime import datetime
from clickhouse_driver import Client
import time

def gen_insert_string(start_stamp, records_num):
    insert_str = ""
    start_timestamp = datetime.strptime(start_stamp, "%Y-%m-%d %H:%M:%S")
    for i in range(records_num):
        cur_timestamp = start_timestamp + timedelta(seconds=i)
        cur_string = "This is just a test string"
        cur_value = 0.12335

        cur_insert_value = "(\'" + str(cur_timestamp) + "\',"
        cur_insert_value += "\'" + cur_string + "\',"
        cur_insert_value += str(cur_value) + ")"

        insert_str += cur_insert_value + ","
    return insert_str[0:-1]

if __name__ == "__main__":
    client = Client(host="192.168.222.221")
    database = "mydb"
    table = "mar11"
    record_num = 500 * 10000

    start = time.time()
    insert_values = gen_insert_string("2005-01-01 00:00:00", record_num)
    print("insert value string gen cost: ", time.time() - start)

    insert_query = "insert into " + database + "." + table + " Values " + insert_values
    start = time.time()
    client.execute(insert_query)
    print("insert query cost: ", time.time() - start)

    select_query = "select * from " + database + "." + table #+ " limit " + str(record_num)
    start = time.time()
    client.execute(select_query)
    print("select query cost: ", time.time() - start)