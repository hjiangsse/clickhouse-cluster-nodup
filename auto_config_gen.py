import sys
import getopt

standby_tcp_port_start = 9001
standby_http_port_start = 8124

master_block_template = """
  ch-master:
    container_name: ch_master
    image: yandex/clickhouse-server:latest
    depends_on:
standby_node_list_str
    ports:
      - 9000:9000
      - 8123:8123
    volumes:
      - type: volume
        source: ch-master-data
        target: /var/lib/clickhouse
      - type: volume
        source: ch-master-logs
        target: /var/log/clickhouse-server
      - ./master-config.xml:/etc/clickhouse-server/config.xml
"""

standby_block_template = """
  ch-sub-index:
    container_name: ch_sub_index
    image: yandex/clickhouse-server:latest
    ports:
      - tcp_port:9000
      - http_port:8123
    volumes:
      - type: volume
        source: ch-sub-index-data
        target: /var/lib/clickhouse
      - type: volume
        source: ch-sub-index-logs
        target: /var/log/clickhouse-server
      - ./sub-config.xml:/etc/clickhouse-server/config.xml
"""

volumns_block_template = """
volumes:
  ch-master-data:
  ch-master-logs:
standby-volumes-str
"""

standby_host_name_prefix = "ch-sub-"

#------------------------------------------------------------------------------
# 生成给docker-compose使用的yaml配置文件
#------------------------------------------------------------------------------
def gen_compose_yml_file(node_num, outpath):
    standby_node_list = []
    standby_block_list = []
    for i in range(node_num):
        standby_node_list.append("ch-sub-" + str(i+1))
        cur_tcp_port = standby_tcp_port_start + i
        cur_http_port = standby_http_port_start + i
        tmp_block = standby_block_template.replace("index", str(i+1))
        tmp_block = tmp_block.replace("tcp_port", str(cur_tcp_port))
        tmp_block = tmp_block.replace("http_port", str(cur_http_port))
        standby_block_list.append(tmp_block)

    standby_node_list_str = ""
    for nodename in standby_node_list:
        standby_node_list_str += "      " + "- " + nodename + "\n"
    standby_node_list_str = standby_node_list_str[0:-1]

    #生成主节点配置块
    master_block_result = master_block_template.replace("standby_node_list_str", standby_node_list_str)

    #生成volumes块
    standby_volumns_str = ""
    for i in range(node_num):
        datastr = "  " + "ch-sub-" + str(i+1) + "-data:" + "\n"
        logstr = "  " + "ch-sub-" + str(i+1) + "-logs:" + "\n"
        standby_volumns_str += datastr
        standby_volumns_str += logstr
    standby_volumns_str = standby_volumns_str[0:-1]

    #生成最终配置文件
    final_config_str = master_block_result 
    for standby_block in standby_block_list:
        final_config_str += standby_block
    
    all_volumes_block = volumns_block_template.replace("standby-volumes-str", standby_volumns_str)
    final_config_str += all_volumes_block

    final_str = "version: \"3.8\"" + "\n\n" + "services:" + "\n" + final_config_str

    with open(outpath, "w+") as file:
        file.write(final_str)

#------------------------------------------------------------------------------
# 生成给clickhouse主节点使用的集群配置信息
#------------------------------------------------------------------------------
def gen_master_cluster_config(node_num, outpath):
    shard_template = """            <shard>
                <replica>
                    <host>ch-sub-index</host>
                    <port>9000</port>
                </replica>
            </shard>
"""
    shard_config_list = []
    shard_config_str = ""
    for i in range(node_num):
        shard_config_list.append(shard_template.replace("index", str(i+1)))

    for shard_config in shard_config_list:
        shard_config_str += shard_config
    
    old_master_config = ""
    with open(outpath, "r") as file:
        old_master_config = file.read()

    start_pos = old_master_config.find("example_cluster") + len("example_cluster") + 1
    end_pos = old_master_config.find("/example_cluster") - 1
    
    first_half = old_master_config[:start_pos]
    second_half = old_master_config[end_pos:]

    with open(outpath, "w+") as file:
        file.write(first_half + "\n" + shard_config_str + "\t\t" + second_half)

#------------------------------------------------------------------------------
# 生成create_cluster.py中的节点信息
#------------------------------------------------------------------------------
def gen_create_cluster(node_num, outpath):
    node_addr_list = []
    node_addr_str = ""
    for i in range(node_num):
        node_addr_list.append("\t" + "(\"127.0.0.1\"," + "\" " +str(9001 + i) + "\"" + "),")

    for node_addr in node_addr_list:
        node_addr_str += node_addr + "\n"
    
    node_addr_str = node_addr_str[0:-1]
    old_file_content = ""
    with open(outpath, "r") as file:
        old_file_content = file.read()

    left_bracket_pos = old_file_content.find("[")
    right_bracket_pos = old_file_content.find("]")
    first_half = old_file_content[0:left_bracket_pos+1]
    second_half = old_file_content[right_bracket_pos:]

    with open(outpath, "w") as file:
        file.write(first_half + "\n" + node_addr_str + "\n" + second_half)

if __name__ == "__main__":
    node_num = 3
    compose_yml_outpath = "./docker-compose.yml"
    master_cluster_config = "./master-config.xml"
    create_cluster_path = "./create-cluster.py"

    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "n:o:m:")
    except:
        print("Error")
  
    for opt, arg in opts:
        if opt in ['-n']:
            node_num = int(arg)
        if opt in ['-o']:
            compose_yml_outpath = arg
        if opt in ['-m']:
            master_cluster_config = arg
        if opt in ['-c']:
            create_cluster_path = arg

    gen_compose_yml_file(node_num, compose_yml_outpath)
    gen_master_cluster_config(node_num, master_cluster_config)
    gen_create_cluster(node_num, create_cluster_path)