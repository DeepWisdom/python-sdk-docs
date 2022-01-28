
# 数据(Dataset)

## 从数据源创建数据集
```python
import deepwisdom as dw

if __name__ == "__main__":
    api_client = dw.Client(appid="your appid", api_key="your api key", secret_key="your secret key")
    dw.set_client(client=api_client)
    
    datasets = dw.Dataset.create(
                str_conn='{"host":"xxx","port":"xxx","user":"root","password":"","db":""}',  # mysql/hive
                cloud_type=dw.CLOUD_TYPE.LOCAL,  
                source=dw.DATA_SOURCE.HIVE,  
                chosed_tables='[{"autotables":[{"table_name":"dataset_update_record"},{"table_name":"scene"}]}]'  # 选择的table 列表。 autotables代表db，dataset_update_record|scene代表autotable下的两个表,支持多层嵌套 
            )
```
