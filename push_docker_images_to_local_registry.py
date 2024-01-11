import argparse
import sys

import docker


class LocalRegistryDockerImagesHandler:
    KAN_IMAGES_LIST = [
        "kan-front:latest"
        "kan_api:latest",
        "kan_celery-beat",
        "kan_celery",
        "redis:7.2.2-alpine",
        "nginx:1.23.2-alpine",
        "prodrigestivill/postgres-backup-local:latest",
        "postgres:15",
    ]
    REPOSITORY_NAME = "kan-two.gis:5000/"

    def __init__(self):
        self.client = docker.from_env()
        self.images = self.client.images.list()

    def tag_images(self):
        for image in self.KAN_IMAGES_LIST:
            self.client.images.get(image).tag(f"{self.REPOSITORY_NAME}{image}")

    def push_images(self):
        for image in self.KAN_IMAGES_LIST:
            self.client.images.push(f"{self.REPOSITORY_NAME}{image}")
            sys.stdout.write(f"\n{image} pushed to {self.REPOSITORY_NAME}")

    def main(self, is_tag=False, is_push=False):
        """
            python -m handle_docker_images --tag --push
        """
        if is_tag:
            self.tag_images()

        if is_push:
            self.push_images()


if __name__ == "__main__":
    """
        Приклад запуску:
        python -m handle_docker_images --tag --push
    """
    parser = argparse.ArgumentParser(
        description=r'Скрипт для заливки докер образів в локальний репозиторій',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--tag", action="store_true", help="tag images for local repo")
    parser.add_argument("--push", action="store_true", help="push images to repo")

    args = parser.parse_args()
    handler = LocalRegistryDockerImagesHandler()
    handler.main(is_tag=args.tag, is_push=args.push)
