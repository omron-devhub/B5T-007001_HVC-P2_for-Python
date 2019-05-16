----------------------------------------------------
 B5T-007001 サンプルコード（Python版）
----------------------------------------------------

(1) サンプルコード内容
  本サンプルはB5T-007001(HVC-P2)のPython APIクラスとそのクラスを用いた2種類のサンプルコードを提供します。
  サンプルコードは「検出処理」、「顔認証用アルバム操作」の2種類のサンプルコードを用意しています。
  
  「検出処理」ではB5T-007001の顔認証を含む全10機能を実行し、その結果を標準出力に出力します。
  また、本サンプルは「安定化ライブラリ(STB library)」を使用することができ
  複数フレーム結果を用いた検出結果の安定化と、顔と人体のトラキングが可能です。
  
  「顔認証用アルバム操作」では顔認証データをB5T-007001上のアルバムに登録、削除を実行することができます。 
  また、B5T-007001上のアルバムをPCなどのホスト装置にファイルとして保存することができます。
  保存されたアルバムファイルはB5T-007001に読み込むことも可能です。

(2) ファイル説明
  1. ユーザ使用用途
    execution.py                  サンプルコードメイン（検出処理）
    registration.py               サンプルコードメイン（顔認証用アルバム操作）
    p2def.py                      定義値ファイル
    connector.py                  Connectorクラス（親クラス）
    serial_connector.py           SerialConnectorクラス（Connectorのサブクラス）
    hvc_p2_api.py                 B5T-001007 Python APIクラス（結果安定化後）
    hvc_tracking_result.py        コマンド実行結果格納クラス(結果安定化後)
    okao_result.py                コマンド実行結果格納クラス(共通）
    grayscale_image.py            出力画像格納クラス
  2. 内部クラスなど
    hvc_p2_wrapper.py             B5T-007001 コマンドラッパクラス
    hvc_result.py                 コマンド実行結果格納クラス（結果安定化なし）
    hvc_result_c.py               "hvc_result"のC言語Pythonラッパクラス（STBの入力として使用）
    hvc_tracking_result_c.py      "hvc_tracking_result"のC言語Pythonラッパクラス（STBの出力として使用）
    stb.py                        STB library pythonクラス
    libSTB.dll                    STB library (Windows用)
    libSTB.so                     STB library (Raspbian Jessie用)

(3) サンプルコードのビルド方法
  1. Pythonバージョン 2.7
  2. pySerial、Python Imaging Library(PIL)を事前にインストールしておく必要があります。

     Note: Python3には未対応

(4) サンプルコードの実行方法
  1. 検出処理

    Usage: execution.py <com_port> <baudrate> [use_stb]

      com_port：COMポート
      baudrate：ボーレート
      use_stb：STB libraryの使用/不使用、デフォルトON、省略可
                   
      例）Windows用
          execution.py COM3 9600 OFF

      例）Raspbian Jessie用
          execution.py /dev/ttyACM0 921600 ON

  2. 顔認証用アルバム操作

    Usage: registration.py <com_port> <baudrate> 
      
(5) プログラミングガイド
  1. 主なクラスの説明
  
    クラス名              説明
    -------------------------------------------------------
    SerialConnector       シリアルコネクタクラス
    HVCP2Api              HVC-P2 API クラス（STB library使用可）
    HVCTrackingResult     検出結果格納クラス
    GrayscaleImage        グレースケール画像格納クラス

      ※詳細なクラス図は同梱の「HVC-P2_class.png」をご参照下さい。

  2. メイン処理フロー

  [検出処理]

    """ クラスの生成 """
    connector = serial_connector.SerialConnector()
    hvc_p2    = hvc_p2_api.HVCP2Api(connector, EX_FACE|EX_AGE, USE_STB_ON)
    hvc_res   = hvc_tracking_result.HVCTrackingResult()
    img       = grayscale_image.GrayscaleImage()

    """ デバイスへの接続 """
    hvc_p2.connect("COM3", 9600, 10)

    """ HVC-P2用パラメータ設定 """
    hvc_p2.set_camera_angle(HVC_CAM_ANGLE_0)
    hvc_p2.set_threshold(500, 500, 500, 500)
    hvc_p2.set_detection_size(30, 8192, 40, 8192, 64, 8192)
    hvc_p2.set_face_angle(HVC_FACE_ANGLE_YAW_30, HVC_FACE_ANGLE_ROLL_15)

    """ STB library用パラメータ設定 """
    hvc_p2.set_stb_tr_retry_count(2)
    hvc_p2.set_stb_tr_steadiness_param(30, 30)

    hvc_p2.set_stb_pe_threshold_use(300)
    hvc_p2.set_stb_pe_angle(-15, 20, -30, 30)
    hvc_p2.set_stb_pe_complete_frame_cunt(5)

    hvc_p2.set_stb_fr_threshold_use(300)
    hvc_p2.set_stb_fr_angle(-15, 20, -30, 30)
    hvc_p2.set_stb_fr_complete_frame_cunt(5)
    hvc_p2.set_stb_fr_min_ratio(60)

    """ 実行 """
    (response_code, stb_status) = hvc_p2_api.execute(OUT_IMG_TYPE_QVGA, hvc_tracking_result, img)

    """ 検出結果の取得 """
    for f in hvc_tracking_result.faces:
        pos_x = f.pos_x
        pos_y = f.pos_y
        size = f.size
        conf = f.conf
        if f.age is not None:
            age = f.age.age
            conf = f.age.conf
            tr_status = f.age.tracking_status

    """ 画像保存 """
    img.save('img.jpg')

    """ デバイスとの切断 """
    hvc_p2.disconnect()


   [顔認証]

    """ クラスの生成 """
    connector = serial_connector.SerialConnector()
    hvc_p2    = hvc_p2_api.HVCP2Api(connector, EX_FACE|EX_RECOGNITION, USE_STB_ON)
    hvc_res   = hvc_tracking_result.HVCTrackingResult()
    reg_img   = grayscale_image.GrayscaleImage()
    img       = grayscale_image.GrayscaleImage()

    """ デバイスへの接続 """
    hvc_p2.connect("COM3", 9600, 30)

    """ 顔登録 """
    user_id = 0
    data_id = 0
    response_code = hvc_p2_api.register_data(user_id, data_id, reg_img)

    """ 登録画像の保存 """
    reg_img.save('reg_img.jpg')
    
    """ 実行 """
    (response_code, stb_status) = hvc_p2_api.execute(OUT_IMG_TYPE_NONE, hvc_tracking_result, img)

    """ 顔認証結果の取得 """
    for f in hvc_tracking_result.faces:
        pos_x = f.pos_x
        pos_y = f.pos_y
        size = f.size
        conf = f.conf
        if f.registration is not None:
            user_id = f.registration.uid 
            score = f.registration.score
            tr_status = f.registration.tracking_status

    """ デバイスとの切断 """
    hvc_p2.disconnect()

[ご使用にあたって]
・本サンプルコードおよびドキュメントの著作権はオムロンに帰属します。
・本サンプルコードは動作を保証するものではありません。
・本サンプルコードは、Apache License 2.0にて提供しています。

----
オムロン株式会社
Copyright 2017-2018 OMRON Corporation, All Rights Reserved.
