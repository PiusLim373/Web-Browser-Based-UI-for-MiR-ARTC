#include <ros/ros.h>
#include <sensor_msgs/PointCloud2.h>
#include <geometry_msgs/Twist.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/common/common.h>
#include <pcl/PCLPointCloud2.h>
#include <pcl_ros/point_cloud.h>
#include <cpprest/http_client.h>
#include <cpprest/http_client.h>
#include <cpprest/json.h>
#include <iostream>

using namespace web;                        // Common features like URIs.
using namespace web::http;                  // Common HTTP functionality
using namespace web::http::client;          // HTTP client features
using namespace web::json;
using namespace std;

ros::Publisher pubPointCloud2;
ros::Publisher pubTwist;

int stopcount = 0;
int resetcount = 0;
const string url= "http://mir.com/api/v2.0.0/status"; //might need to change to ip address of the router
bool Stop = false; //a boolean to check if the stopping request has been sent, false = not sent before

//http put reqeust to change the state id of MiR to 4 (pause)
bool SendStop(){
	
	json::value json_data;
	json_data["state_id"] = json::value::number(4);

	http_client client(url);
	http_request request(methods::PUT);
	request.headers().add("Content-Type", "application/json");
	request.headers().add("Accept-Language", "en_US");
	request.headers().add("Authorization", "Basic YWRtaW46OGM2OTc2ZTViNTQxMDQxNWJkZTkwOGJkNGRlZTE1ZGZiMTY3YTljODczZmM0YmI4YTgxZjZmMmFiNDQ4YTkxOA==");
	request.set_body(json_data.serialize());

	http_response response;
	response = client.request(request).get();
  cout << response.status_code() <<"\n";
	if (response.status_code() == 200) {
		cout << "Stop signal sent successfully" << "\n";
    return true;
	}
  else {
    cout << "Stop signal is not successfully" << "\n";
    return false;
  }
}


void 
cloud_cb (const pcl::PointCloud<pcl::PointXYZ>::Ptr& from_sensor)
{
  // Downsampling the data and store to *downsampled
  pcl::PointCloud<pcl::PointXYZ>::Ptr downsampled (new pcl::PointCloud<pcl::PointXYZ>);
  pcl::VoxelGrid<pcl::PointXYZ> sor;
  sor.setInputCloud (from_sensor);
  sor.setLeafSize (0.1, 0.1, 0.1);
  sor.filter (*downsampled);

  //get the min and max point from the downsampled pointcloud and store to minPoint and maxPoint
  pcl::PointXYZ maxPoint, minPoint;
  pcl::getMinMax3D(*downsampled, minPoint, maxPoint);
  
  //dont print out data at infinite point
  if(minPoint.z <= 1.9 ){
    std::cout << "Min z: " << minPoint.z << std::endl;
    // send stop signal when lower than 0.45m
    if(minPoint.z <= 0.45){
      stopcount ++;
      printf("stop counter: %d\n", stopcount);
      if (stopcount >= 40){
        if (!Stop){
          cout << "Sending stop signal to MiR...\n"; 
          Stop = SendStop();
        }    
      }
    }
    else{
        resetcount ++;
        if ((resetcount >= 20) && (stopcount!= 0)){
          stopcount = 0;
          printf("false positive, resetting stop counter.");
          if (Stop){
            Stop = false;
          }
        }
    }
  }

  //publish the pointcloud for visualization
  pubPointCloud2.publish (*downsampled);

}

int
main (int argc, char** argv)
{
  // Initialize ROS
  ros::init (argc, argv, "test");
  ros::NodeHandle nh;
  // Create a ROS subscriber for the input point cloud
  ros::Subscriber sub = nh.subscribe ("/voxel_grid/output", 1, cloud_cb);   //run cloud_cb() function everytime a new pointcloud data is fed in
  pubPointCloud2 = nh.advertise<sensor_msgs::PointCloud2> ("/output", 1);
  pubTwist = nh.advertise<geometry_msgs::Twist>("/husky_velocity_controller/cmd_vel", 1000);
  // Spin
  ros::spin ();
}