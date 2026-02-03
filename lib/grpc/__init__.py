# -*- coding: utf-8 -*-
"""
Stub grpc module for REST-only usage.

This provides minimal stubs to satisfy imports when using google-generativeai
with REST transport only (no actual gRPC functionality).
"""

from enum import IntEnum


class StatusCode(IntEnum):
    """gRPC status codes - stub for import compatibility."""
    OK = 0
    CANCELLED = 1
    UNKNOWN = 2
    INVALID_ARGUMENT = 3
    DEADLINE_EXCEEDED = 4
    NOT_FOUND = 5
    ALREADY_EXISTS = 6
    PERMISSION_DENIED = 7
    RESOURCE_EXHAUSTED = 8
    FAILED_PRECONDITION = 9
    ABORTED = 10
    OUT_OF_RANGE = 11
    UNIMPLEMENTED = 12
    INTERNAL = 13
    UNAVAILABLE = 14
    DATA_LOSS = 15
    UNAUTHENTICATED = 16


class RpcError(Exception):
    """Base class for gRPC errors - stub."""
    pass


class Call:
    """Stub for grpc.Call"""
    pass


class Channel:
    """Stub for grpc.Channel"""
    pass


class Server:
    """Stub for grpc.Server"""
    pass


class ChannelCredentials:
    """Stub for grpc.ChannelCredentials"""
    pass


class CallCredentials:
    """Stub for grpc.CallCredentials"""
    pass


class AuthMetadataPlugin:
    """Stub for grpc.AuthMetadataPlugin"""
    pass


class AuthMetadataContext:
    """Stub for grpc.AuthMetadataContext"""
    pass


class Compression(IntEnum):
    """Compression options - stub."""
    NoCompression = 0
    Deflate = 1
    Gzip = 2


# Stub functions
def insecure_channel(target, options=None, compression=None):
    """Stub for grpc.insecure_channel"""
    raise NotImplementedError("gRPC not available - use REST transport")


def secure_channel(target, credentials, options=None, compression=None):
    """Stub for grpc.secure_channel"""
    raise NotImplementedError("gRPC not available - use REST transport")


def ssl_channel_credentials(root_certificates=None, private_key=None, certificate_chain=None):
    """Stub for grpc.ssl_channel_credentials"""
    return ChannelCredentials()


def metadata_call_credentials(metadata_plugin, name=None):
    """Stub for grpc.metadata_call_credentials"""
    return CallCredentials()


def composite_channel_credentials(channel_credentials, *call_credentials):
    """Stub for grpc.composite_channel_credentials"""
    return ChannelCredentials()


def access_token_call_credentials(access_token):
    """Stub for grpc.access_token_call_credentials"""
    return CallCredentials()


def unary_unary_rpc_method_handler(behavior, request_deserializer=None, response_serializer=None):
    """Stub for grpc.unary_unary_rpc_method_handler"""
    pass


def unary_stream_rpc_method_handler(behavior, request_deserializer=None, response_serializer=None):
    """Stub for grpc.unary_stream_rpc_method_handler"""
    pass


def stream_unary_rpc_method_handler(behavior, request_deserializer=None, response_serializer=None):
    """Stub for grpc.stream_unary_rpc_method_handler"""
    pass


def stream_stream_rpc_method_handler(behavior, request_deserializer=None, response_serializer=None):
    """Stub for grpc.stream_stream_rpc_method_handler"""
    pass


def method_handlers_generic_handler(service, method_handlers):
    """Stub for grpc.method_handlers_generic_handler"""
    pass


def server(thread_pool=None, handlers=None, interceptors=None, options=None, maximum_concurrent_rpcs=None, compression=None):
    """Stub for grpc.server"""
    raise NotImplementedError("gRPC not available - use REST transport")


# For compatibility with some imports
experimental = None
_compression = Compression
