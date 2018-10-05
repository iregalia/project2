# Minimum CMake version required to generate
# our build system
cmake_minimum_required(VERSION 3.0)

# Name of our Project
project(PiCam)
find_package( OpenCV REQUIRED )
add_executable(PiCam PiCam.cpp)
target_link_libraries( PiCam ${OpenCV_LIBS} )
