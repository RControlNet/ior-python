from cndi.annotations import Bean
import os

from cndi.env import getContextEnvironment
from cndi.exception import InvalidBeanDefination
from rcn import configDir

from ior_research.utils.consts.envs import RCONTROLNET_ENV, RCONTOLNET_PROFILE
from ior_research.utils.initializers import Initializer

@Bean()
def loadInitializer() -> Initializer:

    if RCONTROLNET_ENV in os.environ and os.path.exists(os.environ[RCONTROLNET_ENV]):
        return Initializer(os.environ[RCONTROLNET_ENV])
    elif RCONTOLNET_PROFILE in os.environ:
        configPath = os.path.join(configDir, os.environ[RCONTOLNET_PROFILE], "default.yml")
        return Initializer(configPath)
    else:
        active_profile = getContextEnvironment("rcn.profile.active", defaultValue=None)
        if active_profile is not None:
            configPath = os.path.join(configDir, active_profile, "default.yml")
            return Initializer(configPath)

    raise InvalidBeanDefination(message=f"Could not find Environment Variable {RCONTROLNET_ENV}, or path does not exist")
