"""Banner components."""
from typing import Optional

from reflex import constants
from reflex.components.component import Component
from reflex.components.layout import Box, Cond, Fragment
from reflex.components.overlay.modal import Modal
from reflex.components.typography import Text
from reflex.vars import Var

connection_error = Var.create(
    value="(connectError !== null) ? connectError.message : ''",
    is_local=False,
    is_string=False,
)
has_connection_error = Var.create(
    value="connectError !== null",
    is_string=False,
)
if has_connection_error is not None:
    has_connection_error.type_ = bool
default_connection_error = [
    "Cannot connect to server: ",
    connection_error,
    ". Check if server is reachable at ",
    constants.API_URL,
]


class ConnectionBanner(Cond):
    """A connection banner component."""

    @classmethod
    def create(cls, comp: Optional[Component] = None) -> Component:
        """Create a connection banner component.

        Args:
            comp: The component to render when there's a server connection error.

        Returns:
            The connection banner component.
        """
        if not comp:
            comp = Box.create(
                Text.create(
                    *default_connection_error,
                    bg="red",
                    color="white",
                ),
                textAlign="center",
            )

        return super().create(has_connection_error, comp, Fragment.create())  # type: ignore


class ConnectionModal(Modal):
    """A connection status modal window."""

    @classmethod
    def create(cls, comp: Optional[Component] = None) -> Component:
        """Create a connection banner component.

        Args:
            comp: The component to render when there's a server connection error.

        Returns:
            The connection banner component.
        """
        if not comp:
            comp = Text.create(*default_connection_error)
        return super().create(
            header="Connection Error",
            body=comp,
            is_open=has_connection_error,
        )
