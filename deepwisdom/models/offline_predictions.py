# -*- coding: utf-8 -*-
"""
模型数据集预测

"""
import time
from typing import Any
from typing import List
import trafaret as t
from deepwisdom.models.api_object import APIObject
from deepwisdom._compat import Int, String, Any
import deepwisdom.errors as err
from deepwisdom.enums import API_URL
from dataclasses import dataclass

PREDICT_STATUS_NONE = 0
PREDICT_STATUS_RUNNING = 1
PREDICT_STATUS_FINISH = 2
PREDICT_STATUS_FAILED = 3


@dataclass
class OfflinePredictionListMember(APIObject):
    _converter = t.Dict(
        {
            t.Key("offline_id"): Int,
            t.Key("offline_status"): Int,
            t.Key("dataset_id"): Int,
            t.Key("model_inst_id"): Int,  # 模型id
            t.Key("dataset_name"): String,  # 服务中文名
        }
    ).allow_extra("*")
    offline_id: int = 0
    offline_status: int = 0
    dataset_name: str = ''
    dataset_id: int = 0
    model_inst_id: int = 0

    def get_predict_detail(self) -> 'OfflinePrediction':
        """获取离线预测详情

        Args:
            offline_id (int64): 离线预测id
        Returns:
            OfflinePredictionDetail: 离线预测详情
        """
        data = {
            "offline_id": self.offline_id,
        }
        rsp = self._server_data(API_URL.PREDICTION_DETAIL, data)
        if rsp:
            rsp['offline_id'] = self.offline_id
            checked = OfflinePrediction._converter.check(rsp)
            filtered = OfflinePrediction._filter_data(checked)
            return OfflinePrediction(**filtered)


@dataclass
class OfflinePrediction(APIObject):
    _converter = t.Dict(
        {
            t.Key("offline_id"): Int,
            t.Key("project_id", optional=True): Int,
            t.Key("ret"): Int,
            t.Key("status"): Int,
            t.Key("task_type"): Int,
            t.Key("models_metrics"): Any,  #
            t.Key("models_metric_overview"): Any,  #
            t.Key("models_plot_data"): Any,  #
            t.Key("models_pred_prob"): Any,  #
            t.Key("models_preview_data"): Any,  #
            t.Key("models_preview_data_cols"): Any,  #
        }
    ).allow_extra("*")
    project_id: int = 0
    offline_id: int = 0
    ret: int = 0
    status: int = 0
    task_type: int = 0
    models_metrics: Any = None
    models_metric_overview: Any = None
    models_plot_data: Any = None
    models_pred_prob: Any = None
    models_preview_data: Any = None
    models_preview_data_cols: Any = None

    @classmethod
    def list_predictions(cls, project_id: int) -> List['OfflinePredictionListMember']:
        """获取预测列表
        Args:
            project_id (uint64): 项目id

        """
        data = {
            "project_id": project_id,
        }

        server_data = cls._server_data(API_URL.PREDICTION_LIST, data)
        init_data = [dict(OfflinePredictionListMember._safe_data(item)) for item in server_data]
        return [OfflinePredictionListMember(**data) for data in init_data]


    @classmethod
    def predict(cls, model_inst_id: int, dataset_id: int) -> "OfflinePrediction":
        """开始离线预测

        Returns:
            OfflinePrediction: 离线预测实例
        """
        data = {
            "model_inst_id": model_inst_id,
            "dataset_id": dataset_id,
        }
        rsp = cls._client._post(API_URL.PREDICTION_PREDICT, data)
        if "data" in rsp and rsp['data']['offline_id']:
            return cls.get_predict_detail(rsp['data']['offline_id'])
        return None

    @classmethod
    def get_predict_detail(cls, offline_id: int) -> 'OfflinePrediction':
        """获取离线预测详情

        Args:
            offline_id (int64): 离线预测id
        Returns:
            OfflinePrediction: 离线预测详情
        """
        data = {
            "offline_id": offline_id,
        }
        rsp = cls._server_data(API_URL.PREDICTION_DETAIL, data)
        if rsp:
            rsp['offline_id'] = offline_id
            checked = OfflinePrediction._converter.check(rsp)
            filtered = OfflinePrediction._filter_data(checked)
            return OfflinePrediction(**filtered)

    def get_predict_status(self) -> Int:
        """获取离线预测状态

        Returns:
            Int: 服务状态：0未预测, 1预测中, 2预测结束, 3预测失败
        """
        data = {
            "offline_id": self.offline_id,
        }
        rsp = self._server_data(API_URL.PREDICTION_DETAIL, data)
        if rsp:
            rsp['offline_id'] = self.offline_id
            checked = self._converter.check(rsp)
            filtered = self._filter_data(checked)
            if rsp['ret'] == -1:
                rsp['status'] = 3
            self = self.from_server_data(filtered)
            return rsp["status"]
        return Int(0)

    def wait_for_result(self):
        """等待预测结果
        Returns:
            OfflinePredictionDetail: 离线预测实例
        """
        status = self.get_predict_status()
        while status == 1:
            status = self.get_predict_status()
            if status == PREDICT_STATUS_FINISH or status == PREDICT_STATUS_FAILED:
                break
            time.sleep(3)
        self.status = status
        return status

    @classmethod
    def delete_predictions(cls, offline_ids: List[int]):
        """批量删除预测
        Args:
            offline_ids (List[int]): 离线预测id数组
        """
        data = {
            "offline_ids": offline_ids
        }
        rsp = cls._client._delete(API_URL.PREDICTION_DELETE, data)
        if "data" in rsp:
            return rsp['data']
        return None

    # @classmethod
    # def result_download(cls, project_id: int, target_path: str):
    #     # """项目预测报告下载,当前由前端渲染后下载，暂时不支持服务端直接下载 TODO
    #     #
    #     # Args:
    #     #     project_id (int64):  项目id
    #     # """
    #     data = {
    #         "project_id": project_id,
    #     }
    #     rsp = cls._client._get(API_URL.PREDICTION_RESULT_DOWNLOAD, data)
    #     if "data" in rsp and "zip_name" in rsp["data"]:
    #         print(rsp)
    #         report = cls._client._get(rsp['data']["zip_name"], {})
    #         out = open(target_path, "w+")
    #         out.write(report)
    #         out.close()
    #     return None

    # @classmethod
    # def dataset_download(cls, offline_id: int, target_path: str, target_cols: List[str] = []):
    #     # """离线预测数据集下载，暂时不可用 TODO
    #     #
    #     # Args:
    #     #     offline_id (int): 预测数据集id
    #     #     target_path (str): 下载路径
    #     #     target_cols (List[str]): 数据列选择,默认为空[]
    #     #
    #     # Returns:
    #     #     str: 数据集地址
    #     # """
    #     data = {
    #         "offline_id": offline_id,
    #         "dataset_id": target_cols,
    #     }
    #     rsp = cls._client._get(API_URL.PREDICTION_DATASET_DOWNLOAD, data)
    #     if "data" in rsp:
    #         # pass
    #         # return rsp['data']
    #         fi = cls._client._get(cls.join_dataset_download_path(rsp['data']), {})
    #         out = open(target_path, "w+")
    #         out.write(fi)
    #         out.close()
    #     return None

    @classmethod
    def join_dataset_download_path(cls, path):
        return API_URL.DATASET_DOWNLOAD_HOST + path
