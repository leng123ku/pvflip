CMAKE_MINIMUM_REQUIRED (VERSION 2.6) #specify the required version of cmake
PROJECT (IIO)                        #give a name to the project/solution

# ADD LOCAL PATH TO SEARCH MODULES
#LIST (APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_PREFIX}")
#SET (CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR})
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake")



# SETUP A MAKE CLEAN TO CLEAN EVERYTHING
#
#
SET_DIRECTORY_PROPERTIES (PROPERTIES ADDITIONAL_MAKE_CLEAN_FILES 
   "iioConfig.cmake;CMakeCache.txt;Makefile;cmake_install.cmake;iio.o;CMakeFiles")


# LIBRARIES
#
#

SET (LIBS "")

# IF AVAILABLE USE OPENEXR
FIND_PACKAGE(OPENEXR) 
# OPENEXR_FOUND = OpenEXR found. 
# OPENEXR_INCLUDE_PATHS = OpenEXR include directories.
# OPENEXR_LIBRARIES = libraries that are needed to use OpenEXR.
IF (OPENEXR_FOUND) 
   INCLUDE_DIRECTORIES(${OPENEXR_INCLUDE_PATHS})
   SET(C_FLAGS "${C_FLAGS} -DI_CAN_HAS_LIBEXR")
   SET(LIBS ${LIBS} ${OPENEXR_LIBRARIES})
ENDIF()

# IF AVAILABLE USE LIBRAW (needed for reading Photo RAW formats)
FIND_PACKAGE(LibRaw) 
# LibRaw_INCLUDE_DIR, where to find libraw.h
# LibRaw_LIBRARIES, the libraries needed to use LibRaw (non-thread-safe)
IF (LibRaw_INCLUDE_DIR) 
   SET(C_FLAGS "${C_FLAGS} -DI_USE_LIBRAW")
   INCLUDE_DIRECTORIES(${LibRaw_INCLUDE_DIR})
   SET(LIBS ${LIBS} ${LibRaw_LIBRARIES})
   SET(IIO_LIB_EXTRA_SRCS libraw_interface.cpp)    #c++ interface to libraw
   # Some LibRaw versions depend on openmp
   find_package (OpenMP)
   if(OPENMP_FOUND)
      set (C_FLAGS "${C_FLAGS} ${OpenMP_C_FLAGS}")
   endif()
ENDIF()

# OTHER LIBRARIES
FIND_PACKAGE(TIFF)
IF(TIFF_FOUND)
   INCLUDE_DIRECTORIES(${TIFF_INCLUDE_DIR})
   #  LINK_DIRECTORIES(${TIFF_LIBRARY})
   SET(LIBS ${LIBS} ${TIFF_LIBRARIES})
ENDIF()

FIND_PACKAGE(JPEG)
if(JPEG_FOUND)
   INCLUDE_DIRECTORIES(${JPEG_INCLUDE_DIR})
   # LINK_DIRECTORIES(${JPEG_LIBRARY})
   SET(LIBS ${LIBS} ${JPEG_LIBRARIES})
ENDIF()

FIND_PACKAGE(PNG)
IF(PNG_FOUND)
   INCLUDE_DIRECTORIES(${PNG_INCLUDE_DIR})
   #  LINK_DIRECTORIES(${PNG_LIBRARY})
   SET(LIBS ${LIBS} ${PNG_LIBRARIES})
ENDIF()


# DETECT LINUX
#
#
IF(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
   # Linux specific code flags
   SET(C_FLAGS "${C_FLAGS} -DI_CAN_HAS_LINUX -D_GNU_SOURCE")
ENDIF()


# IIO
#
#
SET(C_FLAGS "${C_FLAGS} -O3 -std=c99 -funroll-loops -Wno-unused -DNDEBUG")
MESSAGE( "FLAGS: ${C_FLAGS}")
SET(IIO_LIB_SRCS iio.h iio.c freemem.c ${IIO_LIB_EXTRA_SRCS})       #Define a variable that contains files of the lib
ADD_LIBRARY(IIOLIB ${IIO_LIB_SRCS}) #Define that those files create the lib FooLib
TARGET_LINK_LIBRARIES(IIOLIB ${LIBS})
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${C_FLAGS}" )


# generate custom iio.o
#
#
set(inc_list "")
get_property(inc_dirs DIRECTORY PROPERTY INCLUDE_DIRECTORIES) 
foreach(next_ITEM ${inc_dirs})
      set(inc_list  ${inc_list}  -I${next_ITEM})
endforeach(next_ITEM ${inc_dirs})


#HORRIBLE HACK TO CONCATENATE THE PARAMETERS
STRING(REGEX REPLACE " "  ";" FLGS "${C_FLAGS}")
foreach(next_ITEM ${FLGS})
      set(inc_list  ${inc_list}  ${next_ITEM})
endforeach(next_ITEM ${FLGS})

message("${inc_list}") 


#ADD_CUSTOM_COMMAND(
#   OUTPUT generate_iio.o 
#   COMMAND ${CMAKE_C_COMPILER} ${inc_list} -c ${CMAKE_CURRENT_SOURCE_DIR}/iio.c -o ${CMAKE_CURRENT_BINARY_DIR}/iio.o
#   DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/iio.c ${CMAKE_CURRENT_SOURCE_DIR}/iio.h
#   COMMENT "Generating iio.o"
#   )
#ADD_CUSTOM_TARGET(iio.o ALL DEPENDS generate_iio.o)


# EXAMPLE
#
#
#ADD_EXECUTABLE (iio iio_test.c)
#TARGET_LINK_LIBRARIES(iio IIOLIB )
#SET_TARGET_PROPERTIES(iio PROPERTIES COMPILE_FLAGS "${C_FLAGS}")

#ADD_EXECUTABLE (iion ../misc/iio_test_named.c iio.h iio.c)
#TARGET_LINK_LIBRARIES(iion IIOLIB m)
#SET_TARGET_PROPERTIES(iion PROPERTIES COMPILE_FLAGS "${C_FLAGS} -I${PROJECT_SOURCE_DIR}")

set(CMAKE_MACOSX_RPATH 1)
ADD_LIBRARY(iio SHARED ${IIO_LIB_SRCS})
set_target_properties(iio PROPERTIES SUFFIX ".so")
TARGET_LINK_LIBRARIES(iio IIOLIB m)

##setup Config.cmake
#
#
SET(PARAMETROS_BASE_DIR "${PROJECT_SOURCE_DIR}")
SET(PARAMETROS_CMAKE_DIR "${PROJECT_BINARY_DIR}")
SET(IIO_LIBS ${PROJECT_SOURCE_DIR}/libIIOLIB.a ${LIBS})
SET(IIO_INCLUDE ${PROJECT_SOURCE_DIR})
MESSAGE( "${PROJECT_BINARY_DIR}" )
MESSAGE( "${PROJECT_SOURCE_DIR}" )
CONFIGURE_FILE(iioConfig.cmake.in
   "${PROJECT_BINARY_DIR}/iioConfig.cmake" @ONLY)

