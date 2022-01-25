
# 数据(Dataset)
## 创建/删除数据集
1. 从本地数据集文件， 创建数据集对象`create_from_file`
2. 从数据源创建数据集对象`create_from_data_source`
3. 直接从数据集id创建`create_from_dataset_id`
4. 删除指定数据集`delete`

## 查找数据集
1. 支持数据集名称的模糊搜索`dataset_search`

## 数据集信息修改
1. 支持数据集名称的修改`modify_dataset`

## eda
1. 目前只支持表格
2. eda查询`get_eda`
3. eda修改`modify_eda`