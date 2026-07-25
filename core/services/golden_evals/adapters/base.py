"""Abstract base for substrate adapters."""

from abc import ABC, abstractmethod

from ..context import EvalRunContext, KNOWN_SUBSTRATES


class SubstrateAdapter(ABC):
    """Base class for a per-substrate observation adapter.

    Subclasses declare ``substrate_type`` as a class attribute (bound to a
    constant from :mod:`core.services.golden_evals.context`) and implement
    :meth:`build_context` to normalize substrate-native rows into
    :class:`EvalRunContext` instances.
    """

    substrate_type: str = ""

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if cls.substrate_type and cls.substrate_type not in KNOWN_SUBSTRATES:
            raise TypeError(
                f"{cls.__name__}.substrate_type={cls.substrate_type!r} not in "
                f"KNOWN_SUBSTRATES. Register the constant in "
                "core.services.golden_evals.context first."
            )

    @abstractmethod
    def build_context(self, primary_row_id: str) -> EvalRunContext:
        """Return an :class:`EvalRunContext` for the given substrate row.

        Raises :class:`LookupError` when the row does not exist.
        """
        raise NotImplementedError
