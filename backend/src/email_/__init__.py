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


def send_vet_registration(
        to: str,
        registration_url: str,
) -> None:
    template_json_file_name = "vet_registration"
    template_fill_obj = {
        "human_readable_project_name": config.get().human_readable_project_name,
        "registration_url": registration_url,
    }

    core.send_mail(
        to,
        template_json_file_name,
        template_fill_obj
    )


if __name__ == "__main__":

    def manually_test_send_vet_registration():
        print(f"Testing {send_vet_registration.__name__}")

        to = input("Enter recipient email address: ")

        send_vet_registration(
            to,
            # Wow, this lecture really helped me with time management. You should definitely check it out!
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )


    manually_test_send_vet_registration()
