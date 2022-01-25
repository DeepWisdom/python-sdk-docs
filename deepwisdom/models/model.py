import os

import requests
import trafaret as t

from deepwisdom._compat import Int, String

from .api_object import APIObject
from deepwisdom.enums import API_URL
from .offline_predictions import OfflinePrediction

# class Model(APIObject):
#     """
#
#     """


# class DicTableModel(Model):
#     """
#     表格二分类
#     """

def _get_models_dir():
    return os.path.expanduser("~/deepwisdom/models")


def _get__model_file(dir_path, filename):
    file_path = os.path.join(dir_path, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    return file_path


_file_exists = os.path.isfile


class ModelInstance(APIObject):
    """

    """
    _converter = t.Dict(
        {
            t.Key("model_id"): Int,
            t.Key("model_name"): String,
        }
    ).allow_extra("*")

    def __init__(
            self,
            project_id,
            trial_no,
            trial_type,
            model_id,
            model_name=None
    ):
        """
        待部署的模型实例
        Args:
            project_id (int): 项目id
            trial_no (int): 实验id
            trial_type (int): 实验类型
            model_id (int): 模型id
            model_name (str): 模型名称
        """
        self.project_id = project_id
        self.trial_no = trial_no
        self.trial_type = trial_type
        self.model_id = model_id
        self.model_name = model_name

    def download_model(self, dir_path=None):
        """
        下载模型文件到指定的目录， 默认~/deepwisdom/models。 目前支持表格类下载
        Args:
            dir_path (string): 自定义目录路径

        Returns:

        """
        data = {
            "model_id": self.model_id
        }

        server_data = self._server_data(API_URL.MODEL_DOWNLOAD, data)
        if dir_path is None:
            dir_path = _get_models_dir()

        file_list = server_data["model_files"]
        for file_obj in file_list:
            if "is_dir" in file_obj and file_obj["is_dir"] is True:
                continue

            r = requests.get(file_obj["file_url"], stream=True)
            file_path = _get__model_file(dir_path, file_obj["file_name"].split("/")[-1])
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):  # 1024 bytes
                    if chunk:
                        f.write(chunk)

    # def evaluate(self, dataset_id: int):
    #     """
    #     离线预测模型
    #     Args:
    #         dataset_id (int): 离线预测数据集id
    #
    #     Returns:
    #         OfflinePrediction: 离线预测结果详情
    #     """
    #     offline_predict = OfflinePrediction.predict(self.model_id, dataset_id)
    #     offline_predict.wait_for_result()
    #     return offline_predict.get_predict_detail(offline_predict.offline_id)


