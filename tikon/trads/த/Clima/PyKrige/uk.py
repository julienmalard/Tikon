from tikon.Clima.PyKrige.uk import UniversalKriging
from tikon.Clima.PyKrige.uk import __doc__

__doc__ = __doc__


class UniversalKriging(UniversalKriging):

    def update_variogram_model(self, variogram_model, variogram_parameters=None, variogram_function=None, nlags=6,
                               weight=False, anisotropy_scaling=1.0, anisotropy_angle=0.0):
        return super().update_variogram_model(variogram_model=variogram_model,
                                              variogram_parameters=variogram_parameters,
                                              variogram_function=variogram_function, nlags=nlags, weight=weight,
                                              anisotropy_scaling=anisotropy_scaling, anisotropy_angle=anisotropy_angle)

    def display_variogram_model(self):
        return super().display_variogram_model()

    def switch_verbose(self):
        return super().switch_verbose()

    def switch_plotting(self):
        return super().switch_plotting()

    def get_epsilon_residuals(self):
        return super().get_epsilon_residuals()

    def plot_epsilon_residuals(self):
        return super().plot_epsilon_residuals()

    def get_statistics(self):
        return super().get_statistics()

    def print_statistics(self):
        return super().print_statistics()

    def execute(self, style, xpoints, ypoints, mask=None, backend="vectorized", specified_drift_arrays=None):
        return super().execute(style=style, xpoints=xpoints, ypoints=ypoints, mask=mask, backend=backend,
                               specified_drift_arrays=specified_drift_arrays)
