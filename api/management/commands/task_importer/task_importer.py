import openpyxl

from api.models import Department
from api.serializers import TaskSerializer


class TaskImporter():

    def __init__(self):
        self.sheet = None
        self.list_of_tasks_data = []
    def _import_excel_file(self, file):
        book = openpyxl.open(file, read_only=True)
        self.sheet = book.active

    def _parsing_excel_file(self):
        list_of_tasks_data = []
        for row in range(4, self.sheet.max_row + 1):
            task_data = {
                "scale": self.sheet[row][0].value,
                "name": self.sheet[row][1].value,
                "year": self.sheet[row][2].value,
                "category": self.sheet[row][3].value,
                "editing_time_estimate": self.sheet[row][4].value,
                "correcting_time_estimate": self.sheet[row][5].value,
                "tc_time_estimate": self.sheet[row][6].value,
                "quarter": self.sheet[row][7].value,
                "department": Department.objects.get_or_none(name=self.sheet[row][8].value),
            }
            self.list_of_tasks_data.append(task_data)

    def _create_tasks_from_list(self):
        serializer = TaskSerializer(many=True)
        serializer.create(self.list_of_tasks_data)

    def run(self, file):
        self._import_excel_file(file)
        self._parsing_excel_file()
        self._create_tasks_from_list()


