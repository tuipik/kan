import argparse
import sys
import docker

KAN_IMAGES = {
    "front_prod": "kan-front-prod:latest",
    "front_preprod": "kan-front-preprod:latest",
    "api": "kan-api:latest",
    "celery-beat": "kan-celery-beat:latest",
    "celery": "kan-celery:latest",
    "redis": "redis:7.2.2-alpine",
    "nginx": "nginx:1.23.2-alpine",
    "backup": "prodrigestivill/postgres-backup-local:16",
    "postgres": "postgres:15.6",
}
image_choices = ["ALL"]
image_choices.extend(list(KAN_IMAGES.keys()))
REPOSITORY_NAME = "kan-two.gis:5000/"


class LocalRegistryDockerImagesHandler:
    def __init__(self):
        self.client = docker.from_env()
        self.images = self.client.images.list()
        self.tag = None
        self.choices = []
        self.images_for_push = []

    def tag_images(self, tag):
        for choice in self.choices:
            tag_names = {tag, "latest"}
            splitted_image_name = KAN_IMAGES[choice].split(":")
            if len(splitted_image_name) > 1:
                tag_names.add(splitted_image_name[1])
            for tag_name in tag_names:
                full_tagged_image_name = (
                    f"{REPOSITORY_NAME}{splitted_image_name[0]}:{tag_name}"
                )
                is_tagged = self.client.images.get(KAN_IMAGES[choice]).tag(
                    full_tagged_image_name
                )
                if is_tagged:
                    self.images_for_push.append(full_tagged_image_name)

    def push_images(self):
        for image in self.images_for_push:
            result = self.client.images.push(image)
            sys.stdout.write(result)
            sys.stdout.write(f"{image} pushed to {REPOSITORY_NAME}\n")

    def _check_image_choices(self, choices):
        if "ALL" in choices:
            image_choices.remove("ALL")
            self.choices = image_choices
            return
        for choice in choices:
            if choice not in image_choices:
                sys.stdout.write(f"There is no such choice {choice}")
                sys.exit()
        self.choices = choices
        return

    def main(self, choices, tag=None, push=False):
        """
        python -m push_images --tag v1.0.1 --push --images front_prod front_preprod api ALL
        """
        self._check_image_choices(choices)

        if tag:
            self.tag_images(tag)

        if push:
            self.push_images()


if __name__ == "__main__":
    """
    Приклад запуску:
    python -m push_images --tag v1.0.1 --push --images front_prod front_preprod api
    """
    parser = argparse.ArgumentParser(
        description=r"Скрипт для заливки докер образів в локальний репозиторій",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--images",
        nargs="*",
        choices=image_choices,
        help=f"Possible images: {list(KAN_IMAGES.keys())}",
        required=True,
    )
    parser.add_argument("--tag", type=str, help="hash of commit", required=True)
    parser.add_argument("--push", action="store_true", help="push images to repo")

    args = parser.parse_args()
    handler = LocalRegistryDockerImagesHandler()
    handler.main(choices=args.images, tag=args.tag, push=args.push)
