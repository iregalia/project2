#include "stdio.h"
#include "opencv2/opencv.hpp"

using namespace cv;

int main(int, char**)
{
	printf("Running.\n");
	VideoCapture cap(0); // open the default camera
	if(!cap.isOpened()) // check if we succeeded
	{
		printf("Cam Fail\n");
		return -1;
	}

	printf("Camera Started\n");

	cap.set(CV_CAP_PROP_FRAME_WIDTH, 384);
	cap.set(CV_CAP_PROP_FRAME_HEIGHT, 288);

//	Mat edges;
//	namedWindow("edges", 1);
	namedWindow("frame", 1);

	for(;;)
	{
		Mat frame;
		cap >> frame; // get new frame from camera
//		cvtColor(frame, edges, CV_BGR2GRAY);
//		GaussianBlur(edges,edges, Size(7,7), 1.5, 1.5);
//		Canny(edges, edges, 0, 30, 3);
//		imshow("edges", edges);
		imshow("frame", frame);
		if(waitKey(50) >= 0) break;
	}

	return 0;
}
