from abc import ABC, abstractmethod
from re import L
import torch
from torchtyping import TensorType
from torch import Tensor
from typing import Tuple, Type
from dataclasses import dataclass, field
from copy import deepcopy

from gym.spaces import Discrete
from scipy.stats import norm


@dataclass
class AbstractStatesBatch(ABC):
    states: Tensor


@dataclass
class Env(ABC):
    """
    Base class for environments, showing which methods should be implemented.
    A common assumption for all environments is that all nodes of the DAG (except s_f)
    can be represented as a fixed length 1-D tensor, and all actions are discrete,
    represented by a number in {0, ..., n_actions - 1}.
    """
    n_envs: int = 1  # number of environments to run in a vectorized wat
    n_actions: int = field(init=False)  # number of actions
    n_states: int = field(init=False)
    action_space: Discrete = field(init=False)
    state_shape: Tuple = field(init=False)  # shape of the states
    state_dim: Tuple = field(init=False)
    StatesBatch: type = field(init=False)
    device: torch.device = field(init=False)

    def __post_init__(self):
        self.StatesBatch = self.make_state_class(self.n_envs)
        self.state_dim = (self.n_envs, *self.state_shape)
        self.action_space = Discrete(self.n_actions)
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')

    @abstractmethod
    def make_state_class(self, batch_size) -> type:
        """
        :return: a class that represents a state.
        """
        pass

    def reset(self, *kwargs) -> AbstractStatesBatch:
        """
        :return: a batch of states, instance of StatesBatch
        """
        self._state = self.StatesBatch(*kwargs)
        return deepcopy(self._state)

    @abstractmethod
    def step(self, actions: TensorType[n_envs, torch.long]) -> Tuple[AbstractStatesBatch, TensorType[n_envs, bool]]:

        pass

    @abstractmethod
    def reward(self, final_states: AbstractStatesBatch) -> TensorType['batch_size', float]:
        pass

    @abstractmethod
    def get_states_indices(self, states: AbstractStatesBatch) -> TensorType['batch_size', torch.long]:
        pass
