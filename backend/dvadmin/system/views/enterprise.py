# -*- coding: utf-8 -*-
import pypinyin
from django.db.models import Q
from rest_framework import serializers

from dvadmin.system.models import Enterprise
from dvadmin.utils.field_permission import FieldPermissionMixin
from dvadmin.utils.json_response import SuccessResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class EnterpriseSerializer(CustomModelSerializer):
    """企业序列化器"""
    pcode_count = serializers.SerializerMethodField(read_only=True)
    hasChild = serializers.SerializerMethodField()
    pcode_info = serializers.SerializerMethodField()

    def get_pcode_info(self, instance):
        pcode = Enterprise.objects.filter(code=instance.pcode_id).values("name", "code")
        return pcode

    def get_pcode_count(self, instance: Enterprise):
        return Enterprise.objects.filter(pcode=instance).count()

    def get_hasChild(self, instance):
        has_child = Enterprise.objects.filter(pcode=instance.code).exists()
        return has_child

    class Meta:
        model = Enterprise
        fields = "__all__"
        read_only_fields = ["id"]


class EnterpriseCreateUpdateSerializer(CustomModelSerializer):
    """企业创建/更新序列化器"""

    def to_internal_value(self, data):
        pinyin = ''.join([''.join(i) for i in pypinyin.pinyin(data["name"], style=pypinyin.NORMAL)])
        data["level"] = 1
        data["pinyin"] = pinyin
        data["initials"] = pinyin[0].upper() if pinyin else "#"
        pcode = data["pcode"] if 'pcode' in data else None
        if pcode:
            pcode = Enterprise.objects.get(pk=pcode)
            data["pcode"] = pcode.code
            data["level"] = pcode.level + 1
        return super().to_internal_value(data)

    class Meta:
        model = Enterprise
        fields = '__all__'


class EnterpriseViewSet(CustomModelViewSet, FieldPermissionMixin):
    """企业管理接口"""
    queryset = Enterprise.objects.all()
    serializer_class = EnterpriseSerializer
    create_serializer_class = EnterpriseCreateUpdateSerializer
    update_serializer_class = EnterpriseCreateUpdateSerializer
    extra_filter_class = []

    def list(self, request, *args, **kwargs):
        # 复用地区管理的列表查询逻辑（支持分页、上级筛选）
        self.request.query_params._mutable = True
        params = self.request.query_params
        known_params = {'page', 'limit', 'pcode'}
        other_params_exist = any(param not in known_params for param in params)
        
        if other_params_exist:
            queryset = self.queryset.filter(enable=True)
        else:
            pcode = params.get('pcode', None)
            params['limit'] = 999
            if params and pcode:
                queryset = self.queryset.filter(enable=True, pcode=pcode)
            else:
                queryset = self.queryset.filter(enable=True, level=1)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, request=request)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(data=serializer.data, msg="获取成功")