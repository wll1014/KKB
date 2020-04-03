#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'
import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'ops.settings'
django.setup()

logger = logging.getLogger('ops.' + __name__)

from platreport.generate_report_data import ReportDateGenerator

if __name__ == '__main__':
    rdg = ReportDateGenerator()
    # rdg = ReportDateGenerator(includes=['transmit_resource'])
    rdg.generate_handler()
