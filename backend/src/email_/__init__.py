from typing import Any

from utils import template

if __name__ == "__main__":
    import os
    from pathlib import Path
    import sys

    package_path = Path(__file__).parent
    src_path = package_path.parent

    sys.path.append(str(src_path))
    sys.path.append(str(package_path))
    __package__ = package_path.name

    os.environ["ENV"] = "dev"

import config
from . import _core as core
from ._errors import FailedToSend


def send_vet_registration(
        to: str,
        registration_token: str,
) -> None:
    template_json_file_name = "vet_registration"
    template_fill_obj = {
        "human_readable_project_name": config.get().human_readable_project_name,
        "form_url": template.replace(
            config.get().form.vet_registration_url_template,
            {
                "token": registration_token
            }
        )
    }

    core.send_mail(
        to,
        template_json_file_name,
        template_fill_obj
    )


def send_vet_management(
        to: str,
        grant_verification_url: str,
        revoke_verification_url: str,
        delete_url: str,
        vet_id: str,
        vet_fields: dict[str, Any],
) -> None:
    template_json_file_name = "vet_management"
    template_fill_obj = {
        "human_readable_project_name": config.get().human_readable_project_name,
        "grant_verification_url": grant_verification_url,
        "revoke_verification_url": revoke_verification_url,
        "delete_url": delete_url,
        "vet_id": vet_id,
        "vet_fields": "\n".join([
            f"{name}={repr(value)} \\"
            for name, value in vet_fields.items()
        ])
    }

    core.send_mail(
        to,
        template_json_file_name,
        template_fill_obj,
    )


if __name__ == "__main__":

    def manually_test_send_vet_registration():
        print(f"Testing {send_vet_registration.__name__}")

        to = input("Enter recipient email address: ")

        send_vet_registration(to)


    manually_test_send_vet_registration()
