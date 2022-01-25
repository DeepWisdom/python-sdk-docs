import hashlib
import json
import logging
import os
import time
import string
from io import BytesIO

import trafaret as t
import deepwisdom.errors as err

from deepwisdom._compat import Int, String
from .api_object import APIObject
from deepwisdom.enums import API_URL, MODAL_TYPE
from deepwisdom.utils import aes
import pandas as pd


def _get_upload_id(file_path):
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            data = f.read()
            return hashlib.md5(data).hexdigest() + "-" + str(time.time())
    else:
        logging.error("%s doesn't exist, no md5", file_path)
        return ""


_base_dataset_schema = t.Dict(
    {
        t.Key("dataset_id"): Int,
        t.Key("dataset_name", optional=True): String,
        t.Key("create_time", optional=True): String,
        t.Key("file_size", optional=True): Int,
        t.Key("file_type", optional=True): Int,
    }
)


class Dataset(APIObject):
    """

    """
    _converter = _base_dataset_schema.allow_extra("*")

    def __init__(
        self,
        dataset_id: int,
        dataset_name: str = None,
        create_time: str = None,
        file_size: int = None,
        file_type: int = None

    ):
        self.dataset_id = dataset_id
        self.dataset_name = dataset_name
        self.create_time = create_time
        self.file_size = file_size
        self.file_type = file_type

    @classmethod
    def delete(cls, dataset_ids: list):
        """
        批量数据集删除
        Args:
            dataset_ids (list): 需要删除的数据集id列表

        Returns:

        """
        data = {
            "dataset_ids": dataset_ids
        }

        cls._client._delete(API_URL.DATASET_DELETE, data)

    @classmethod
    def create(cls, file_path: str = "", str_conn: str = "", dataset_id: int = 0, stage="train", dataset_type: int = 1,
               cloud_type: int = 0, source: int = 1,
               chosed_tables: string = "", modal_type: int = MODAL_TYPE.CSV, dataset_scene_id: int = 1,
               max_chunk_size: int = 10*1024*1024, ):
        """
        创建数据集
        Args:
            file_path (str):  数据集路径
            str_conn (json字符串):  mysql/hive的连接信息。 mysql/hive: {"host":"xxx","port":"3306","user":"xx","password":"xxx","db":"","encoding":"utf8","passwordCustom":"xx"}
            dataset_id (int): 数据集id
            stage (str): 阶段。 train:训练用的数据集， test: 离线预测用的数据集
            dataset_type (int):  0离线验证数据集，1训练数据集
            cloud_type (int): 云类型。 0本地, 1Amazon, 2阿里云, 3腾讯云, 4华为云
            source (int): 数据来源。 0本地文件, 1mysql, 2oracle, 3mariadb, 4hdfs, 5hive
            chosed_tables (json字符串): 选择的table 列表。 '[{"autotables":[{"table_name":"dataset_update_record"},{"table_name":"scene"}]}]'  # 选择的table 列表。 autotables代表db，dataset_update_record|scene代表autotable下的两个表,支持多层嵌套
            modal_type (int): 模态类型。 0CSV,1VIDEO,2IMAGE,3SPEECH,4TEXT
            dataset_scene_id (int): 场景id。默认1 枚举
            max_chunk_size (int): 分片上传的大小

        Returns:

        """
        if stage == "train":
            if file_path != "":
                return cls.create_from_file(filename=file_path,  dataset_type=dataset_type, modal_type=modal_type,
                                            dataset_scene_id=dataset_scene_id, max_chunk_size=max_chunk_size)
            elif str_conn != "":
                return cls.create_from_data_source(conn_info=str_conn, cloud_type=cloud_type, source=source,
                                                   chosed_tables=chosed_tables)
            elif dataset_id != 0:
                return cls.create_from_dataset_id(dataset_id=dataset_id)
            else:
                raise err.UploadTrainDataError

        elif stage == "test":
            # 目前离线预测只支持上传本地文件
            if file_path == "":
                raise err.UploadTestDataError

            if modal_type == MODAL_TYPE.CSV:
                return cls.upload_csv_offline_dataset(filename=file_path)
            else:
                return cls.create_from_file(filename=file_path,  dataset_type=0, modal_type=modal_type,
                                            dataset_scene_id=dataset_scene_id, max_chunk_size=max_chunk_size)

    @classmethod
    def upload_csv_offline_dataset(cls, filename=""):
        """
        表格类离线预测数据集上传
        Args:
            filename (str): 数据集路径

        Returns:

        """
        data = {
        }

        file_type = os.path.splitext(filename)[-1][1:]
        if file_type == "csv" or file_type == "txt":
            mime_type = 'text/csv'
        else:
            mime_type = 'application/octet-stream'
        with open(filename, 'rb') as f:
            files = {
                "file": (os.path.basename(filename), f, mime_type)
            }

            response = cls._client._upload(API_URL.DATASET_PREDICT_UPLOAD, data, files)

        dataset = dict(PredictDataset._safe_data(response["data"]))
        return PredictDataset(**dataset)

    @classmethod
    def dataset_search(cls, query: str = "", dataset_id: int = None):
        """
        查询数据集列表, 默认只拉一页，至多50条数据, 按更新的时间排序
        Args:
            dataset_id (int): 数据集id
            query (str): 模糊查询关键字

        Returns:
            list: 数据集对象列表

        """
        data = {
            "query": query,
            "page": 1,
            "limit": 50,
            "sortrules": "-update_time",
            "usable": 1
        }
        if dataset_id is not None:
            dataset = {
                "dataset_id": dataset_id
            }
            data.update(dataset)

        server_data = cls._server_data(API_URL.DATASET_LIST, data)
        init_data = [dict(Dataset._safe_data(item)) for item in server_data]
        return [Dataset(**data) for data in init_data]

    @classmethod
    def create_from_data_source(
            cls,
            conn_info: string,
            cloud_type: int,
            source: int,
            chosed_tables: string
    ):
        """
        目前支持从mysql/hive导入创建
        Args:
            conn_info (json字符串): mysql的连接信息。 mysql/hive: {"host":"xxx","port":"3306","user":"xx","password":"xxx","db":"","encoding":"utf8","passwordCustom":"xx"}
            cloud_type (int): 云类型。 0本地, 1Amazon, 2阿里云, 3腾讯云, 4华为云
            source (int):  数据来源。 0本地文件, 1mysql, 2oracle, 3mariadb, 4hdfs, 5hive
            chosed_tables (json字符):  选择的table 列表。 '[{"autotables":[{"table_name":"dataset_update_record"},{"table_name":"scene"}]}]'  # 选择的table 列表。 autotables代表db，dataset_update_record|scene代表autotable下的两个表,支持多层嵌套

        Returns:
            list: 数据集对象列表， 每个表对应一个数据集对象
        """
        # 密码做aes加密
        ac = aes.AesCrypt('ECB', '', 'utf-8', 'databaseloginpwd')
        conn_json = json.loads(conn_info)
        if conn_json.__contains__("password"):
            conn_json["password"] = ac.aesencrypt(conn_json["password"])

        conn_info = json.dumps(conn_json)

        data = {
            "conn_info": conn_info,
            "cloud_type": cloud_type,
            "source": source,
            "choosed_tables": chosed_tables
        }

        resp = cls._client._post(API_URL.DATASET_SUMMIT, data)
        if resp["code"] != 200 or "data" in resp and "ret" in resp["data"] and resp["data"]["ret"] != 1:
            raise err.ServerError(resp, resp["code"])

        table_map = resp["data"]["table_map"]

        datasets = []
        for dataset_id in table_map:
            # 等待数据集处理完成
            while True:
                tmp_datasets = cls.dataset_search(dataset_id=dataset_id)
                if len(tmp_datasets) > 0:
                    break

            data = {
                "dataset_id": dataset_id
            }
            server_data = cls._server_data(API_URL.DATASET_INFO, data)
            datasets.append(cls.from_server_data(server_data))

        return datasets

    @classmethod
    def create_from_file(
        cls,
        filename: str = None,
        dataset_type: int = 1,
        modal_type: int = None,
        dataset_scene_id: int = 1,
        max_chunk_size: int = 10*1024*1024
    ):
        """
        从本地上传、创建数据集
        Args:
            dataset_type (int): 0离线验证数据集，1训练数据集
            filename: 本地数据集的绝对路径
            modal_type: 模态类型。 0CSV,1VIDEO,2IMAGE,3SPEECH,4TEXT
            dataset_scene_id: 场景id。默认1 枚举
            max_chunk_size: 分片上传的大小

        Returns:
            Dataset: 数据集对象
        """

        dataset_id, msg = cls.dataset_upload(filename, dataset_type, modal_type, dataset_scene_id, max_chunk_size)
        if dataset_id < 0:
            logging.info(msg)
            raise err.UploadTrainDataError

        # 等待数据集处理完成
        while True:
            datasets = cls.dataset_search(dataset_id=dataset_id)
            if len(datasets) > 0:
                break

        data = {
            "dataset_id": dataset_id
        }
        server_data = cls._server_data(API_URL.DATASET_INFO, data)

        return cls.from_server_data(server_data)

    @classmethod
    def create_from_dataset_id(cls, dataset_id):
        data = {
            "dataset_id": dataset_id
        }
        server_data = cls._server_data(API_URL.DATASET_INFO, data)

        return cls.from_server_data(server_data)

    @classmethod
    def _file_upload(cls, url, file, data):
        return cls._client._upload(url, data, file)

    @classmethod
    def dataset_upload(
        cls,
        file_path: str,
        dataset_type: int,
        modal_type: int,
        dataset_scene_id: int,
        max_chunk_size: int
    ):
        """
        数据集上传
        Args:
            dataset_type (int): 0离线验证数据集，1训练数据集
            file_path:
            modal_type:
            dataset_scene_id:
            max_chunk_size:

        Returns:

        """
        upload_id = _get_upload_id(file_path)
        if upload_id == "":
            return -1, file_path + " doesn't exist"
        # file_path = filepath.replace('\\', '/')
        file_names = os.path.split(file_path)
        filename = file_names[-1]
        # 上传准备
        prepare_data = {}
        prepare_data["modal_type"] = modal_type
        prepare_data["filename"] = filename

        prepare_data["upload_id"] = upload_id

        resp = cls._client._post(API_URL.DATASET_PREPARE, prepare_data)

        if resp["data"]["ret"] != 1:
            return -1, resp

        _chunk_id_list = resp["data"]["chunk_id_list"]
        chunk_id_list = list()

        # 文件上传
        with open(file_path, 'rb') as fp:
            while 1:
                chunk = fp.read(max_chunk_size)
                if not chunk:
                    break
                chunk_id = hashlib.md5(chunk).hexdigest()
                chunk_id_list.append(chunk_id)
                if chunk_id in _chunk_id_list:
                    continue
                uploadData = {}
                uploadData["upload_id"] = upload_id
                uploadData["chunk_id"] = chunk_id
                chunk_fp = BytesIO(chunk)
                files = {
                    "file": (chunk_id, chunk_fp, 'application/octet-stream')
                }
                resp = cls._file_upload(API_URL.FILE_UPLOAD, files, uploadData)
                chunk_fp.close()
                if resp["data"]["ret"] != 1:
                    return -1, resp

        # 数据集上传
        dataset_deal_data = {}

        dataset_deal_data["filename"] = filename
        dataset_deal_data["upload_id"] = upload_id
        dataset_deal_data["chunk_id_list"] = json.dumps(chunk_id_list)
        dataset_deal_data["modal_type"] = modal_type
        # 场景Id， 二分等
        dataset_deal_data["dataset_scene_id"] = dataset_scene_id
        dataset_deal_data["data_type"] = dataset_type

        resp = cls._client._post(API_URL.DATASET_UPLOAD, dataset_deal_data)

        if resp["data"]["ret"] != 1:
            return -1, resp

        # 3秒间隔，轮询获取
        # 获取数据集信息
        while True:
            dataset_query_data = {}
            dataset_query_data["upload_id"] = upload_id

            resp = cls._client._post(API_URL.DATASET_QUERY, dataset_query_data)
            logging.info(resp)
            if resp["errNo"] != 0 or resp["data"]["data_set_id"] == -1:
                return -1, resp

            # id不为0生成完成
            if resp["data"]["data_set_id"] > 0:
                return resp["data"]["data_set_id"], "success"

            time.sleep(3)

    @classmethod
    def modify_dataset(cls, dataset_id: int, new_name: str = ""):
        """
        重命名数据集
        Args:
            dataset_id (int): 数据集id
            new_name (str): 新的名字

        Returns:

        """

        data = {
            "dataset_id": dataset_id,
            "file_name": new_name
        }

        cls._client._patch(API_URL.DATASET_MODIFY, data)

    def get_eda(self):
        """
        获取数据集的eda
        Returns:
            pandas.DataFrame: DataFrame对象

        """
        data = {
            "dataset_id": self.dataset_id
        }

        server_data = self._server_data(API_URL.DATASET_EDA, data)
        return pd.DataFrame(data=server_data["data"], columns=server_data["columns"], index=server_data["index"])

    def modify_eda(self, eda: pd.DataFrame):
        """
        修改数据集的eda
        Args:
            eda (pandas.DataFrame): eda对应的DataFrame

        Returns:

        """
        data = {
            "dataset_id": self.dataset_id,
            "eda": eda.to_json(orient='split')
        }
        self._client._patch(API_URL.DATASET_EDA, data)


class PredictDataset(APIObject):
    _converter = t.Dict(
        {
            t.Key("dataset_id"): Int,
            t.Key("dataset_name", optional=True): String
        }
    ).allow_extra("*")

    def __init__(
            self,
            # project_id: int,
            dataset_id: int,
            dataset_name: str = None
    ):
        # self.project_id = project_id
        self.dataset_id = dataset_id
        self.dataset_name = dataset_name


