# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: proto/sdxl_turbo.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'proto/sdxl_turbo.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16proto/sdxl_turbo.proto\x12\nsdxl_turbo\"\x84\x01\n\x0eImg2ImgRequest\x12\r\n\x05image\x18\x01 \x01(\x0c\x12\x0e\n\x06prompt\x18\x02 \x01(\t\x12\x1b\n\x13num_inference_steps\x18\x03 \x01(\x05\x12\x10\n\x08strength\x18\x04 \x01(\x02\x12\x16\n\x0eguidance_scale\x18\x05 \x01(\x02\x12\x0c\n\x04seed\x18\x06 \x01(\x03\"Z\n\x0fImg2ImgResponse\x12\x17\n\x0fgenerated_image\x18\x01 \x01(\x0c\x12\x12\n\nrequest_id\x18\x02 \x01(\x03\x12\x1a\n\x12processing_time_ms\x18\x03 \x01(\x03\"\x9d\x01\n\x13Img2ImgBatchRequest\x12\r\n\x05image\x18\x01 \x01(\x0c\x12\x0e\n\x06prompt\x18\x02 \x01(\t\x12\x12\n\nnum_images\x18\x03 \x01(\x05\x12\x1b\n\x13num_inference_steps\x18\x04 \x01(\x05\x12\x10\n\x08strength\x18\x05 \x01(\x02\x12\x16\n\x0eguidance_scale\x18\x06 \x01(\x02\x12\x0c\n\x04seed\x18\x07 \x01(\x03\"`\n\x14Img2ImgBatchResponse\x12\x18\n\x10generated_images\x18\x01 \x03(\x0c\x12\x12\n\nrequest_id\x18\x02 \x01(\x03\x12\x1a\n\x12processing_time_ms\x18\x03 \x01(\x03\"\x14\n\x12QueueStatusRequest\"d\n\x13QueueStatusResponse\x12\x14\n\x0cqueue_length\x18\x01 \x01(\x05\x12\x1e\n\x16\x65stimated_wait_time_ms\x18\x02 \x01(\x03\x12\x17\n\x0f\x61\x63tive_requests\x18\x03 \x01(\x05\x32\x82\x02\n\x10SDXLTurboService\x12\x44\n\x07Img2Img\x12\x1a.sdxl_turbo.Img2ImgRequest\x1a\x1b.sdxl_turbo.Img2ImgResponse\"\x00\x12S\n\x0cImg2ImgBatch\x12\x1f.sdxl_turbo.Img2ImgBatchRequest\x1a .sdxl_turbo.Img2ImgBatchResponse\"\x00\x12S\n\x0eGetQueueStatus\x12\x1e.sdxl_turbo.QueueStatusRequest\x1a\x1f.sdxl_turbo.QueueStatusResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.sdxl_turbo_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_IMG2IMGREQUEST']._serialized_start=39
  _globals['_IMG2IMGREQUEST']._serialized_end=171
  _globals['_IMG2IMGRESPONSE']._serialized_start=173
  _globals['_IMG2IMGRESPONSE']._serialized_end=263
  _globals['_IMG2IMGBATCHREQUEST']._serialized_start=266
  _globals['_IMG2IMGBATCHREQUEST']._serialized_end=423
  _globals['_IMG2IMGBATCHRESPONSE']._serialized_start=425
  _globals['_IMG2IMGBATCHRESPONSE']._serialized_end=521
  _globals['_QUEUESTATUSREQUEST']._serialized_start=523
  _globals['_QUEUESTATUSREQUEST']._serialized_end=543
  _globals['_QUEUESTATUSRESPONSE']._serialized_start=545
  _globals['_QUEUESTATUSRESPONSE']._serialized_end=645
  _globals['_SDXLTURBOSERVICE']._serialized_start=648
  _globals['_SDXLTURBOSERVICE']._serialized_end=906
# @@protoc_insertion_point(module_scope)
