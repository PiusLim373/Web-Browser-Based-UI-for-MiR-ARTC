cmake_minimum_required(VERSION 2.8.3)
project(my_pcl_tutorial)
SET(CMAKE_CXX_FLAGS "-std=c++0x")

find_package(catkin REQUIRED COMPONENTS
  pcl_conversions
  pcl_ros
  roscpp
  sensor_msgs
)
find_package(Boost REQUIRED system)

find_package(cpprestsdk REQUIRED)

include_directories(
  ${catkin_INCLUDE_DIRS}
)
catkin_package()

add_executable(StopMiR src/extractpoint.cpp)
target_link_libraries(StopMiR ${catkin_LIBRARIES} cpprestsdk::cpprest ${Boost_SYSTEM_LIBRARY})

