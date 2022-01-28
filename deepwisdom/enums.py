import json


def enum(*vals, **enums):
    """
    Enum without third party libs and compatible with py2 and py3 versions.
    """
    enums.update(dict(zip(vals, vals)))
    return type("Enum", (), enums)


PROJECT_DEFAULT_ADVANCE_SETTING = json.loads('{"search_space":[{"hp_subspace":"feature_engineering","hp_values":{"KeyTimeBinSecond":{"hp_type":"bool","hp_values":[true,false]},"KeyTimeBinMsecond":{"hp_type":"bool","hp_values":[true,false]},"KeyTimeWeekday":{"hp_type":"bool","hp_values":[true,false]},"KeyTimeHour":{"hp_type":"bool","hp_values":[true,false]},"KeyTimeDay":{"hp_type":"bool","hp_values":[true,false]},"KeyTimeMonth":{"hp_type":"bool","hp_values":[true,false]},"KeyTimeYear":{"hp_type":"bool","hp_values":[true,false]},"KeyNumDiff":{"hp_type":"bool","hp_values":[true,false]},"KeyTimeDiff_BW_Window_1":{"hp_type":"bool","hp_values":[true,false]},"KeyTimeDiff_FW_Window_10":{"hp_type":"bool","hp_values":[true,false]},"McCatRank":{"hp_type":"bool","hp_values":[true,false]},"McMcInnerLen":{"hp_type":"bool","hp_values":[true,false]},"GroupCntDivNunique":{"hp_type":"bool","hp_values":[true,false]},"CatCnt":{"hp_type":"bool","hp_values":[true,false]},"GroupMean":{"hp_type":"bool","hp_values":[true,false]},"GroupMax":{"hp_type":"bool","hp_values":[true,false]},"GroupMin":{"hp_type":"bool","hp_values":[true,false]},"GroupStd":{"hp_type":"bool","hp_values":[true,false]},"GroupMeanMinusSelf":{"hp_type":"bool","hp_values":[true,false]},"GroupMaxMinusSelf":{"hp_type":"bool","hp_values":[true,false]},"GroupMinMinusSelf":{"hp_type":"bool","hp_values":[true,false]},"CatSegCtrOrigin":{"hp_type":"bool","hp_values":[true,false]}}},{"hp_subspace":"modeling","hp_values":{"model":{"hp_type":"choice","hp_values":[{"hp_name":"LIGHTGBM","learning_rate":{"hp_type":"loguniform","hp_values":[0.005,0.2]},"feature_fraction":{"hp_type":"uniform","hp_values":[0.75,1]},"min_data_in_leaf":{"hp_type":"randint","hp_values":[2,30]},"num_leaves":{"hp_type":"randint","hp_values":[16,96]}},{"hp_name":"RANDOMFOREST","n_estimators":{"hp_type":"randint","hp_values":[30,200]},"max_features":{"hp_type":"uniform","hp_values":[0,0.5]}},{"hp_name":"GBTREE","learning_rate":{"hp_type":"loguniform","hp_values":[0.01,1]},"n_estimators":{"hp_type":"randint","hp_values":[30,200]},"subsample":{"hp_type":"uniform","hp_values":[0.5,1]}},{"hp_name":"CATBOOST","depth":{"hp_type":"randint","hp_values":[5,8]},"l2_leaf_reg":{"hp_type":"uniform","hp_values":[1,5]}},{"hp_name":"LOGISTIC_REGRESSION","C":{"hp_type":"loguniform","hp_values":[0.1,10]},"fit_intercept":{"hp_type":"choice","hp_values":[true,false]}},{"hp_name":"RIDGE","alpha":{"hp_type":"uniform","hp_values":[0.1,5]}},{"hp_name":"DECISIONTREE","max_features":{"hp_type":"uniform","hp_values":[0.3,1]},"max_depth":{"hp_type":"randint","hp_values":[3,9]}},{"hp_name":"TABNET","max_epochs":{"hp_type":"randint","hp_values":[3,20]},"gamma":{"hp_type":"uniform","hp_values":[1.1,1.5]}}]}}}],"target_train":{"train_data_ratio":80,"training_program":"指标优先","call_limit":[5,20],"instance_num":2,"call_delay":50,"gpu_mem":0,"memory_limit":20,"program_num":5,"max_trials":30,"trial_concurrency":3,"random_seed":1647}}')

DEFAULT_DOMAIN = ""
DEFAULT_ADMIN_DOMAIN = ""

# default time out values in seconds for waiting response from client
DEFAULT_TIMEOUT = enum(
    CONNECT=6.05,  # time in seconds for the connection to server to be established
    SOCKET=60,
    READ=60,  # time in seconds after which to conclude the server isn't responding anymore
    UPLOAD=600,  # time in seconds after which to conclude that project dataset cannot be uploaded
)

API_DOMAIN = enum(
    ACCESS_TOKEN="",
    API="",
    ADMIN=""
)

SVR_STATUS = enum(
    CREATE=1,
    SCHEDULE=2,
    SCHEDULE_SUCC=3,
    RUNNING=4,
    FAIL=5,
    HANDUP=6,
    CANCEL=7,
    DELETING=8,
    DELETED=9,
)

# 云类型
CLOUD_TYPE = enum(
    LOCAL=0,
    AMAZON=1,
    ALI=2,
    TENCENT=3,
    HUAWEI=4
)

# 数据来源
DATA_SOURCE = enum(
    LOCAL=0,
    MYSQL=1,
    ORACLE=2,
    MARIADB=3,
    HDFS=4,
    HIVE=5
)

# 模态类型
MODAL_TYPE = enum(
    CSV=0,
    VIDEO=1,
    IMAGE=2,
    SPEECH=3,
    TEXT=4
)

# 0二分类/分类,1多分类/检测/意图识别/匹配,2回归/定位/语音分离/序列,3时序/分隔
TASK_TYPE = enum(

)

API_URL = enum(
    AUTH="appmng/token",
    DATASET_PREPARE="sdk/datasetprepare",
    FILE_UPLOAD="sdk/fileupload",
    DATASET_UPLOAD="sdk/datasetupload",
    DATASET_QUERY="sdksvr/querydataset",  # 获取数据集id和状态
    DATASET_INFO="sdk/datasetinfo",
    DATASET_DELETE="sdk/datasetdelete",  # 数据集删除 /datawarehouse/datasets  DELETE
    DATASET_LIST="sdk/datasetlist",  # 数据集搜索 /datawarehouse/datasets  GET
    DATASET_MODIFY="sdk/datasetmodify",  # 数据集修改 /datawarehouse/dataset Patch
    DATASET_SUMMIT="sdk/connectionsummit",  # 从数据源导入生成数据集  /connection/submit POST
    DATASET_EDA="sdk/dataseteda",  # 获取数据集的EDA  /dataset/eda GET  PATCH
    PROJECT_CREATE="sdk/createproj",
    PROJECT_DELETE="sdk/deleteproj",  # 批量删除项目  /projects  DELETE
    PROJECT_ADVANCESETTING_UPDATE="sdk/projsetting",  # 高级设置修改  /project/advance_settings  PATCH
    PROJECT_TRAIN="sdk/projtrain",
    PROJECT_TERMINATE_TRAIN="sdk/terminatetrain",  # 终止训练  /project/terminate/train
    PROJECT_INFO="sdk/projinfo",
    PROJECT_DATASET_LIST="sdk/projdatasets",  # 项目下的数据集列表 /project/dataset
    PROJECT_TRAIN_RESULT="/sdk/trainresult",
    PROJECT_EFFECT="sdk/projeffect",  #迭代效果，实验列表： /project/iterative/effect
    PROJECT_SCHEME="sdk/projscheme",  #有最终方案的实验/solution：  /project/trial/scheme
    PROJECT_MODEL_LIST="sdk/modellist",  #项目的模型列表：/project/models
    PROJECT_MODEL="sdk/model",  #模型详情：  /project/model
    PROJECT_MODEL_SELECT="sdk/modelselect",  #需要部署的模型信息： /project/model/select
    PROJECT_MODEL_SS="/basic/searchspace/modal/task/ss",  #搜索空间详情： 请求admin  /basic/searchspace/modal/task/ss
    MODEL_DOWNLOAD="sdk/modeldownload", #模型文件下载： /project/model/download
    DATASET_PREDICT_UPLOAD="sdk/predictupload", #离线预测数据集上传： /predict/dataset/upload
    DATASET_PREDICT_LIST="sdk/predictlist",  # 离线预测数据集列表  /predict/datasets
    PREDICTION_DETAIL="sdk/projeval/detail",
    PREDICTION_PREDICT="sdk/projeval/predict",
    PREDICTION_LIST="sdk/projeval/list",
    PREDICTION_DELETE="sdk/projeval/delete",
    PREDICTION_DATASET_DOWNLOAD="sdk/projeval/dataset_download",
    PREDICTION_RESULT_DOWNLOAD="sdk/projeval/result_download",

    DEPLOY_CREATE_SERVICE='sdk/deploy/create',
    DEPLOY_GET_SERVICE_DETAIL='sdk/deploy/detail',
    DEPLOY_LIST_DEPLOYMENTS='sdk/deploy/list',
    DEPLOY_RESIDENT_DEPLOYMENT='sdk/deploy/resident',  # 推理服务常驻
    DEPLOY_RENAME_DEPLOYMENT='sdk/deploy/rename',
    DEPLOY_DELETE_DEPLOYMENT='sdk/deploy/delete',
    DEPLOY_GET_DEPLOYMENT_LOG='sdk/deploy/logs',
    DEPLOY_GET_SERVICE_API='sdk/deploy/get_api',

    # DATASET_DOWNLOAD_HOST="http://192.168.50.24:5000/proxy/static/"

)




