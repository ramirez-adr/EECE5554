cmake_minimum_required(VERSION 3.8)
project(gps_driver)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

# Generate message interfaces
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/GpsMsg.msg"
  DEPENDENCIES std_msgs
)

ament_export_dependencies(rosidl_default_runtime)

# Install your executable node script so ros2 run can see it
install(PROGRAMS
  gps_driver/driver.py
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files (if you have them)
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()
