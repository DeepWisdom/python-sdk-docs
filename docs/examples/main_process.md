# 主流程
```python
import deepwisdom as dw

if __name__ == "__main__":
    api_client = dw.Client(appid="your appid", api_key="your api key", secret_key="your secret key")
    dw.set_client(client=api_client)

    train_dataset = dw.Dataset.create(file_path="path to train", stage="train")
    automl = dw.AutoML.create(dataset=train_dataset, name="sdk-demo", label_col="k", time_col="g")
    automl.train()

    test_dataset = dw.Dataset.create(file_path="path to test", stage="test")
    eval_res = automl.evaluate(test_dataset)

    service = dw.Deployment.create(project=automl, name="sdk-demo")
    ret = service.call_service()

```