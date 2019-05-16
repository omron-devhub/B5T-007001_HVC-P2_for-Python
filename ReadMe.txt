----------------------------------------------------
 B5T-007001 Sample Code （for Python）
----------------------------------------------------

(1) Contents
  This code provides B5T-007001(HVC-P2) python API class and sample code using that API class.
  The sample code is for "Detection process" and "Album operation for face recognition".
  
  The "Detection process" can execute any functions in all 10 functions of B5T-007001,
  and outputs the result in standard output.
  And this sample is avalable to use STB library which stabilizes the detected results by multiple frames
  and tracks detected faces ande bodies.

  The "Album operation" can execute registration and deletion of face recognition data of B5T-007001.
  And this sample can save the album on the B5T-007001 to your host(PC etc.) as a file,
  and can load the album from your host.

(2) File description
  1. for user use.
    execution.py                  Sample code main (Detection Process)
    registration.py               Sample code main (Album operation)
    p2def.py                      Definitions
    connector.py                  Connector parent class
    serial_connector.py           Serial connector class（Connector sub-class）
    hvc_p2_api.py                 B5T-001007 Python API class with STB library
    hvc_tracking_result.py        Class storing command execution result(with STB library)
    okao_result.py                Class storing command execution result(common)
    grayscale_image.py            Class storing output image
  2. inner class.
    hvc_p2_wrapper.py             B5T-007001 command wrapper class
    hvc_result.py                 Class storing command execution result
    hvc_result_c.py               Python wrapper class for C language of "hvc_result" used for STB input
    hvc_tracking_result_c.py      Python wrapper class for C language of "hvc_tracking_result" used for STB output
    stb.py                        STB library python class
    libSTB.dll                    STB library (for Windows)
    libSTB.so                     STB library (for Raspbian Jessie)

(3) Method for building code
   1. Use Python 2.7 (required)
   2. Install pySerial and Python Imaging Library(PIL)  (required)

     Note: Python3 is NOT supported.

(4) Usage of sample code
  [Detection process]
  
    Usage: execution.py <com_port> <baudrate> [use_stb=ON]
        com_port:  COM port
        baudreate: baudrate
        use_stb:   Using flag for STB Library (optional)
    
    1. Example: for Windows
         execution.py COM3 9600 OFF

    2. Example: for Raspbian Jessie
          execution.py /dev/ttyACM0 921600 ON

  [Album operation]
  
    Usage: registration.py <com_port> <baudrate> 


(5) Programing guidance
  1. Description of main classes
  
    Class name            Description
    -------------------------------------------------------
    SerialConnector       Serial connector class
    HVCP2Api              HVC-P2 API class with STB library
    HVCTrackingResult     Class storing detection results
    GrayscaleImage        Calss stroing gray scale image

      Refer to the class diagram in HVC-P2_class.png for detail.    

  2. Main process flow
  
   [Detection process]

    """ Create class """
    connector = serial_connector.SerialConnector()
    hvc_p2    = hvc_p2_api.HVCP2Api(connector, EX_FACE|EX_AGE, USE_STB_ON)
    hvc_res   = hvc_tracking_result.HVCTrackingResult()
    img       = grayscale_image.GrayscaleImage()

    """ Connect to device via serial interface. """
    hvc_p2.connect("COM3", 9600, 10)

    """ Set HVC-P2 parameters """
    hvc_p2.set_camera_angle(HVC_CAM_ANGLE_0)
    hvc_p2.set_threshold(500, 500, 500, 500)
    hvc_p2.set_detection_size(30, 8192, 40, 8192, 64, 8192)
    hvc_p2.set_face_angle(HVC_FACE_ANGLE_YAW_30, HVC_FACE_ANGLE_ROLL_15)

    """ Set STB parameters """
    hvc_p2.set_stb_tr_retry_count(2)
    hvc_p2.set_stb_tr_steadiness_param(30, 30)
    hvc_p2.set_stb_pe_threshold_use(300)
    hvc_p2.set_stb_pe_angle(-15, 20, -30, 30)
    hvc_p2.set_stb_pe_complete_frame_cunt(5)
    hvc_p2.set_stb_fr_threshold_use(300)
    hvc_p2.set_stb_fr_angle(-15, 20, -30, 30)
    hvc_p2.set_stb_fr_complete_frame_cunt(5)
    hvc_p2.set_stb_fr_min_ratio(60)

    """ Execution """
    (response_code, stb_status) = hvc_p2_api.execute(OUT_IMG_TYPE_QVGA, hvc_tracking_result, img)

    """ Get detection result"""
    for f in hvc_tracking_result.faces:
        pos_x = f.pos_x
        pos_y = f.pos_y
        size = f.size
        conf = f.conf
        if f.age is not None:
            age = f.age.age
            conf = f.age.conf
            tr_status = f.age.tracking_status

    """ save image """
    img.save('img.jpg')

    """ Disconnect to device """
    hvc_p2.disconnect()


  [Album operation]
    """ Create class """
    connector = serial_connector.SerialConnector()
    hvc_p2    = hvc_p2_api.HVCP2Api(connector, EX_FACE|EX_RECOGNITION, USE_STB_ON)
    hvc_res   = hvc_tracking_result.HVCTrackingResult()
    reg_img   = grayscale_image.GrayscaleImage()
    img       = grayscale_image.GrayscaleImage()

    """ Connect to device via serial interface. """
    hvc_p2.connect("COM3", 9600, 10)

    """ Registration """
    user_id = 0
    data_id = 0
    response_code = hvc_p2_api.register_data(user_id, data_id, reg_img)

    """ save registered image """
    reg_img.save('reg_img.jpg')
    
    """ Execution """
    (response_code, stb_status) = hvc_p2_api.execute(OUT_IMG_TYPE_NONE, hvc_tracking_result, img)

    """ Get recognition result"""
    for f in hvc_tracking_result.faces:
        pos_x = f.pos_x
        pos_y = f.pos_y
        size = f.size
        conf = f.conf
        if f.registration is not None:
            user_id = f.registration.uid
            score = f.registration.score
            tr_status = f.registration.tracking_status

    """ Disconnect to device """
    hvc_p2.disconnect()


[NOTES ON USAGE]
* This sample code and documentation are copyrighted property of OMRON Corporation  
* This sample code does not guarantee proper operation
* This sample code is distributed in the Apache License 2.0.
----
OMRON Corporation 
Copyright 2017-2018 OMRON Corporation, All Rights Reserved.
