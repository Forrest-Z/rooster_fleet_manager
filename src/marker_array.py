#!/usr/bin/env python

import rospy
from visualization_msgs.msg import Marker, MarkerArray
from JobManager.Location import Location

#launch the script and then open RViz, add "MarkerArray" view, choose the right topic.

#init node here in order to have rospy.get_rostime() later
rospy.init_node('marker_publisher_node', anonymous=True)

#Each location displays as two markers: a semi-transparent purple screen and white text label. 
#Each marker is created by a corresponding function
def create_sphere_marker(name, x_coordinate, y_coordinate, id):
    sphere_name = name + '_sphere'
    sphere_name = Marker()
    sphere_name.header.frame_id = "/map"
    sphere_name.header.stamp    = rospy.get_rostime()
    sphere_name.id = id
    sphere_name.type = Marker.SPHERE
    sphere_name.action = Marker.ADD
    sphere_name.pose.position.x = x_coordinate
    sphere_name.pose.position.y = y_coordinate
    sphere_name.pose.position.z = 0
    sphere_name.pose.orientation.x = 0
    sphere_name.pose.orientation.y = 0
    sphere_name.pose.orientation.z = 0.0
    sphere_name.pose.orientation.w = 1.0
    sphere_name.scale.x = 0.5
    sphere_name.scale.y = 0.5
    sphere_name.scale.z = 0.5
    sphere_name.color.r = 1.0
    sphere_name.color.g = 0.0
    sphere_name.color.b = 1.0
    # This has to be, otherwise it will be transparent
    sphere_name.color.a = 0.5
    # If we want it forever, 0, otherwise seconds before desapearing
    sphere_name.lifetime = rospy.Duration(0)
    return sphere_name

def create_text_marker(name, x_coordinate, y_coordinate, id):
    text_name = name + '_text'
    text_name = Marker()
    text_name.header.frame_id = "/map"
    text_name.header.stamp    = rospy.get_rostime()
    text_name.id = id
    text_name.type = Marker.TEXT_VIEW_FACING
    text_name.action = Marker.ADD
    text_name.pose.position.x = x_coordinate
    text_name.pose.position.y = y_coordinate
    text_name.pose.position.z = 1
    text_name.pose.orientation.x = 0
    text_name.pose.orientation.y = 0
    text_name.pose.orientation.z = 0.0
    text_name.pose.orientation.w = 1.0
    text_name.scale.z = 1
    text_name.color.r = 1.0
    text_name.color.g = 1.0
    text_name.color.b = 1.0
    text_name.color.a = 1.0
    text_name.lifetime = rospy.Duration(0)
    text_name.text = name
    return text_name

#creating object (array)
marker_array = MarkerArray()


location_dict = {
            "loc01" : Location("loc01", "Storage #1", -0.5, -2.5, 1.57),

            "loc02" : Location("loc02", "Assembly station #1", 4.5, 2.5, 3.1415/2.0),

            "loc03" : Location("loc03", "Storage #2", -2.0, 0.0, 3.1415),

            "loc04" : Location("loc04", "Assembly station #2", -5.0, 4.5, 6.283)
        }

#Go through all the locations.
for key in location_dict:
    index = key
    marker_object = create_sphere_marker(location_dict[index].name, location_dict[index].x, location_dict[index].y, int(location_dict[index].id[3:]))
    marker_array.markers.append(marker_object)    
    text_object = create_text_marker(location_dict[index].name, location_dict[index].x, location_dict[index].y, int(location_dict[index].id[3:])+100)
    marker_array.markers.append(text_object)
#marker_object = create_sphere_marker('Storage 1', 2, 3, 1)
#marker_array.markers.append(marker_object)

#text_object = create_text_marker('Storage 1', 2, 3, 2)
#marker_array.markers.append(text_object)

publisher = rospy.Publisher('/visualization_marker_array', MarkerArray, queue_size=1)

rate = rospy.Rate(1)

while not rospy.is_shutdown():
    publisher.publish(marker_array)
    rate.sleep()