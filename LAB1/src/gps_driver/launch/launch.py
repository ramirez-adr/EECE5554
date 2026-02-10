from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    port_arg = DeclareLaunchArgument(
        'port',
        default_value='/dev/ttyUSB0',
        description='Serial port for GPS puck'
    )

    port = LaunchConfiguration('port')

    driver_node = Node(
        package='gps_driver',
        executable='driver',   # from setup.py entry_points
        name='gps_driver',
        output='screen',
        arguments=['--port', port],   # passes argparse flag
    )

    return LaunchDescription([
        port_arg,
        driver_node
    ])
