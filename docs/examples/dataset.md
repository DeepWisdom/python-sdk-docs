
# 数据(Dataset)

## 从数据源创建数据集
```python
import deepwisdom as dw

# 初始化api客户端， 传入申请的appid, api_key, secret_key
api_client = dw.Client(appid=4, api_key="xx", secret_key="xxx")
dw.set_client(client=api_client)

datasets = dw.Dataset.create(
            str_conn='{"host":"xxx","port":"xxx","user":"root","password":"","db":""}',  # mysql/hive
            cloud_type=0,  # 云类型: 0本地, 1Amazon, 2阿里云, 3腾讯云, 4华为云
            source=5,  # 数据来源: 0本地文件, 1mysql, 2oracle, 3mariadb, 4hdfs, 5hive
            chosed_tables='[{"autotables":[{"table_name":"dataset_update_record"},{"table_name":"scene"}]}]'  # 选择的table 列表。 autotables代表db，dataset_update_record|scene代表autotable下的两个表,支持多层嵌套 
        )
```
