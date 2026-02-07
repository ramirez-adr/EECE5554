from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # argument we pass at launch time
    port_arg = DeclareLaunchArgument(
        'port',
        default_value='/dev/ttyUSB0',
        description='Serial port for GPS device'
    )

    driver_node = Node(
        package='gps_driver',
        executable='driver.py',   # matches ros2 pkg executables output
        name='gps_driver',
        output='screen',
        arguments=['--port', LaunchConfiguration('port')]
    )

    return LaunchDescription([
        port_arg,
        driver_node
    ])
