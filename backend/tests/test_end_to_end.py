"""
The following test should cover all main outward-facing
functionally that will interact with external services or users
(and be maintained with this goal in mind).

Consider a rewrite using a BDD test framework.
"""

import random
import re
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, ContextManager

import pytest
from fastapi import status
from fastapi.testclient import TestClient

import config
import db
import email_
import paths
import vet_management
import vet_visibility


TEST_API_ROOT = f"{config.get().domain}:{config.get().fastapi.port}"


class Steps:
    """
    Used as a namespace, listing steps that would normally be executed
    during typical usage of the system.

    Class methods prefixed with 'steps_' will be tested sequentially.
    """
    visibility = "software_test"
    form_user_email_address = "form.user@example.com"

    # State will incrementally be populated by the steps
    visibility_token: str
    form_user_access_token: str
    content_management_access_token: str

    @classmethod
    def step_read_vet_visibility_token_from_txt_file(cls, assertion_ctx) -> None:
        # Given ***************************************************************
        tokens_file = paths.find_backend() / "vet_visibility_tokens.txt"

        # When ****************************************************************
        if tokens_file.exists():
            tokens_file_exists = True

            lines: list[str]
            with open(tokens_file, "r") as f:
                lines = f.readlines()

            for line in lines:
                visibility, token = line.strip().split(":")
                if visibility == cls.visibility:
                    cls.visibility_token = token
                    break
        else:
            tokens_file_exists = False

        # Then ****************************************************************
        with assertion_ctx(f"Tokens file '{tokens_file}' should exist"):
            assert tokens_file_exists

        with assertion_ctx(f"Tokens file should contain a token for the visibility '{cls.visibility}'"):
            assert cls.visibility_token is not None

        with assertion_ctx("Should be able to determine visibility from token"):
            assert vet_visibility.get_visibility_from_jwt(cls.visibility_token) == cls.visibility

    @classmethod
    def step_fail_to_send_vet_registration_email_with_invalid_token_to_form_user_using_api(
            cls,
            assertion_ctx,
            api: TestClient
    ) -> None:
        # Given ***************************************************************
        tampered_token = tamper_with_jwt(cls.visibility_token)

        email_address = "dummy.email@example.com"
        request_url = f"{TEST_API_ROOT}/form/send-vet-registration-email"
        request_headers = {
            "Authorization": f"Bearer {tampered_token}",
            'Content-Type': 'application/json'
        }
        request_body = {
            "emailAddress": email_address,
        }

        # When ****************************************************************
        with use_mail_stub():
            res = api.post(
                request_url,
                headers=request_headers,
                json=request_body,
            )

        # Then ****************************************************************
        with assertion_ctx("Request response should have '403 Forbidden' status"):
            assert res.status_code == status.HTTP_403_FORBIDDEN

    @classmethod
    def step_send_vet_registration_email_to_form_user_using_api(cls, assertion_ctx, api: TestClient) -> None:
        # Given ***************************************************************
        email_address = "dummy.email@example.com"
        request_url = f"{TEST_API_ROOT}/form/send-vet-registration-email"
        request_headers = {
            "Authorization": f"Bearer {cls.visibility_token}",
            'Content-Type': 'application/json'
        }
        request_body = {
            "emailAddress": email_address,
        }

        # When ****************************************************************
        with use_mail_stub() as mail_stub:
            res = api.post(
                request_url,
                headers=request_headers,
                json=request_body,
            )

        send_mail_arguments = mail_stub.capture_send_mail_arguments()

        # Then ****************************************************************
        with assertion_ctx("Request response should have successful status"):
            assert res.status_code == status.HTTP_200_OK

        with assertion_ctx("The email should be sent to the address passed in the request body"):
            assert len(send_mail_arguments) == 1
            assert send_mail_arguments[0].recipient_address == email_address

        form_url = send_mail_arguments[0].template_fill_obj["form_url"]
        form_url_route = get_url_route(form_url)

        with assertion_ctx(
            "The link sending the user to the registration form int the email should "
            "contain a JWT access token and the email address"
        ):
            email_parameter_value_regex = r"[^@]+@[^\.]+\.[^\.]+"
            assert re.match(
                f"/form\\?access-token={get_jwt_regex_pattern()}&email={email_parameter_value_regex}",
                form_url_route
            ) is not None
            assert form_url.endswith(f"&email={email_address}")

        cls.form_user_access_token = get_text_between_string(
            form_url_route,
            "access-token=",
            "&email"
        )

        with assertion_ctx("JWT form access token allows access for 'form_user' role"):
            assert vet_management.access_is_allowed(
                cls.form_user_access_token,
                "form_user"
            )

    @classmethod
    def step_create_vet_by_form_user_using_api(cls, assertion_ctx, api: TestClient) -> None:
        # Given ***************************************************************
        request_url = f"{TEST_API_ROOT}/form/create-or-overwrite-vet"
        request_headers = {
            "Authorization": f"Bearer {cls.form_user_access_token}",
            'Content-Type': 'application/json'
        }
        request_body = FormCreateOrOverwriteVetRequestBodies.create

        # When ****************************************************************
        with use_mail_stub() as mail_stub:
            res = api.put(
                request_url,
                headers=request_headers,
                json=request_body,
            )

        send_mail_arguments_for_each_call = mail_stub.capture_send_mail_arguments()

        # Then ****************************************************************
        with assertion_ctx("Request response should have successful status"):
            assert res.status_code == status.HTTP_200_OK

        with assertion_ctx("Response should contain keys and values from request object"):
            assert_first_dict_is_subset_of_second(
                request_body,
                res.json(),
                recursive=True,
            )

        with assertion_ctx("Should send content management emails"):
            # Consider replacing emails with a dedicated content management system
            for send_mail_arguments in send_mail_arguments_for_each_call:
                assert send_mail_arguments.recipient_address in config.get().content_management.email_addresses

        with assertion_ctx("Content management emails should contain valid 'grant vet verification' link"):
            for send_mail_arguments in send_mail_arguments_for_each_call:
                assert "grant_verification_url" in send_mail_arguments.template_fill_obj

                grant_verification_route = get_url_route(
                    send_mail_arguments.template_fill_obj["grant_verification_url"]
                )

                expected_prefix = "/content-management/grant-vet-verification?access-token="

                assert grant_verification_route.startswith(expected_prefix)

                grant_verification_access_token = grant_verification_route.removeprefix(expected_prefix)

                assert_has_jwt_format(grant_verification_access_token)

        cls.content_management_access_token = grant_verification_access_token

        with assertion_ctx("Content management emails should contain valid 'revoke vet verification' link"):
            for send_mail_arguments in send_mail_arguments_for_each_call:
                assert "revoke_verification_url" in send_mail_arguments.template_fill_obj

                revoke_verification_route = get_url_route(
                    send_mail_arguments.template_fill_obj["revoke_verification_url"]
                )

                expected_prefix = "/content-management/revoke-vet-verification?access-token="

                assert revoke_verification_route.startswith(expected_prefix)

                revoke_verification_access_token = revoke_verification_route.removeprefix(expected_prefix)

                assert_has_jwt_format(revoke_verification_access_token)

                assert revoke_verification_access_token == cls.content_management_access_token

        with assertion_ctx("Content management emails should contain valid 'delete vet' link"):
            for send_mail_arguments in send_mail_arguments_for_each_call:
                assert "delete_url" in send_mail_arguments.template_fill_obj

                delete_route = get_url_route(
                    send_mail_arguments.template_fill_obj["delete_url"]
                )

                expected_prefix = "/content-management/delete-vet?access-token="

                assert delete_route.startswith(expected_prefix)

                delete_access_token = delete_route.removeprefix(expected_prefix)

                assert_has_jwt_format(delete_access_token)

                assert delete_access_token == cls.content_management_access_token

        with assertion_ctx("JWT content management access token allows access for 'content_management' role"):
            assert vet_management.access_is_allowed(
                cls.content_management_access_token,
                "content_management"
            )

    @classmethod
    def step_get_vet_created_by_form_user_using_api(cls, assertion_ctx, api: TestClient) -> None:
        # Given ***************************************************************
        request_url = f"{TEST_API_ROOT}/form/vet"
        request_headers = {
            "Authorization": f"Bearer {cls.form_user_access_token}",
            'Content-Type': 'application/json'
        }
        access_info = vet_management.allow_access_and_get_info(
            cls.form_user_access_token,
            "form_user",
        )

        # When ****************************************************************
        res = api.get(
            request_url,
            headers=request_headers,
        )

        # Then ****************************************************************
        with assertion_ctx("Request response should have successful status"):
            assert res.status_code == status.HTTP_200_OK

        with assertion_ctx("Response should contain id field from access token"):
            assert res.json()["id"] == access_info.id

        with assertion_ctx("Response should contain keys and values from create request object"):
            assert_first_dict_is_subset_of_second(
                FormCreateOrOverwriteVetRequestBodies.create,
                res.json(),
                recursive=True,
            )

    @classmethod
    def step_update_vet_by_form_user_using_api(cls, assertion_ctx, api: TestClient) -> None:
        # Given ***************************************************************
        request_url = f"{TEST_API_ROOT}/form/create-or-overwrite-vet"
        request_headers = {
            "Authorization": f"Bearer {cls.form_user_access_token}",
            'Content-Type': 'application/json'
        }
        request_body = FormCreateOrOverwriteVetRequestBodies.update

        # When ****************************************************************
        with use_mail_stub() as mail_stub:
            res = api.put(
                request_url,
                headers=request_headers,
                json=request_body,
            )

        send_mail_arguments_for_each_call = mail_stub.capture_send_mail_arguments()

        # Then ****************************************************************
        with assertion_ctx("Request response should have successful status"):
            assert res.status_code == status.HTTP_200_OK

        with assertion_ctx("Response should contain keys and values from request object"):
            assert_first_dict_is_subset_of_second(
                request_body,
                res.json(),
                recursive=True,
            )

        with assertion_ctx("Should send content management emails"):
            # Consider replacing emails with a dedicated content management system
            for send_mail_arguments in send_mail_arguments_for_each_call:
                assert send_mail_arguments.recipient_address in config.get().content_management.email_addresses

    @classmethod
    def step_get_empty_vets_array_by_frontend_user_using_api_before_vet_is_verified(
            cls,
            assertion_ctx,
            api: TestClient
    ) -> None:
        # Given ***************************************************************
        request_url = f"{TEST_API_ROOT}/vets"
        request_headers = {
            "Authorization": f"Bearer {cls.visibility_token}",
            'Content-Type': 'application/json'
        }

        # When ****************************************************************
        res = api.get(
            request_url,
            headers=request_headers,
        )

        # Then ****************************************************************
        with assertion_ctx("Request response should have successful status"):
            assert res.status_code == status.HTTP_200_OK

        with assertion_ctx("Response should be empty"):
            assert res.json() == []

    @classmethod
    def step_grant_vet_verification_by_content_management_using_api(cls, assertion_ctx, api: TestClient) -> None:
        # Given ***************************************************************
        request_url = (
            f"{TEST_API_ROOT}/content-management/grant-vet-verification"
            # The access token is not passed in the header so that we can directly
            # use the url as a link within the email.
            # TODO: Find a securer solution
            f"?access-token={cls.content_management_access_token}"
        )

        # When ****************************************************************
        res = api.get(request_url)

        # Then ****************************************************************
        with assertion_ctx("Request response should have successful status"):
            assert res.status_code == status.HTTP_200_OK

    @classmethod
    def step_get_vets_array_by_frontend_user_using_api_containing_verified_vet(
            cls,
            assertion_ctx,
            api: TestClient
    ) -> None:
        # Given ***************************************************************
        request_url = f"{TEST_API_ROOT}/vets"
        request_headers = {
            "Authorization": f"Bearer {cls.visibility_token}",
            'Content-Type': 'application/json'
        }

        # When ****************************************************************
        res = api.get(
            request_url,
            headers=request_headers,
        )

        # Then ****************************************************************
        with assertion_ctx("Request response should have successful status"):
            assert res.status_code == status.HTTP_200_OK

        with assertion_ctx("Response should contain verified vet"):
            assert len(res.json()) == 1

            assert_first_dict_is_subset_of_second(
                FormCreateOrOverwriteVetRequestBodies.update,
                res.json()[0],
                recursive=True,
            )

    @classmethod
    def step_revoke_vet_verification_by_content_management_using_api(cls, assertion_ctx, api: TestClient) -> None:
        # Given ***************************************************************
        request_url = (
            f"{TEST_API_ROOT}/content-management/revoke-vet-verification"
            # The access token is not passed in the header so that we can directly
            # use the url as a link within the email.
            # TODO: Find a securer solution
            f"?access-token={cls.content_management_access_token}"
        )

        # When ****************************************************************
        res = api.get(request_url)

        # Then ****************************************************************
        with assertion_ctx("Request response should have successful status"):
            assert res.status_code == status.HTTP_200_OK

    @classmethod
    def step_get_empty_vets_array_by_frontend_user_using_api_after_vet_verification_has_been_revoked(
            cls,
            assertion_ctx,
            api: TestClient
    ) -> None:
        # Given ***************************************************************
        request_url = f"{TEST_API_ROOT}/vets"
        request_headers = {
            "Authorization": f"Bearer {cls.visibility_token}",
            'Content-Type': 'application/json'
        }

        # When ****************************************************************
        res = api.get(
            request_url,
            headers=request_headers,
        )

        # Then ****************************************************************
        with assertion_ctx("Request response should have successful status"):
            assert res.status_code == status.HTTP_200_OK

        with assertion_ctx("Response should be empty"):
            assert res.json() == []

    @classmethod
    def step_delete_vet_by_content_management_using_api(cls, assertion_ctx, api: TestClient) -> None:
        # Given ***************************************************************
        request_url = (
            f"{TEST_API_ROOT}/content-management/delete-vet"
            # The access token is not passed in the header so that we can directly
            # use the url as a link within the email.
            # TODO: Find a securer solution
            f"?access-token={cls.content_management_access_token}"
        )

        # When ****************************************************************
        res = api.get(request_url)

        # Then ****************************************************************
        with assertion_ctx("Request response should have successful status"):
            assert res.status_code == status.HTTP_200_OK

        with assertion_ctx("Vet collections in database should be empty"):
            assert db.vet_collections_are_empty("software_test")


class FormCreateOrOverwriteVetRequestBodies:
    create = {
        "clinicName": "Initial Clinic Name",
        "nameInformation": {
            "formOfAddress": "ms",
            "title": "dr_med",
            "firstName": "Jane",
            "lastName": "Doe"
        },
        "location": {
            "address": {
                "street": "Alt-Friedrichsfelde",
                "zipCode": 10315,
                "city": "Berlin",
                "number": "60"
            }
        },
        "contacts": [
            {
                "type": "tel:landline",
                "value": "INVALID TELEPHONE NUMBER"  # TODO: Add validation
            },
            {
                "type": "tel:mobile",
                "value": "INVALID MOBILE NUMBER"  # TODO: Add validation
            },
            {
                "type": "email",
                "value": "INVALID EMAIL"  # TODO: Add validation
            },
            {
                "type": "website",
                "value": "INVALID WEBSITE"  # TODO: Add validation
            }
        ],
        "treatments": [
            "dogs"
        ],
        "openingHours": {
            "Mon": {
                "from": "11:00",
                "to": "14:00"
            },
            "Thu": {
                "from": "15:00",
                "to": "20:00"
            }
        },
        "emergencyTimes": [
            {
                "startDate": "12.11.2022",
                "endDate": "16.11.2022",
                "fromTime": "12:00",
                "toTime": "13:00",
                "days": [
                    "Mon",
                    "Tue"
                ]
            },
            {
                "startDate": "01.12.2022",
                "endDate": "31.12.2022",
                "fromTime": "10:00",
                "toTime": "17:00",
                "days": [
                    "Mon",
                    "Wed",
                    "Fri",
                    "Sun"
                ]
            }
        ]
    }
    update = create | {"clinicName": "Updated Clinic Name"}


class ExpectedFormVetResponseBodies:
    after_create = FormCreateOrOverwriteVetRequestBodies.create


def test(fastapi_client: TestClient, delete_test_collections) -> None:

    # Helpers
    def try_run_step(step_name: str, step: Callable) -> None:

        @contextmanager
        def add_step_assertion_error_ctx(msg: str) -> None:
            with add_assert_error_ctx(
                    f"Step '{step_name.removeprefix('step_').replace('_', ' ')}': {msg}"
            ):
                yield

        successfully_ran_step = False
        errors = []
        for arguments in ((add_step_assertion_error_ctx,), (add_step_assertion_error_ctx, fastapi_client,)):
            try:
                step(*arguments)
                successfully_ran_step = True
                break
            except Exception as err:
                errors.append(err)

        if not successfully_ran_step:
            # Prioritize AssertionErrors
            for error in errors:
                if isinstance(error, AssertionError):
                    raise error

            # Next look for errors do not relate to missing arguments
            for error in errors:
                if isinstance(error, TypeError) and (
                    "required positional argument" in str(error)
                    or "required keyword argument" in str(error)
                ):
                    continue

                raise error

            raise errors[0]

    def is_step_name(member_name: str) -> bool:
        return member_name.startswith("step_")

    # Run steps
    for step_name in filter(is_step_name, list(Steps.__dict__.keys())):
        step = getattr(Steps, step_name)
        try_run_step(step_name, step)


@pytest.fixture
def delete_test_collections() -> None:
    """Remove 'software_test' collections before and after test."""
    db.delete_vet_collections("software_test")

    yield

    db.delete_vet_collections("software_test")


# Helpers
# =============================================================================

def tamper_with_jwt(
    jwt: str,
    replace_n_chars_in_header: int = 0,
    replace_n_chars_in_payload: int = 0,
    replace_n_chars_in_signature: int = 1,
    rng_seed: int | None = None,
) -> str:
    url_safe_base64_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")

    segments = [list(chars) for chars in jwt.split(".")]

    if rng_seed is not None:
        random.seed(rng_seed)

    for segment_index, replace_n_chars in (
        (0, replace_n_chars_in_header),
        (1, replace_n_chars_in_payload),
        (2, replace_n_chars_in_signature),
    ):
        for replacement_index in random.choices(
            range(len(segments[segment_index])),
            k=replace_n_chars
        ):
            original_char = segments[segment_index][replacement_index]
            replacement_char = random.choice(sorted(url_safe_base64_chars - {original_char}))
            segments[segment_index][replacement_index] = replacement_char

    return ".".join("".join(chars) for chars in segments)


@contextmanager
def add_assert_error_ctx(ctx: str) -> None:
    try:
        yield
    except AssertionError as err:
        if len(err.args) >= 1:
            err.args = (err.args[0] + f"\n\nContext: {ctx}", *err.args[1:])
        else:
            err.args = (f"Context: {ctx}",)

        raise err


@dataclass(frozen=True)
class SendMailArgs:
    recipient_address: str
    template: dict | str
    template_fill_obj: Any


@dataclass(frozen=True)
class MailStub:
    capture_send_mail_arguments: Callable[[], list[SendMailArgs]]


@contextmanager
def use_mail_stub() -> ContextManager[MailStub]:
    send_mail_stub, capture_send_mail_arguments = create_send_mail_stub_and_argument_capturer()

    with email_.use_temp_default_config(
        email_.Config(
            send_mail=send_mail_stub,
        )
    ):
        yield MailStub(capture_send_mail_arguments=capture_send_mail_arguments)


def create_send_mail_stub_and_argument_capturer() -> tuple[
    Callable[[str, dict | str, Any], None],
    Callable[[], list[SendMailArgs]]
]:
    args: list[SendMailArgs] = []

    def capture_arguments() -> list[SendMailArgs]:
        return args

    def stub(
            recipient_address: str,
            template: dict | str,
            template_fill_obj: Any,
    ) -> None:
        args.append(SendMailArgs(
            recipient_address=recipient_address,
            template=template,
            template_fill_obj=template_fill_obj,
        ))

    return stub, capture_arguments


def get_url_route(url: str) -> str:
    segments_after_domain = (
        segment
        for segment in url.removeprefix('https://').removeprefix('http://').split('/')[1:]
        if segment != ""
    )

    return f"/{'/'.join(segments_after_domain)}"


def get_jwt_regex_pattern() -> str:
    return r"[a-z,A-Z,0-9,_,-]+\.[a-z,A-Z,0-9,_,-]+\.[a-z,A-Z,0-9,_,-]+"


def assert_has_jwt_format(s: str) -> None:
    return re.fullmatch(get_jwt_regex_pattern(), s) is not None


def get_text_between_string(s: str, start: str, end: str) -> str:
    return s[(start_index := s.index(start) + len(start)):s.index(end, start_index)]


def assert_first_dict_is_subset_of_second(
        dict1: dict,
        dict2: dict,
        *,
        recursive: bool = False,
        path: str = "",
) -> None:
    for key, dict1_value in dict1.items():
        sub_path = str(key) if path == "" else f"{path}.{key}"
        assert key in dict2, f"Superset dictionary is missing key '{sub_path}'"

        dict2_value = dict2[key]

        assert type(dict1_value) is type(dict2_value), (
            f"Values of dictionaries at '{sub_path}' do not have same type. "
            f"Subset dictionary value = '{dict1_value}'; "
            f"superset dictionary value = '{dict2_value}'"
        )

        if type(dict1_value) is dict and recursive:
            assert_first_dict_is_subset_of_second(
                dict1_value,
                dict2_value,
                recursive=True,
                path=sub_path,
            )
        else:
            assert dict1_value == dict2_value, (
                f"Values of dictionaries at '{sub_path}' are not equal"
            )
