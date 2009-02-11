#!/usr/bin/python2.4
# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import service
from google.protobuf import service_reflection
from google.protobuf import descriptor_pb2


_USER_GENDER = descriptor.EnumDescriptor(
  name='Gender',
  full_name='lastfm.User.Gender',
  filename='Gender',
  values=[
    descriptor.EnumValueDescriptor(
      name='MALE', index=0, number=0,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='FEMALE', index=1, number=1,
      options=None,
      type=None),
  ],
  options=None,
)


_GROUP = descriptor.Descriptor(
  name='Group',
  full_name='lastfm.Group',
  filename='lastfm.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='groupName', full_name='lastfm.Group.groupName', index=0,
      number=1, type=9, cpp_type=9, label=2,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_FRIEND = descriptor.Descriptor(
  name='Friend',
  full_name='lastfm.Friend',
  filename='lastfm.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='friendName', full_name='lastfm.Friend.friendName', index=0,
      number=1, type=9, cpp_type=9, label=2,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_TRACK = descriptor.Descriptor(
  name='Track',
  full_name='lastfm.Track',
  filename='lastfm.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='artist', full_name='lastfm.Track.artist', index=0,
      number=1, type=9, cpp_type=9, label=2,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='trackName', full_name='lastfm.Track.trackName', index=1,
      number=2, type=9, cpp_type=9, label=2,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='playcount', full_name='lastfm.Track.playcount', index=2,
      number=3, type=5, cpp_type=1, label=2,
      default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_USER = descriptor.Descriptor(
  name='User',
  full_name='lastfm.User',
  filename='lastfm.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='username', full_name='lastfm.User.username', index=0,
      number=1, type=9, cpp_type=9, label=2,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='name', full_name='lastfm.User.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='age', full_name='lastfm.User.age', index=2,
      number=3, type=5, cpp_type=1, label=1,
      default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='country', full_name='lastfm.User.country', index=3,
      number=4, type=9, cpp_type=9, label=1,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='executions', full_name='lastfm.User.executions', index=4,
      number=5, type=5, cpp_type=1, label=1,
      default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='average', full_name='lastfm.User.average', index=5,
      number=6, type=2, cpp_type=6, label=1,
      default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='homepage', full_name='lastfm.User.homepage', index=6,
      number=7, type=9, cpp_type=9, label=1,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='userSince', full_name='lastfm.User.userSince', index=7,
      number=8, type=9, cpp_type=9, label=1,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='resetedDate', full_name='lastfm.User.resetedDate', index=8,
      number=13, type=9, cpp_type=9, label=1,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='gender', full_name='lastfm.User.gender', index=9,
      number=9, type=14, cpp_type=8, label=1,
      default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='groups', full_name='lastfm.User.groups', index=10,
      number=10, type=11, cpp_type=10, label=3,
      default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='friends', full_name='lastfm.User.friends', index=11,
      number=11, type=11, cpp_type=10, label=3,
      default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='tracks', full_name='lastfm.User.tracks', index=12,
      number=12, type=11, cpp_type=10, label=3,
      default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
    _USER_GENDER,
  ],
  options=None)


_USER.fields_by_name['gender'].enum_type = _USER_GENDER
_USER.fields_by_name['groups'].message_type = _GROUP
_USER.fields_by_name['friends'].message_type = _FRIEND
_USER.fields_by_name['tracks'].message_type = _TRACK

class Group(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _GROUP

class Friend(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _FRIEND

class Track(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _TRACK

class User(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _USER
