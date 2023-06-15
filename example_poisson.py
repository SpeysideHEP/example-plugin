from scipy.stats import poisson
import numpy as np

from spey import BackendBase, ExpectationType
from spey.base.model_config import ModelConfig


class PoissonPDF(BackendBase):
    """
    An example poisson pdf implementation

    Args:
        signal_yields (``np.ndarray``): signal yields
        background_yields (``np.ndarray``): background yields
        data (``np.ndarray``): observations
    """

    name: str = "example.poisson"
    """Name of the backend"""
    version: str = "1.0.0"
    """Version of the backend"""
    author: str = "John Smith"
    """Author of the backend"""
    spey_requires: str = ">=0.0.1,<0.1.0"
    """Spey version required for the backend"""
    doi: str = "doi/address"
    """Citable DOI for the backend"""
    arXiv: str = "abcd.xyzw"
    """arXiv reference for the backend"""

    def __init__(
        self, signal_yields: np.ndarray, background_yields: np.ndarray, data: np.ndarray
    ):
        self.signal_yields = signal_yields
        self.background_yields = background_yields
        self.data = data

    @property
    def is_alive(self) -> bool:
        """Returns True if at least one bin has non-zero signal yield."""
        return np.any(self.signal_yields > 0.0)

    def config(self, allow_negative_signal: bool = True, poi_upper_bound: float = 10.0):
        r"""
        Model configuration.

        Args:
            allow_negative_signal (``bool``, default ``True``): If ``True`` :math:`\hat\mu`
              value will be allowed to be negative.
            poi_upper_bound (``float``, default ``40.0``): upper bound for parameter
              of interest, :math:`\mu`.

        Returns:
            ~spey.base.ModelConfig:
            Model configuration. Information regarding the position of POI in
            parameter list, suggested input and bounds.
        """
        min_poi = -np.min(
            self.background_yields[self.signal_yields > 0]
            / self.signal_yields[self.signal_yields > 0]
        )

        return ModelConfig(
            0,
            min_poi,
            [0.0],
            [(min_poi if allow_negative_signal else 0.0, poi_upper_bound)],
        )

    def get_logpdf_func(
        self,
        expected: ExpectationType = ExpectationType.observed,
        data: np.ndarray = None,
    ):
        r"""
        Generate function to compute :math:`\log\mathcal{L}(\mu, \theta)` where :math:`\mu` is the
        parameter of interest and :math:`\theta` are nuisance parameters.

        Args:
            expected (~spey.ExpectationType): Sets which values the fitting algorithm should focus and
              p-values to be computed.

              * :obj:`~spey.ExpectationType.observed`: Computes the p-values with via post-fit
                prescriotion which means that the experimental data will be assumed to be the truth
                (default).
              * :obj:`~spey.ExpectationType.aposteriori`: Computes the expected p-values with via
                post-fit prescriotion which means that the experimental data will be assumed to be
                the truth.
              * :obj:`~spey.ExpectationType.apriori`: Computes the expected p-values with via pre-fit
                prescription which means that the SM will be assumed to be the truth.
            data (``np.array``, default ``None``): input data that to fit

        Returns:
            ``Callable[[np.ndarray], float]``:
            Function that takes fit parameters (:math:`\mu` and :math:`\theta`) and computes
            :math:`\log\mathcal{L}(\mu, \theta)`.
        """
        current_data = (
            self.background_yields if expected == ExpectationType.apriori else self.data
        )
        data = current_data if data is None else data

        return lambda pars: np.sum(
            poisson.logpmf(data, pars[0] * self.signal_yields + self.background_yields)
        )

    def get_sampler(self, pars: np.ndarray):
        r"""
        Retreives the function to sample from.

        Args:
            pars (``np.ndarray``): fit parameters (:math:`\mu` and :math:`\theta`)
            include_auxiliary (``bool``): wether or not to include auxiliary data
              coming from the constraint model.

        Returns:
            ``Callable[[int, bool], np.ndarray]``:
            Function that takes ``number_of_samples`` as input and draws as many samples
            from the statistical model.
        """

        def sampler(sample_size: int, **kwargs) -> np.ndarray:
            """
            Fucntion to generate samples.

            Args:
                sample_size (``int``): number of samples to be generated.

            Returns:
                ``np.ndarray``:
                generated samples
            """
            return poisson.rvs(
                pars[0] * self.signal_yields + self.background_yields,
                size=(sample_size, len(self.signal_yields)),
            )

        return sampler

    def expected_data(self, pars: np.ndarray, **kwargs):
        r"""
        Compute the expected value of the statistical model

        Args:
            pars (``List[float]``): nuisance, :math:`\theta` and parameter of interest,
              :math:`\mu`.

        Returns:
            ``List[float]``:
            Expected data of the statistical model
        """
        return pars[0] * self.signal_yields + self.background_yields
