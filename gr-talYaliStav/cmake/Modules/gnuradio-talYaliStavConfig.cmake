find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_TALYALISTAV gnuradio-talYaliStav)

FIND_PATH(
    GR_TALYALISTAV_INCLUDE_DIRS
    NAMES gnuradio/talYaliStav/api.h
    HINTS $ENV{TALYALISTAV_DIR}/include
        ${PC_TALYALISTAV_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_TALYALISTAV_LIBRARIES
    NAMES gnuradio-talYaliStav
    HINTS $ENV{TALYALISTAV_DIR}/lib
        ${PC_TALYALISTAV_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-talYaliStavTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_TALYALISTAV DEFAULT_MSG GR_TALYALISTAV_LIBRARIES GR_TALYALISTAV_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_TALYALISTAV_LIBRARIES GR_TALYALISTAV_INCLUDE_DIRS)
