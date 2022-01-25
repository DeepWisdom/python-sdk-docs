# 项目(Project)
## 创建/删除项目
1. 目前支持从现有的数据集创建项目(`create_from_dataset`) 和 直接从项目id创建项目(`create_from_id`)
2. 通过项目项目id可删除对应的项目(`delete`)
3. 项目高级设置更新(`update_advance_settings`)

## 项目训练
1. 开始训练(`train`)。 支持开始，并等待训练完成(`wait_train`)
2. 查询训状态(`check_train_finish`)
3. 终止训练(`terminate_train`)

## 项目的训练结果
1. 获取实验列表(`trial_list`)
2. 获取方案列表(`solution_list`), 注意不一定所有的实验都有方案
3. 获取可以部署的模型列表(`get_select_models`)， 这里的模型id、模型名称用于离线预测和部署的入参
4. 直接获取推荐的模型(`recommended_select_model`)

## 项目详情
1. 目前详情信息为Project的成员变量，没有暴露更多的信息

## 搜索空间
1. 支持高级配置中搜索空间的配置
2. 获取指定模态任务的搜索空间`SearchSpace.create`
3. 指定搜索空间的model`SearchSpace.custom_model_hp`
4. 例子参照example中的主流程用例