# Web-Browser-Based-UI-for-MiR-ARTC
Pius' Final Year Project, title: Web Bowser-Based for Monitoring and Controlling Robot

# Flask Web Server
Prerequisite: 

How to use: 
1. Switch on MiR
2. On Intel MiniPC, run main.py
3. On your smartphone / tablet, connect to agv_network
4. Open any browser and type in 192.168.12.149 (IP address of MiniPC)

# Safe Navigation
Package needed:
1. ROS
2. realsense-ros (to start D435 camera node and start publishing data to /camera/depth_registered/points), available here: https://github.com/IntelRealSense/realsense-ros
3. perception_pcl (to downsample the camera feed and truncate data 2 meters away), available here: https://github.com/ros-perception/perception_pcl
4. PCL Library (to abstract the Z-distance of point cloud and analyse the data), follow instruction here: https://gist.github.com/IgniparousTempest/ce5fadbe742526d10d6bdbf15c3a3fe7
