import trafaret as t

from deepwisdom._compat import Int, String

from .api_object import APIObject
from deepwisdom.enums import API_URL


class Solution(APIObject):
    """

    """
    _converter = t.Dict(
        {
            t.Key("trial_no"): Int,
            t.Key("trial_type"): Int,
            t.Key("model_name", optional=True): String
        }
    ).allow_extra("*")

    def __init__(
            self,
            project_id,
            trial_no,
            trial_type,
            model_name=None
    ):
        """
        方案类
        Args:
            project_id (int): 项目id
            trial_no (int): 实验id
            trial_type (int): 实验类型
            model_name (str): 模型名称
        """
        self.project_id = project_id
        self.trial_no = trial_no
        self.trial_type = trial_type
        self.model_name = model_name

    def get_detail(self, tab_type=1):
        """
        方案详情
        Args:
            tab_type (int):  1效果图 2模型参数 3模型特征重要性 4 混淆矩阵 5最优跑测结果 6特征相关性 7特征重要性分布

        Returns:

        """
        data = {
            "project_id": self.project_id,
            "trial_no": self.trial_no,
            "tab_type": tab_type
        }

        return self._server_data(API_URL.PROJECT_MODEL, data)


