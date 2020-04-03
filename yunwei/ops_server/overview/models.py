from django.db import models
from hosts.models import MachineProfile


# Create your models here.

class ProvinceModel(models.Model):
    class Meta:
        db_table = 'province'

    name = models.CharField(max_length=32)


class CityModel(models.Model):
    class Meta:
        db_table = 'city'

    name = models.CharField(max_length=32)
    province = models.ForeignKey(to=ProvinceModel, on_delete=models.CASCADE, db_constraint=False)


class GisConfModel(models.Model):
    class Meta:
        db_table = 'gis_conf'

    province = models.OneToOneField(to=ProvinceModel, null=True, on_delete=models.CASCADE, db_constraint=False)
    city = models.OneToOneField(to=CityModel, null=True, on_delete=models.CASCADE, db_constraint=False)


class GisMachineRoomModel(models.Model):
    class Meta:
        db_table = 'gis_machine_room'

    moid = models.CharField(max_length=64, db_index=True, blank=True, unique=True,
                            null=True, verbose_name='机房moid')
    name = models.CharField(max_length=128)
    coordinate_str = models.CharField(max_length=64, blank=True, default=None)


class GisTerminalModel(models.Model):
    class Meta:
        db_table = 'gis_terminal'

    moid = models.CharField(max_length=64, db_index=True, blank=True, unique=True,
                            null=True, verbose_name='终端moid')
    name = models.CharField(max_length=128)
    coordinate_str = models.CharField(max_length=64, blank=True, default=None)
    group_name = models.CharField(max_length=64, null=True, default=None)


class GisPeripheralModel(models.Model):
    class Meta:
        db_table = 'gis_peripheral'

    moid = models.CharField(max_length=64, db_index=True, blank=True, unique=True,
                            null=True, verbose_name='外设moid')
    name = models.CharField(max_length=128)
    coordinate_str = models.CharField(max_length=64, blank=True, default=None)
