# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: producer-types.proto
# flake8: noqa
# mypy: ignore-errors
# pylint: disable-all
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x14producer-types.proto\x12\x1dwatson_core_data_model.common"+\n\nProducerId\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t"P\n\x10ProducerPriority\x12<\n\tproducers\x18\x01 \x03(\x0b\x32).watson_core_data_model.common.ProducerIdB{\n!com.ibm.watson.runtime.wisdom_extP\x01ZTgithub.ibm.com/ai-foundation/wisdom_ext_runtime_client/watson_core_data_model/commonb\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "producer_types_pb2", globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"\n!com.ibm.watson.runtime.wisdom_extP\001ZTgithub.ibm.com/ai-foundation/wisdom_ext_runtime_client/watson_core_data_model/common"
    _PRODUCERID._serialized_start = 55
    _PRODUCERID._serialized_end = 98
    _PRODUCERPRIORITY._serialized_start = 100
    _PRODUCERPRIORITY._serialized_end = 180
# @@protoc_insertion_point(module_scope)
