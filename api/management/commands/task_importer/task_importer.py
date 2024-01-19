import sys
from unittest import mock

import openpyxl

from api.CONSTANTS import SCALE_RULES_FOR_IMPORT_EXCEL
from api.models import Department, User
from api.serializers import TaskSerializer
from rest_framework.exceptions import ValidationError


class TaskImporter:

    def __init__(self):
        self.sheet = None
        # self.incorrect_rows = []
        # self.list_of_tasks_data = []

    def _import_excel_file(self, file):
        book = openpyxl.open(file, read_only=True)
        self.sheet = book.active

    def _process_row(self, row):
        department_name = self.sheet[row][8].value
        department = Department.objects.get(name=department_name)

        task_data = {
            "scale": SCALE_RULES_FOR_IMPORT_EXCEL.get(self.sheet[row][0].value),
            "name": self.sheet[row][1].value,
            "year": self.sheet[row][2].value,
            "category": self.sheet[row][3].value,
            "editing_time_estimate": self.sheet[row][4].value,
            "correcting_time_estimate": self.sheet[row][5].value,
            "tc_time_estimate": self.sheet[row][6].value,
            "quarter": self.sheet[row][7].value,
            "department": department.id,
        }
        admin_user = User.objects.filter(username='admin').first()
        mock_context = {
            "request": mock.MagicMock(
                user=admin_user,  # Mock a user object
                method="POST"  # Set the request method to "POST"
            )
        }
        serializer = TaskSerializer(data=task_data, context=mock_context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def _parsing_excel_file(self):
        self.counter = 0
        for row in range(4, self.sheet.max_row + 1):
            self.counter += 1
            if not self.sheet[row][8].value:
                break
            try:
                self._process_row(row)
            except ValidationError as e:
                print(f"Error in row {self.sheet[row]}")
                print(f"{self.counter=}")
                for index in range(8):
                    print(f"field {index + 1} with value {self.sheet[row][index].value}")
                    raise e

        # if self.incorrect_rows: # Todo Повернутись, коли будуть виправлені валідації в TaskSerializer
        #     sys.stdout.write("\r-----------------------------------------------------\n")
        #     sys.stdout.write("Correct the errors below and try again:\n")
        #     for inc_row in self.incorrect_rows:
        #         sys.stdout.write(f"{inc_row}\n")
        #     sys.exit(3)

    def run(self, file):
        self._import_excel_file(file)
        self._parsing_excel_file()

