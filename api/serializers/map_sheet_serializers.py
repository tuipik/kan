from rest_framework import serializers

from kanban.settings import CURRENT_YEAR
from map_sheet.models import MapSheet


class MapSheetSerializer(serializers.ModelSerializer):

    class Meta:
        model = MapSheet
        fields = [
            'scale',
            'name',
            'row',
            'column',
            'trapeze_500k',
            'trapeze_200k',
            'trapeze_100k',
            'trapeze_50k',
            'trapeze_25k',
            'trapeze_10k',
            'year',
            'created',
            'updated',
        ]

        extra_kwargs = {
            'row': {'required': False},
            'column': {'required': False},
            'year': {'allow_null': True, 'default': CURRENT_YEAR},
        }

    def _get_row_column_trapezes_data(self):
        row_column_trapezes_data = {
            "trapeze_500k": None,
            "trapeze_200k": None,
            "trapeze_100k": None,
            "trapeze_50k": None,
            "trapeze_25k": None,
            "trapeze_10k": None,
        }

        map_sheet_name = self.validated_data["name"]

        row, column, *trapezes = map_sheet_name.split('-')

        row_column_trapezes_data['row'] = row
        row_column_trapezes_data['column'] = column

        if len(trapezes): # all except 1kk

            scale = self.validated_data.get('scale', self.instance and self.instance.scale)
            match scale:

                case 10:
                    row_column_trapezes_data["trapeze_100k"] = trapezes[0]
                    row_column_trapezes_data["trapeze_50k"] = trapezes[1]
                    row_column_trapezes_data["trapeze_25k"] = trapezes[2]
                    row_column_trapezes_data["trapeze_10k"] = trapezes[3]
                case 25:
                    row_column_trapezes_data["trapeze_100k"] = trapezes[0]
                    row_column_trapezes_data["trapeze_50k"] = trapezes[1]
                    row_column_trapezes_data["trapeze_25k"] = trapezes[2]
                case 50:
                    row_column_trapezes_data["trapeze_100k"] = trapezes[0]
                    row_column_trapezes_data["trapeze_50k"] = trapezes[1]
                case 100:
                    row_column_trapezes_data["trapeze_100k"] = trapezes[0]
                case 200:
                    row_column_trapezes_data["trapeze_200k"] = trapezes[0]
                case 500:
                    row_column_trapezes_data["trapeze_500k"] = trapezes[0]

        return row_column_trapezes_data

    def _get_map_sheet_data(self):
        map_sheet_data = {}

        if map_sheet_name := self.validated_data.get('name'):
            map_sheet_data["name"] = map_sheet_name
            map_sheet_data.update(self._get_row_column_trapezes_data())

        return map_sheet_data

    def save(self, **kwargs):
        updated_kwargs = {**kwargs, **self._get_map_sheet_data()}
        return super().save(**kwargs, **updated_kwargs)
