# 依赖
python3.9
# 安装/升级
待正式对外发布
# 配置
1. 鉴权通过OAuth2.0, 所以这里要先申请用户的`appid`、`api_key`、`secret_key`
2. 配置方式一：直接通过制定参数的方式实例化api_client， 参考快速开始部分
3. 配置方式二: yaml配置文件， 配置的默认路径为`~./.config/deepwisdom/dwconfig.yaml`, 配置内容如下
```yaml
api_key: "xx"
secret_key: "xxx"
appid: 3
domain: "xxx"
```

# 快速开始
以表格二分类为例
```python
import deepwisdom as dw

if __name__ == "__main__":

    api_client = dw.Client(appid="your_appid", api_key="your_api_key", secret_key="your_secret_key")
    dw.set_client(client=api_client)
    
    train_dataset = dw.Dataset.create(file_path="path_to_train", stage="train")
    automl = dw.AutoML.create(dataset=train_dataset, name="sdk-demo", label_col="k", time_col="g")
    automl.train()
    
    test_dataset = dw.Dataset.create(file_path="path_to_test", stage="test")
    eval_res = automl.evaluate(test_dataset)
    
    service = dw.Deployment.create(project=automl, name="sdk-demo")
    ret = service.call_service()
    
```
# 特性
1. 数据集管理。 包括数据集的增删改查、数据集模糊搜索等
2. 项目管理。 项目的增删改查、训练管理、离线预测、高级设置更新、方案/部署模型列表等
3. 实验管理。 实验详情数据查询，包括耗时、性能和效果指标等
4. 最佳方案。 实验的方案列表及对应的部署模型信息等
5. 离线预测。 获取离线预测列表，进行离线预测等
6. 推理部署。推理服务创建，获取列表，修改常驻状态，修改推理服务名称，调用服务等

# 详细文档
1. API Reference。 
2. tutorials

