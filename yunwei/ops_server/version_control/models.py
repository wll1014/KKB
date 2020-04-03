import os
from django.db import models
from ops.settings import MEDIA_ROOT

version_control_relative_path = 'version_control'
Platform_relative_path = 'platform'
Terminal_relative_path = 'terminal'
OS_relative_path = 'os'

# Create your models here.

ROOT_PLATFORM = os.path.join(MEDIA_ROOT, version_control_relative_path, Platform_relative_path)
ROOT_TERMINAL = os.path.join(MEDIA_ROOT, version_control_relative_path, Terminal_relative_path)
ROOT_OS = os.path.join(MEDIA_ROOT, version_control_relative_path, OS_relative_path)


class PlatFormVersionModel(models.Model):
    """
    平台版本
    """
    upload_time = models.DateTimeField(auto_now_add=True, help_text='上传日期')
    uploader = models.CharField(max_length=128, help_text='上传用户')
    file = models.FilePathField(path=ROOT_PLATFORM, recursive=True, allow_files=True, allow_folders=False,
                                help_text='版本文件绝对路径')
    name = models.CharField(max_length=64, help_text='版本文件')
    version = models.CharField(max_length=128, blank=True, default="", help_text='版本信息')
    describe = models.CharField(max_length=256, blank=True, default="", help_text='版本描述')
    postscript = models.CharField(max_length=512, blank=True, default="", help_text='备注')

    class Meta:
        db_table = "platform_version"


class TerminalVersionModel(models.Model):
    """
    终端版本
    """
    upload_time = models.DateTimeField(auto_now_add=True, help_text='上传日期')
    uploader = models.CharField(max_length=128, help_text='上传用户')
    file = models.FilePathField(path=ROOT_TERMINAL, recursive=True, allow_files=True, allow_folders=False,
                                help_text='版本文件绝对路径')
    name = models.CharField(max_length=64, help_text='版本文件')
    version = models.CharField(max_length=128, blank=True, default="", help_text='版本信息')
    describe = models.CharField(max_length=256, blank=True, default="", help_text='版本描述')
    postscript = models.CharField(max_length=512, blank=True, default="", help_text='备注')

    class Meta:
        db_table = "terminal_version"


class OSVersionModel(models.Model):
    """
    操作系统版本
    """
    upload_time = models.DateTimeField(auto_now_add=True, help_text='上传日期')
    uploader = models.CharField(max_length=128, help_text='上传用户')
    file = models.FilePathField(path=ROOT_OS, recursive=True, allow_files=True, allow_folders=False,
                                help_text='版本文件绝对路径')
    name = models.CharField(max_length=64, help_text='版本文件')
    version = models.CharField(max_length=128, blank=True, default="", help_text='版本信息')
    describe = models.CharField(max_length=256, blank=True, default="", help_text='版本描述')
    postscript = models.CharField(max_length=512, blank=True, default="", help_text='备注')

    class Meta:
        db_table = "os_version"
