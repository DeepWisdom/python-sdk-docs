
# 项目(Project)

## 创建项目
```python
import deepwisdom as dw

if __name__ == "__main__":
    api_client = dw.Client(appid="your appid", api_key="your api key", secret_key="your secret key")
    dw.set_client(client=api_client)
    
    # 数据集
    dataset = dw.Dataset.create_from_file(filename="path to train", dataset_type=1, modal_type=0)
    
    primary_label = "X"
    project_name = "SDK-PROJECT-DEMO"
    train_setting = dw.TrainSetting(training_program="deepwisdom", max_trials=3)
    # 获取模态任务的搜索空间
    ss = dw.SearchSpace.create(model_type=0, task_type=0)
    # 指定搜索空间的model
    ss.custom_model_hp(["LIGHTGBM", "CATBOOST"])
    settings = dw.AdvanceSetting(gp_switch="off", optimizer="ga", random_seed=6571, target_train=train_setting, 
                                 search_space=ss.search_space_info)
    dataset_id = dataset.dataset_id
    # 基于数据集创建项目
    project = dw.Project.create_from_dataset(name=project_name, dataset_id=dataset_id, modal_type=0, task_type=0,
                                             scene=1, primary_label=primary_label, primary_main_time_col="",
                                             advance_settings=settings, search_space_id=ss.search_space_id)
    ...
   
```
