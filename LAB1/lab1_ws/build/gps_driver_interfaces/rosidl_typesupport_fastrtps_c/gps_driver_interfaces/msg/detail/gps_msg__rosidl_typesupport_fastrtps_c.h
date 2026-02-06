// generated from rosidl_typesupport_fastrtps_c/resource/idl__rosidl_typesupport_fastrtps_c.h.em
// with input from gps_driver_interfaces:msg/GpsMsg.idl
// generated code does not contain a copyright notice
#ifndef GPS_DRIVER_INTERFACES__MSG__DETAIL__GPS_MSG__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
#define GPS_DRIVER_INTERFACES__MSG__DETAIL__GPS_MSG__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_


#include <stddef.h>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "gps_driver_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "gps_driver_interfaces/msg/detail/gps_msg__struct.h"
#include "fastcdr/Cdr.h"

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gps_driver_interfaces
bool cdr_serialize_gps_driver_interfaces__msg__GpsMsg(
  const gps_driver_interfaces__msg__GpsMsg * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gps_driver_interfaces
bool cdr_deserialize_gps_driver_interfaces__msg__GpsMsg(
  eprosima::fastcdr::Cdr &,
  gps_driver_interfaces__msg__GpsMsg * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gps_driver_interfaces
size_t get_serialized_size_gps_driver_interfaces__msg__GpsMsg(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gps_driver_interfaces
size_t max_serialized_size_gps_driver_interfaces__msg__GpsMsg(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gps_driver_interfaces
bool cdr_serialize_key_gps_driver_interfaces__msg__GpsMsg(
  const gps_driver_interfaces__msg__GpsMsg * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gps_driver_interfaces
size_t get_serialized_size_key_gps_driver_interfaces__msg__GpsMsg(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gps_driver_interfaces
size_t max_serialized_size_key_gps_driver_interfaces__msg__GpsMsg(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gps_driver_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, gps_driver_interfaces, msg, GpsMsg)();

#ifdef __cplusplus
}
#endif

#endif  // GPS_DRIVER_INTERFACES__MSG__DETAIL__GPS_MSG__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
