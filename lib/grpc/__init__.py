# -*- coding: utf-8 -*-
"""
Stub grpc module for REST-only usage.

This provides minimal stubs to satisfy imports when using google-generativeai
with REST transport only (no actual gRPC functionality).
"""

from enum import Enum

# Version info for compatibility
__version__ = "1.0.0-stub"


class StatusCode(Enum):
    """gRPC status codes - stub for import compatibility.
    
    Values are tuples (int_code, description) matching real grpc.StatusCode format.
    This allows code like `x.value[0]` to work correctly.
    """
    OK = (0, "ok")
    CANCELLED = (1, "cancelled")
    UNKNOWN = (2, "unknown")
    INVALID_ARGUMENT = (3, "invalid argument")
    DEADLINE_EXCEEDED = (4, "deadline exceeded")
    NOT_FOUND = (5, "not found")
    ALREADY_EXISTS = (6, "already exists")
    PERMISSION_DENIED = (7, "permission denied")
    RESOURCE_EXHAUSTED = (8, "resource exhausted")
    FAILED_PRECONDITION = (9, "failed precondition")
    ABORTED = (10, "aborted")
    OUT_OF_RANGE = (11, "out of range")
    UNIMPLEMENTED = (12, "unimplemented")
    INTERNAL = (13, "internal")
    UNAVAILABLE = (14, "unavailable")
    DATA_LOSS = (15, "data loss")
    UNAUTHENTICATED = (16, "unauthenticated")


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


class UnaryUnaryMultiCallable:
    """Stub for grpc.UnaryUnaryMultiCallable"""
    pass


class UnaryStreamMultiCallable:
    """Stub for grpc.UnaryStreamMultiCallable"""
    pass


class StreamUnaryMultiCallable:
    """Stub for grpc.StreamUnaryMultiCallable"""
    pass


class StreamStreamMultiCallable:
    """Stub for grpc.StreamStreamMultiCallable"""
    pass


class UnaryUnaryClientInterceptor:
    """Stub for grpc.UnaryUnaryClientInterceptor"""
    pass


class UnaryStreamClientInterceptor:
    """Stub for grpc.UnaryStreamClientInterceptor"""
    pass


class StreamUnaryClientInterceptor:
    """Stub for grpc.StreamUnaryClientInterceptor"""
    pass


class StreamStreamClientInterceptor:
    """Stub for grpc.StreamStreamClientInterceptor"""
    pass


class Compression(Enum):
    """Compression options - stub."""
    NoCompression = (0, "identity")
    Deflate = (1, "deflate")
    Gzip = (2, "gzip")


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
