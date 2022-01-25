# flake8: noqa

from ._version import __version__
from .client import Client, set_client

from .errors import AppPlatformError
from .models import (
    Dataset,
    OfflinePrediction,
    Deployment,
    Project,
    AdvanceSetting,
    TrainSetting,
    SearchSpace,
    CreateDeploymentRequest
)

from .models import Project as AutoML
