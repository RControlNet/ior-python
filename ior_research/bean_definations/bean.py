from cndi.annotations import Bean
import os

from cndi.exception import InvalidBeanDefination

from ior_research.utils.consts.envs import RCONTROLNET_ENV
from ior_research.utils.initializers import ProjectConfig, Initializer

@Bean()
def loadInitializer() -> Initializer:
    if RCONTROLNET_ENV in os.environ and os.path.exists(os.environ[RCONTROLNET_ENV]):
        return Initializer(os.environ[RCONTROLNET_ENV])
    raise InvalidBeanDefination(message=f"Could not find Environment Variable {RCONTROLNET_ENV}, or path does not exist")