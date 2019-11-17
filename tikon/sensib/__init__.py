from .sens_salib import SensSALib
from .sensib import AnlzdrSensib


def gen_anlzdr_sensib(anlzdr):
    if isinstance(anlzdr, AnlzdrSensib):
        return anlzdr
    return SensSALib()
