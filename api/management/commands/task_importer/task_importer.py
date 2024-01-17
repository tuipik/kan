import openpyxl

from api.CONSTANTS import SCALE_RULES_FOR_IMPORT_EXCEL
from api.models import Department
from api.serializers import TaskSerializer


class TaskImporter:

    def __init__(self):
        self.sheet = None
        self.list_of_tasks_data = []

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
        TaskSerializer(data=task_data).is_valid(raise_exception=True)

        self.list_of_tasks_data.append(task_data)
        print(f"{self.sheet[row][0].row} row completed ({self.sheet[row][1].value})")

    def _parsing_excel_file(self):
        self.counter = 0
        for row in range(4, self.sheet.max_row + 1):
            self.counter += 1
            if not self.sheet[row][8].value:
                break
            try:
                self._process_row(row)
            except Exception as e:
                print(f"Issue with {row=}")
                for i in range(9):

                    print(f"cell{i+1} {self.sheet[row][i].value}")
                raise e

    def _create_tasks_from_list(self):
        serializer = TaskSerializer(many=True, data=self.list_of_tasks_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print("--------------------")
        print(f"{self.counter-1} tasks were added.")
    def run(self, file):
        self._import_excel_file(file)
        self._parsing_excel_file()
        self._create_tasks_from_list()

