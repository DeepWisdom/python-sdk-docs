# -*- coding: utf-8 -*-
"""
推理服务部署

通过 get_deployment_detail 可以快速返回一个deployment对象，而不必直接实例化 Deployment(...)

```
调用服务: 
        deploy = Deployment.get_service(200)
        print(deploy.call_service({}))
---
获取服务列表: 
        deploys = Deployment.list_deployments(3976)
        for deploy in deploys:
            detail = deploy.get_deployment_detail()
        print(deploys)
---
修复服务名称:
        deploy = Deployment.rename_deployment(deploy_id, "test")
```

"""
from typing import List
import trafaret as t
from deepwisdom.models.api_object import APIObject
from deepwisdom.enums import API_URL, SVR_STATUS
from deepwisdom.models.project import Project
import deepwisdom.errors as err
from deepwisdom._compat import Int, String, Any
from dataclasses import dataclass
from typing import Optional, List


# @dataclass
class CreateDeploymentRequest(dict):
    project_id: int  # 项目id
    model_inst_id: int  # 模型id
    name: str  # 服务名
    gpu_mem: int = 2  # gpu显存限制GB
    memory_limit: int = 3  # GB 内存限制
    max_pod: int = 1  # 最大pod数
    min_pod: int = 1  # 最少pod数

    # def __setattr__(self, k, v):
    #     if k in self.__dataclass_fields__:
    #         self[k] = v
    #     super().__setattr__(k, v)
    def __init__(self, project_id, model_inst_id, name, gpu_mem=2, memory_limit=2, min_pod=0, max_pod=1):
        super().__init__(project_id=project_id, model_inst_id=model_inst_id, name=name, gpu_num=0,
                         gpu_mem=gpu_mem, memory_limit=memory_limit, max_pod=max_pod,
                         min_pod=min_pod)


@dataclass
class ServiceApiInfo(APIObject):
    _converter = t.Dict(
        {
            t.Key("http_type"): String,  # 服务调用method,
            t.Key("token"): String,  # 服务调用token,
            t.Key("url"): String,  # 服务url
            t.Key("post_example"): Any,  # 服务调用body demo
            t.Key("data_example"): Any,  # 服务响应data demo
            t.Key("response_example"): Any  # 服务响应body demo
        }
    ).allow_extra("*")
    http_type: str = ""
    token: str = ''
    url: str = ''
    post_example: Any = ''
    data_example: Any = ''
    response_example: Any = None


@dataclass
class Deployment(APIObject):
    _converter = t.Dict(
        {
            t.Key("id", optional=True): Int,
            t.Key("project_id"): Int,
            t.Key("user_id"): Int,
            t.Key("name"): String,  # 服务中文名,
            t.Key("service_name"): String,  # 服务名称-英文,
            t.Key("model_inst_id"): Int,  # 模型id,
            t.Key("serverless_infer_id"): Int,  # 服务部署id,
            t.Key("token"): String,  # 服务调用token,
            t.Key("token_url"): String,  # 服务调用token,
            t.Key("deploy_model", optional=True): String,  # 部署的模型名称,
            t.Key("route_path", optional=True): String,  # 服务调用api
            # t.Key("failed_log", optional=True,default=""): String,  # 服务失败日志
            t.Key("status", optional=True): Int,  # 服务状态
            t.Key("infer_lock", optional=True): Int,
            t.Key("min_pod"): Int,
            t.Key("max_pod"): Int,
            t.Key("create_time"): String,  # 2021-10-27 18:43:12,
            t.Key("update_time"): String,  # 2021-10-27 18:43:12,
            t.Key("deploy_time", optional=True): String,  # 2021-10-27 18:43:12,
            t.Key("is_del"): Int,
        }
    ).allow_extra("*")
    id: int = 0
    project_id: int = 0
    user_id: int = 0
    name: str = ''  # 服务中文名
    service_name: str = ''  # 服务名称-英文
    model_inst_id: int = 0  # 模型id
    serverless_infer_id: int = 0  # 服务部署id
    deploy_model: str = ''  # 部署模型名称
    route_path: str = ''  # 服务调用URL
    token: str = ''  # 服务调用token
    token_url: str = ''
    status: int = 0
    infer_lock: int = 0
    min_pod: int = 0
    max_pod: int = 0
    create_time: str = ''  # 2021-10-27 18:43:12
    update_time: str = ''  # 2021-10-27 18:43:12
    deploy_time: str = ''  # 2021-10-27 18:43:12
    is_del: int = 0

    @classmethod
    def create(cls, project: Optional[Project] = None, name: str = "Untitled Service", gpu_mem: int = 2,
               memory_limit: int = 3, max_pod: int = 1, min_pod: int = 1) -> "Deployment":
        """
        创建服务
        Args:
            project (Project): 项目对象
            name (str): 名称
            gpu_mem (int): gpu显存限制GB
            memory_limit (int): GB 内存限制
            max_pod (int): 最大pod数
            min_pod (int):  最小pod数

        Returns:

        """
        req = CreateDeploymentRequest(project_id=project.project_id, model_inst_id=project.recommended_model().model_id,
                                      name=name, gpu_mem=gpu_mem, memory_limit=memory_limit, max_pod=max_pod,
                                      min_pod=min_pod)

        return cls.create_from_req(req)
        
        

    @classmethod
    def create_from_req(cls, options: CreateDeploymentRequest) -> "Deployment":
        """创建服务

        Args:
            options (CreateDeploymentRequest): 服务创建请求参数

        Returns:
            [Deployment]: 返回具体的服务对象
        """
        data = {}
        data.update(options)
        rsp = cls._client._post(API_URL.DEPLOY_CREATE_SERVICE, data)
        if "data" in rsp and "ret" in rsp["data"] and len(rsp["data"]["ret"]) == 1:
            deployment = cls.from_server_data(rsp['data']["ret"][0])
            # 等待服务部署完成
            while True:
                status = deployment.get_service_status()
                if status == SVR_STATUS.FAIL:
                    raise err.CreateDeploymentError
                if status == SVR_STATUS.RUNNING:
                    return deployment
        else:
            raise err.CreateDeploymentError

    @classmethod
    def get_service(cls, service_id, **kwargs) -> "Deployment":
        """获取服务详情

        Args:
            service_id (int): 服务id
        Returns:
            Deployment: 服务详情
        """
        data = {
            "service_id": service_id
        }
        rsp = cls._server_data(API_URL.DEPLOY_GET_SERVICE_DETAIL, data)
        return cls.from_server_data(rsp)

    @classmethod
    def list_deployments(cls, project_id: int, **kwargs) -> List["DeploymentListMember"]:
        """获取服务部署列表

        Args:
            project_id (int): 项目id

        Returns:
            List[DeploymentListMember]: 服务列表
        """
        data = {
            "project_id": project_id
        }
        server_data = cls._server_data(API_URL.DEPLOY_LIST_DEPLOYMENTS, data)
        # return [cls.get_deployment_detail(item["service_id"]) for item in server_data]
        return [DeploymentListMember(**item) for item in server_data]

    @classmethod
    def resident_deployment(cls, svc_id: int, min_pod: int):
        """切换服务常驻状态

        Args:
            svc_id (int64): 服务id
            min_pod (int): 最少pod数，大于0为服务常驻，等于0为非常驻
        Returns:
            Deployment: 服务详情
        """
        data = {
            "svc_id": svc_id,
            "min_pod": min_pod
        }
        rsp = cls._client._post(API_URL.DEPLOY_RESIDENT_DEPLOYMENT, data)
        if rsp['code'] == 200 and rsp['message'] == 'ok':
            return cls.get_deployment_detail(svc_id)
        return None

    @classmethod
    def delete_deployments(cls, service_ids: List[int]) -> bool:
        """删除服务

        Args:
            service_ids (int64): 服务id
        """
        data = {
            "svc_ids": service_ids
        }
        rsp = cls._client._delete(API_URL.DEPLOY_DELETE_DEPLOYMENT, data)
        if rsp['code'] == 200 and rsp['message'] == 'ok':
            return True
        return False

    @classmethod
    def rename_deployment(cls, svc_id: int, svc_name: str):
        """重命名服务

        Args:
            svc_id (int): 服务id
            svc_name (str): 新服务名称
        Returns:
            Deployment: 服务详情
        """
        data = {
            "svc_id": svc_id,
            "svc_name": svc_name
        }
        rsp = cls._client._patch(API_URL.DEPLOY_RENAME_DEPLOYMENT, data)
        if rsp['code'] == 200 and rsp['message'] == 'ok':
            return cls.get_deployment_detail(svc_id)
        return None

    @classmethod
    def get_deployment_log(cls, svc_id: int) -> str:
        """获取服务日志

        Args:
            svc_id (int): 服务id

        Returns:
            str: 日志内容
        """
        data = {
            "service_id": svc_id
        }
        rsp = cls._client._get(API_URL.DEPLOY_GET_DEPLOYMENT_LOG, data)
        if "data" in rsp:
            return rsp['data']
        return None

    def get_service_status(self) -> Int:
        """获取服务状态

        Returns:
            Int: 服务状态：1-创建，2-调度中，3-调度成功，4-执行中，5-创建失败，6-挂起，7-取消，8-删除中，9- 已删除
        """
        svc = self.get_service(self.id)
        return svc.status

    def call_service(self, data: Any = None) -> Any:
        """调用服务

        Args:
            data (Any): 服务调用入参

        Returns:
            Any: 响应body
        """
        if data is None:
            api_desc = self.get_service_api(self.id)
            data = api_desc.post_example

        header = {
            "Authorization": "Bearer  {}".format(self.token),
            "Content-Type": "application/json; charset=utf-8",
        }
        rsp = self._client.raw_request(
            "post", self.token_url, json=data, headers=header)
        return rsp

    @classmethod
    def get_service_api(cls, svc_id: int) -> ServiceApiInfo:
        """获取服务api

        Args:
            svc_id (int): 服务id

        Returns:
            ServiceApiInfo: api详情
        """
        data = {
            "svc_id": svc_id
        }
        rsp = cls._client._get(API_URL.DEPLOY_GET_SERVICE_API, data)
        if "data" in rsp:
            checked = ServiceApiInfo._converter.check(rsp['data'])
            filtered = Deployment._filter_data(checked)
            return ServiceApiInfo(**filtered)
        return None


@dataclass
class DeploymentListMember(APIObject):
    _converter = t.Dict(
        {
            t.Key("service_id", optional=True): Int,
            t.Key("service_name", optional=True): String,  # 服务中文名,
            t.Key("min_pod"): Int,
            t.Key("model_name"): String,  # 模型名称
            t.Key("trial_no"): Int,  # 训练id
            t.Key("trial_type"): Int,  # 训练类型
            t.Key("recom_model", optional=True): String,  # 推荐的模型名称
            t.Key("eval_metric"): Any,  # 评估指标
            t.Key("service_status"): Int,  # 服务状态
            t.Key("service_create_time"): String,  # 2021-10-27 18:43:12
        }
    ).allow_extra("*")
    service_id: int = 0
    service_name: str = ''  # 服务中文名
    min_pod: int = 0
    model_name: str = ''  # 部署模型名称
    trial_no: int = 0
    trial_type: int = 0
    recom_model: str = ''  # 推荐的模型名称
    eval_metric: Any = ''
    service_status: int = 0
    service_create_time: str = ''  # 2021-10-27 18:43:12

    def get_deployment_detail(self) -> "Deployment":
        """获取服务详情
        Returns:
            Deployment: 服务详情
        """
        data = {
            "service_id": self.service_id
        }
        rsp = self._client._get(API_URL.DEPLOY_GET_SERVICE_DETAIL, data)
        if "data" in rsp:
            checked = Deployment._converter.check(rsp['data'])
            filtered = Deployment._filter_data(checked)
            return Deployment(**filtered)
