#!/usr/bin/env python3
# coding: utf-8
from django.db import connections
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

__author__ = 'wanglei_sxcpx@kedacom.com'

from rest_framework import serializers
from warning.models import *
import logging

logger = logging.getLogger('ops.' + __name__)


class WarningCodeSerializer(serializers.ModelSerializer):
    class Meta:
        # fields = '__all__'
        exclude = ('suggestion',)
        model = WarningCodeModel

    sub = serializers.SerializerMethodField()

    def get_sub(self, obj):
        sub_count = SubWarningCodeModel.objects.filter(sub_code=obj.code).count()
        if sub_count:
            return 1
        return 0


class WatningThresholdsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = WarningThresholdModel
        read_only_fields = ('name', 'type')


class SubWarningCodeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = SubWarningCodeModel

    def validate_sub_code(self, attrs):
        is_valid_code = WarningCodeModel.objects.filter(code=attrs).count()
        if not is_valid_code:
            raise serializers.ValidationError('未知的告警码')
        return attrs

    sub_code_detail = serializers.SerializerMethodField()

    def get_sub_code_detail(self, obj):
        code = obj.sub_code
        detail = WarningCodeModel.objects.filter(code=code).first()
        return {
            'name': detail.name,
            'level': detail.level,
            'type': detail.type
        }


class RulesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = WarningNotifyRuleModel

    persons = serializers.SerializerMethodField()
    notice_method = serializers.SerializerMethodField()
    sub_codes = serializers.SerializerMethodField()

    def get_persons(self, obj):
        users = obj.warningnotifyusermodel_set.all()
        s_users = UsersSerializer(users, many=True)

        return [data.get('user_name') for data in s_users.data]

    def get_notice_method(self, obj):
        methods = []
        if WarningNotifyEmailModel.objects.filter(warning_notify_id=obj.pk).count():
            methods.append('email')
        if WarningNotifyPhoneModel.objects.filter(warning_notify_id=obj.pk).count():
            methods.append('sms')
        if WarningNotifyWeChatModel.objects.filter(warning_notify_id=obj.pk).count():
            methods.append('wechat')
        return methods

    def get_sub_codes(self, obj):
        sub_codes = {
            "other": [],
            "server": [],
            "terminal": [],
            "mcu": []
        }
        codes = WarningNotifySubCodeModel.objects.filter(warning_notify_id=obj.pk)
        for code in codes:
            if WarningCodeModel.objects.filter(code=code.sub_code).count():
                warning_type = WarningCodeModel.objects.filter(code=code.sub_code).first().type
                sub_codes.get(warning_type).append(code.sub_code)

        return sub_codes


class RulesDetailSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = WarningNotifyRuleModel

    persons = serializers.SerializerMethodField()
    notice_method = serializers.SerializerMethodField()
    sub_codes = serializers.SerializerMethodField()

    def get_persons(self, obj):
        users = obj.warningnotifyusermodel_set.all()
        s_users = UsersSerializer(users, many=True)

        return s_users.data

    def get_notice_method(self, obj):
        methods = []
        if WarningNotifyEmailModel.objects.filter(warning_notify_id=obj.pk).count():
            methods.append('email')
        if WarningNotifyPhoneModel.objects.filter(warning_notify_id=obj.pk).count():
            methods.append('sms')
        if WarningNotifyWeChatModel.objects.filter(warning_notify_id=obj.pk).count():
            methods.append('wechat')
        return methods

    def get_sub_codes(self, obj):
        sub_codes = {
            "other": [],
            "server": [],
            "terminal": [],
            "mcu": []
        }
        codes = WarningNotifySubCodeModel.objects.filter(warning_notify_id=obj.pk)
        for code in codes:
            if WarningCodeModel.objects.filter(code=code.sub_code).count():
                warning_type = WarningCodeModel.objects.filter(code=code.sub_code).first().type
                sub_codes.get(warning_type).append(code.sub_code)

        return sub_codes


class RulesDetailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = WarningNotifyRuleModel

    persons = serializers.ListField(write_only=True, )
    sub_codes = serializers.ListField(write_only=True, )
    notice_method = serializers.ListField(write_only=True, )

    #############################################
    def create(self, validated_data):
        rule_instance = RulesSerializer(data={'name': validated_data.get('name')})
        rule_instance.is_valid()
        obj = rule_instance.save()
        users = []
        for attr, value in validated_data.items():
            if attr == 'name':
                # 已优先处理,此处跳过
                pass
            elif attr == 'persons':
                for user_id in value:
                    user = WarningNotifyUserModel.objects.filter(user_id=user_id).first()
                    with connections['movision'].cursor() as cursor:
                        sql = '''
                        SELECT up.name,ui.moid,ui.email,ui.mobile 
                        FROM user_info ui LEFT JOIN user_profile up on ui.moid=up.moid 
                        WHERE ui.moid=%s
                        '''
                        params = [user_id]
                        cursor.execute(sql, params)
                        fetchone = cursor.fetchone()
                        if fetchone:
                            user_name, user_id, user_email, user_phone = fetchone
                            if user:
                                user.email = user_email if user_email else ''
                                user.phone = user_phone if user_phone else ''
                                user.rules.add(obj)
                                user.save()
                                users.append(user)
                            else:
                                user = WarningNotifyUserModel.objects.create(
                                    user_name=user_name,
                                    user_id=user_id,
                                    email=user_email if user_email else '',
                                    phone=user_phone if user_phone else '',
                                )
                                user.rules.add(obj)
                                user.save()
                                users.append(user)
            elif attr == 'sub_codes':
                for sub_code in value:
                    WarningNotifySubCodeModel.objects.create(warning_notify_id=obj, sub_code=sub_code)
            elif attr == 'notice_method':
                logger.info(value)
                if 'wechat' in value:
                    for user in users:
                        WarningNotifyWeChatModel.objects.create(
                            warning_notify_id=obj,
                            user_name=user.user_name,
                            user_id=user.user_id
                        )
                        logger.debug('微信通知用户新增: %s, id: %s' % (user.user_name, user.user_id))
                if 'email' in value:
                    for user in users:
                        WarningNotifyEmailModel.objects.create(
                            warning_notify_id=obj,
                            user_name=user.user_name,
                            user_id=user.user_id
                        )
                        logger.debug('邮件通知用户新增: %s, id: %s' % (user.user_name, user.user_id))
                if 'sms' in value:
                    for user in users:
                        WarningNotifyPhoneModel.objects.create(
                            warning_notify_id=obj,
                            user_name=user.user_name,
                            user_id=user.user_id
                        )
                        logger.debug('短信通知用户新增: %s, id: %s' % (user.user_name, user.user_id))

        return validated_data

    #############################################
    def validate(self, attrs):
        count = WarningNotifyRuleModel.objects.all().count()
        if count >= 15:
            raise serializers.ValidationError('最多创建15条规则')
        return attrs


class RulesDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = WarningNotifyRuleModel

    persons = serializers.ListField(write_only=True, )
    sub_codes = serializers.ListField(write_only=True, )
    notice_method = serializers.ListField(write_only=True, )

    #############################################
    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        users = []

        if validated_data.get('name'):
            name_value = validated_data['name']
            setattr(instance, 'name', name_value)
            instance.save()
        for attr, value in validated_data.items():
            if attr == 'name':
                # 已提前处理
                pass
            elif attr == 'persons':
                # 删除所有此规则的通知用户
                for warningnotifyusermodel_set in instance.warningnotifyusermodel_set.all():
                    warningnotifyusermodel_set.rules.remove(instance)
                # 添加修改的此规则的通知用户
                for user_id in value:
                    user = WarningNotifyUserModel.objects.filter(user_id=user_id).first()
                    with connections['movision'].cursor() as cursor:
                        sql = '''
                        SELECT up.name,ui.moid,ui.email,ui.mobile 
                        FROM user_info ui LEFT JOIN user_profile up on ui.moid=up.moid 
                        WHERE ui.moid=%s
                        '''
                        params = [user_id]
                        cursor.execute(sql, params)
                        fetchone = cursor.fetchone()
                        logger.info(fetchone)
                        if fetchone:
                            user_name, user_id, user_email, user_phone = fetchone
                            if user:
                                user.rules.add(instance)
                                user.email = user_email if user_email else ''
                                user.phone = user_phone if user_phone else ''
                                user.save()
                                users.append(user)
                            else:
                                user = WarningNotifyUserModel.objects.create(
                                    user_name=user_name,
                                    user_id=user_id,
                                    email=user_email if user_email else '',
                                    phone=user_phone if user_phone else '',
                                )
                                user.rules.add(instance)
                                user.save()
                                users.append(user)

            elif attr == 'sub_codes':
                # 删除所有此规则的订阅告警码
                for warningnotifysubcodemodel_set in instance.warningnotifysubcodemodel_set.all():
                    warningnotifysubcodemodel_set.delete()
                # 添加修改的此规则的订阅告警码
                for sub_code in value:
                    WarningNotifySubCodeModel.objects.create(warning_notify_id=instance, sub_code=sub_code)
            elif attr == 'notice_method':
                WarningNotifyWeChatModel.objects.filter(warning_notify_id=instance).delete()
                WarningNotifyEmailModel.objects.filter(warning_notify_id=instance).delete()
                WarningNotifyPhoneModel.objects.filter(warning_notify_id=instance).delete()
                logger.info(value)
                logger.info(users)
                if 'wechat' in value:
                    for user in users:
                        WarningNotifyWeChatModel.objects.create(
                            warning_notify_id=instance,
                            user_name=user.user_name,
                            user_id=user.user_id
                        )
                        logger.debug('微信通知用户新增: %s, id: %s' % (user.user_name, user.user_id))
                if 'email' in value:
                    for user in users:
                        WarningNotifyEmailModel.objects.create(
                            warning_notify_id=instance,
                            user_name=user.user_name,
                            user_id=user.user_id
                        )
                        logger.debug('邮件通知用户新增: %s, id: %s' % (user.user_name, user.user_id))
                if 'sms' in value:
                    for user in users:
                        WarningNotifyPhoneModel.objects.create(
                            warning_notify_id=instance,
                            user_name=user.user_name,
                            user_id=user.user_id
                        )
                        logger.debug('短信通知用户新增: %s, id: %s' % (user.user_name, user.user_id))

        return instance


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        # fields = '__all__'
        exclude = ('rules', 'id')
        model = WarningNotifyUserModel


class ServerWarningRepairedSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = ServerWarningRepairedModel

    platform_domain_name = serializers.SerializerMethodField()
    platform_domain_moid = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_platform_domain_moid(self, obj):
        with connections['luban'].cursor() as cursor:
            sql = '''
            SELECT domain_moid FROM machine_room_info WHERE machine_room_moid=%s
            '''
            parmas = [obj.machine_room_moid]

            cursor.execute(sql, parmas)
            fetchone = cursor.fetchone()
        return fetchone[0] if fetchone else ''

    def get_platform_domain_name(self, obj):
        with connections['luban'].cursor() as cursor:
            sql = '''
            SELECT domain_name FROM machine_room_info mri 
            LEFT JOIN domain_info di on mri.domain_moid=di.domain_moid 
            WHERE machine_room_moid=%s
            '''
            parmas = [obj.machine_room_moid]

            cursor.execute(sql, parmas)
            fetchone = cursor.fetchone()
        return fetchone[0] if fetchone else ''

    def get_name(self, obj):
        name_queryset = WarningCodeModel.objects.filter(code=obj.code).first()
        name = name_queryset.name
        return name


class ServerWarningUnrepairedSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = ServerWarningUnrepairedModel

    platform_domain_name = serializers.SerializerMethodField()
    platform_domain_moid = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_platform_domain_moid(self, obj):
        with connections['luban'].cursor() as cursor:
            sql = '''
            SELECT domain_moid FROM machine_room_info WHERE machine_room_moid=%s
            '''
            parmas = [obj.machine_room_moid]

            cursor.execute(sql, parmas)
            fetchone = cursor.fetchone()
        return fetchone[0] if fetchone else ''

    def get_platform_domain_name(self, obj):
        with connections['luban'].cursor() as cursor:
            sql = '''
            SELECT domain_name FROM machine_room_info mri 
            LEFT JOIN domain_info di on mri.domain_moid=di.domain_moid 
            WHERE machine_room_moid=%s
            '''
            parmas = [obj.machine_room_moid]

            cursor.execute(sql, parmas)
            fetchone = cursor.fetchone()
        return fetchone[0] if fetchone else ''

    def get_name(self, obj):
        name_queryset = WarningCodeModel.objects.filter(code=obj.code).first()
        name = name_queryset.name
        return name


class TerminalWarningRepairedSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = TerminalWarningRepairedModel

    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        name_queryset = WarningCodeModel.objects.filter(code=obj.code).first()
        name = name_queryset.name
        return name


class TerminalWarningUnrepairedSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = TerminalWarningUnrepairedModel

    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        name_queryset = WarningCodeModel.objects.filter(code=obj.code).first()
        name = name_queryset.name
        return name
