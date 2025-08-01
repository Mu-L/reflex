"""Integration tests for var operations."""

from collections.abc import Generator
from typing import TypeVar

import pytest
from selenium.webdriver.common.by import By

from reflex.testing import AppHarness

# pyright: reportOptionalMemberAccess=false, reportGeneralTypeIssues=false, reportUnknownMemberType=false


def DynamicComponents():
    """App with var operations."""
    import reflex as rx

    class DynamicComponentsState(rx.State):
        value: int = 10

        button: rx.Component = rx.button(
            "Click me",
            custom_attrs={
                "id": "button",
            },
        )

        @rx.event
        def got_clicked(self):
            self.button = rx.button(
                "Clicked",
                custom_attrs={
                    "id": "button",
                },
            )

        @rx.var
        def client_token_component(self) -> rx.Component:
            return rx.vstack(
                rx.el.input(
                    custom_attrs={
                        "id": "token",
                    },
                    value=self.router.session.client_token,
                    is_read_only=True,
                ),
                rx.button(
                    "Update",
                    custom_attrs={
                        "id": "update",
                    },
                    on_click=DynamicComponentsState.got_clicked,
                ),
            )

    app = rx.App()

    def factorial(n: int) -> int:
        if n == 0:
            return 1
        return n * factorial(n - 1)

    @app.add_page
    def index():
        return rx.vstack(
            DynamicComponentsState.client_token_component,
            DynamicComponentsState.button,
            rx.text(
                DynamicComponentsState._evaluate(
                    lambda state: factorial(state.value), of_type=int
                ),
                id="factorial",
            ),
        )


@pytest.fixture(scope="module")
def dynamic_components(tmp_path_factory) -> Generator[AppHarness, None, None]:
    """Start VarOperations app at tmp_path via AppHarness.

    Args:
        tmp_path_factory: pytest tmp_path_factory fixture

    Yields:
        running AppHarness instance
    """
    with AppHarness.create(
        root=tmp_path_factory.mktemp("dynamic_components"),
        app_source=DynamicComponents,
    ) as harness:
        assert harness.app_instance is not None, "app is not running"
        yield harness


T = TypeVar("T")


@pytest.fixture
def driver(dynamic_components: AppHarness):
    """Get an instance of the browser open to the dynamic components app.

    Args:
        dynamic_components: AppHarness for the dynamic components

    Yields:
        WebDriver instance.
    """
    driver = dynamic_components.frontend()
    try:
        token_input = AppHarness.poll_for_or_raise_timeout(
            lambda: driver.find_element(By.ID, "token")
        )
        # wait for the backend connection to send the token
        token = dynamic_components.poll_for_value(token_input)
        assert token is not None

        yield driver
    finally:
        driver.quit()


def test_dynamic_components(driver, dynamic_components: AppHarness):
    """Test that the var operations produce the right results.

    Args:
        driver: selenium WebDriver open to the app
        dynamic_components: AppHarness for the dynamic components
    """
    button = AppHarness.poll_for_or_raise_timeout(
        lambda: driver.find_element(By.ID, "button")
    )
    assert button.text == "Click me"

    update_button = driver.find_element(By.ID, "update")
    assert update_button
    update_button.click()

    assert (
        dynamic_components.poll_for_content(button, exp_not_equal="Click me")
        == "Clicked"
    )

    factorial = AppHarness.poll_for_or_raise_timeout(
        lambda: driver.find_element(By.ID, "factorial")
    )
    assert factorial.text == "3628800"
