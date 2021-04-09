import hashlib
import json
import logging
import random
import traceback
from typing import Iterator

import allauth
from django import shortcuts
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.core.paginator import Paginator
from django.db.models import ExpressionWrapper, F, fields
from django.dispatch import receiver
from django.utils.timezone import datetime, timedelta
from django_grpc.signals import grpc_request_started
from google import protobuf
from prometheus_client import start_http_server

from chat_python_lib.chat.grpcs.vip import VipServiceServicer
from chat_python_lib.utils import utils
from com.chat import (
    base_pb2,
    base_pb2_grpc,
    dynamic_pb2,
    dynamic_pb2_grpc,
    login_pb2,
    login_pb2_grpc,
    match_pb2,
    match_pb2_grpc,
    user_pb2,
    user_pb2_grpc,
    video_pb2,
    video_pb2_grpc,
    vip_pb2,
    vip_pb2_grpc,
)

from .grpcs.dynamic import CommentServiceServicer, DynamicServiceServicer
from .grpcs.login import LoginServiceServicer
from .grpcs.match import MatchServiceServicer
from .grpcs.user import UserServiceServicer
from .grpcs.video import VideoServiceServicer

logger = logging.getLogger(__name__)


@receiver(grpc_request_started)
def request_logger(request, context, *args, **kwargs):
    logger.info(request)
    logger.info(context)


def grpc_hook(server):
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(),
                                                    server)
    login_pb2_grpc.add_LoginServiceServicer_to_server(LoginServiceServicer(),
                                                      server)
    dynamic_pb2_grpc.add_DynamicServiceServicer_to_server(
        DynamicServiceServicer(), server)
    dynamic_pb2_grpc.add_CommentServiceServicer_to_server(
        CommentServiceServicer(), server)
    video_pb2_grpc.add_VideoServiceServicer_to_server(VideoServiceServicer(),
                                                      server)
    match_pb2_grpc.add_MatchServiceServicer_to_server(MatchServiceServicer(),
                                                      server)
    vip_pb2_grpc.add_VipServiceServicer_to_server(VipServiceServicer(), server)
    start_http_server(settings.METRICS_PORT)

    try:
        from grpc_reflection.v1alpha import reflection

        SERVICE_NAMES = (
            login_pb2.DESCRIPTOR.services_by_name['LoginService'].full_name,
            user_pb2.DESCRIPTOR.services_by_name['UserService'].full_name,
            dynamic_pb2.DESCRIPTOR.services_by_name['DynamicService'].
            full_name,
            dynamic_pb2.DESCRIPTOR.services_by_name['CommentService'].
            full_name,
            video_pb2.DESCRIPTOR.services_by_name['VideoService'].full_name,
            match_pb2.DESCRIPTOR.services_by_name['MatchService'].full_name,
            vip_pb2.DESCRIPTOR.services_by_name['VipService'].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)
    except:
        traceback.print_exc()
