import socket
import tkinter as tk
from tkinter import scrolledtext, font as tkFont

import threading # ✨ 스레딩 라이브러리 추가
import time


# 라즈베리파이의 실제 IP 주소를 입력합니다.
RPI_HOST = '192.168.137.27' 
DOIP_PORT = 13400

# --- ✨ 세션 상태 관리를 위한 전역 변수 ---
g_extended_session_active = False
g_last_comm_time = 0.0

# --- ✨ Tester Present 백그라운드 스레드 함수 ---
def tester_present_thread():
    """백그라운드에서 주기적으로 Tester Present를 보내는 스레드"""
    global g_last_comm_time
    while True:
        # Extended 세션이 활성화되었을 때만 동작합니다.
        if g_extended_session_active:
            # 마지막 통신 후 2초가 지났는지 확인합니다.
            if (time.time() - g_last_comm_time) > 2.0:
                try:
                    # 0x3E 0x80 (suppressPosRspMsgIndicationBit)은 응답을 보내지 말라는 요청입니다.
                    # ECU의 S3 타이머 리셋 목적이므로 응답을 기다릴 필요가 없습니다.
                    uds_request = bytes([0x3E, 0x80]) 
                    print("[Keep-Alive] Tester Present 전송...")
                    
                    doip_request_packet = wrap_in_doip(uds_request)
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(2)
                        s.connect((RPI_HOST, DOIP_PORT))
                        s.sendall(doip_request_packet)
                    
                    g_last_comm_time = time.time() # 전송 시간 갱신
                except Exception as e:
                    print(f"[Keep-Alive] 에러: {e}")
        time.sleep(1) # 1초마다 상태를 확인합니다.

def poll_session_status_thread():
    """백그라운드에서 주기적으로 현재 세션 상태(DID 0xF186)를 요청하고 GUI를 업데이트하는 스레드"""
    global g_current_session_code
    session_map = {1: "Default", 3: "Extended", 2: "Programming"}
    while True:
        try:
            uds_request = bytes([0x22, 0xF1, 0x86])
            # 이 통신은 Keep-Alive 타이머에 영향을 주지 않도록 update_time=False 사용
            uds_response = send_and_receive_doip(uds_request, update_time=False)
            
            if uds_response and uds_response[0] == 0x62:
                session_code = uds_response[3]
                session_name = session_map.get(session_code, f"Unknown (0x{session_code:02X})")
                session_status_label.config(text=f"현재 세션: {session_name}")

                # --- ✨ 추가된 부분: 세션 변경 감지 및 결과창 업데이트 ---
                # 이전 세션과 현재 세션이 다른지 확인
                if g_current_session_code != session_code:
                    # Extended(3)에서 Default(1)로 변경되었다면, 타임아웃으로 간주
                    if g_current_session_code == 3 and session_code == 1:
                        update_result_text("[+] Default 세션으로 복귀 (타임아웃)")
                    
                    # 현재 세션 상태를 전역 변수에 업데이트
                    g_current_session_code = session_code
                # --- ✨ 추가 끝 ---

            else:
                session_status_label.config(text="현재 세션: 확인 불가")
        except Exception:
            session_status_label.config(text="현재 세션: 연결 끊김")
        
        time.sleep(3)

# DID 번호와 한글 설명 매핑해 둡니다.
DID_DESCRIPTIONS = {
    0x1000: "레이저 센서 거리",
    0x1001: "초음파(좌) 센서 거리",
    0x1004: "초음파(우) 센서 거리",
    0x1005: "초음파(후) 센서 거리",
    0xF187: "ECU 부품 번호",
    0xF18C: "ECU 시리얼 번호",
    0xF190: "차대번호 (VIN)",
    0xF192: "ECU 공급업체 정보",
    0xF193: "ECU 제조 날짜",
    0xF1A0: "지원 DID 목록",
    0xF186: "현재 세션 정보"
}

# --- DoIP 헬퍼 함수 (변경 없음) ---
def wrap_in_doip(uds_payload):
    protocol_version = 0x02
    payload_type = 0x8001
    payload_length = len(uds_payload)
    doip_header = bytearray([protocol_version, protocol_version ^ 0xFF])
    doip_header.extend(payload_type.to_bytes(2, 'big'))
    doip_header.extend(payload_length.to_bytes(4, 'big'))
    return bytes(doip_header) + uds_payload

def unwrap_doip(doip_packet):
    if len(doip_packet) < 8 or doip_packet[0] != 0x02:
        raise ValueError("Invalid DoIP packet")
    payload_length = int.from_bytes(doip_packet[4:8], 'big')
    uds_message = doip_packet[8:]
    if len(uds_message) != payload_length:
        raise ValueError("DoIP payload length mismatch")
    return uds_message

def format_dtc(dtc_bytes):
    if len(dtc_bytes) != 3: return "Invalid DTC format"
    first_byte = dtc_bytes[0]
    dtc_type_map = {0b00: 'P', 0b01: 'C', 0b10: 'B', 0b11: 'U'}
    first_char = dtc_type_map.get(first_byte >> 6, '?')
    second_char = (first_byte >> 4) & 0x03
    last_three_chars = f"{(first_byte & 0x0F):X}{dtc_bytes[1]:02X}{dtc_bytes[2]:02X}"
    return f"{first_char}{second_char}{last_three_chars}"


def send_and_receive_doip(uds_payload):
    """DoIP 통신을 수행하고, 마지막 통신 시간을 기록하는 공통 함수"""
    global g_last_comm_time
    # 사용자가 버튼을 눌러 통신을 시작하면 마지막 통신 시간을 갱신합니다.
    g_last_comm_time = time.time() 
    
    doip_request_packet = wrap_in_doip(uds_payload)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((RPI_HOST, DOIP_PORT))
        s.sendall(doip_request_packet)
        doip_response_packet = s.recv(1024)
        return unwrap_doip(doip_response_packet)
    
    

# --- 기능 함수들 ---
def request_part_number():
    """ECU 부품 번호(DID 0xF187) 요청 함수"""
    uds_request = bytes([0x22, 0xF1, 0x87])
    update_result_text(f"[*] DID 0xF187 (부품 번호) 요청 전송 중...")
    try:
        uds_response = send_and_receive_doip(uds_request)
        if uds_response and uds_response[0] == 0x62:
            # ECU가 보낸 데이터는 문자열(ASCII)이므로 디코딩합니다.
            part_number = uds_response[3:].decode('utf-8', errors='ignore')
            update_result_text(f"[+] ECU 부품 번호: {part_number}")
        else:
            update_result_text(f"[-] ECU 부정 응답: {uds_response.hex().upper()}")
    except Exception as e:
        update_result_text(f"[!] 에러: {e}")

def request_serial_number():
    """ECU 시리얼 번호(DID 0xF18C) 요청 함수"""
    uds_request = bytes([0x22, 0xF1, 0x8C])
    update_result_text(f"[*] DID 0xF18C (시리얼 번호) 요청 전송 중...")
    try:
        uds_response = send_and_receive_doip(uds_request)
        if uds_response and uds_response[0] == 0x62:
            # ECU가 보낸 데이터는 문자열(ASCII)이므로 디코딩합니다.
            serial_number = uds_response[3:].decode('utf-8', errors='ignore')
            update_result_text(f"[+] ECU 시리얼 번호: {serial_number}")
        else:
            update_result_text(f"[-] ECU 부정 응답: {uds_response.hex().upper()}")
    except Exception as e:
        update_result_text(f"[!] 에러: {e}")

def request_vin():
    """차대번호(VIN) 요청 함수"""
    uds_request = bytes([0x22, 0xF1, 0x90]);
    update_result_text(f"[*] DID 0xF190 (차대번호) 요청 전송 중...")
    try:
        uds_response = send_and_receive_doip(uds_request)
        if uds_response and uds_response[0] == 0x62:
            vin_number = uds_response[3:].decode('utf-8', errors='ignore')
            update_result_text(f"[+] 차대번호(VIN) : {vin_number}")
        else:
            update_result_text(f"[-] ECU 부정 응답: {uds_response.hex().upper()}")
    except Exception as e:
        update_result_text(f"[!] 에러: {e}")

def request_manufacturingDate():
    """ECU 제조 날짜 요청 함수"""
    uds_request = bytes([0x22, 0xF1, 0x92]);
    update_result_text(f"[*] DID 0xF192 (ECU 제조 날짜) 요청 전송 중...")
    try:
        uds_response = send_and_receive_doip(uds_request)
        if uds_response and uds_response[0] == 0x62:
            manufacturingDate = uds_response[3:].decode('utf-8', errors='ignore')
            update_result_text(f"[+] ECU 제조 날짜 : {manufacturingDate}")
        else:
            update_result_text(f"[-] ECU 부정 응답: {uds_response.hex().upper()}")
    except Exception as e:
        update_result_text(f"[!] 에러: {e}")

def request_supplier():
    """ECU 공급 업체 정보 요청 함수"""
    uds_request = bytes([0x22, 0xF1, 0x93]);
    update_result_text(f"[*] DID 0xF193 (ECU 공급 업체 정보) 요청 전송 중...")
    try:
        uds_response = send_and_receive_doip(uds_request)
        if uds_response and uds_response[0] == 0x62:
            supplier = uds_response[3:].decode('utf-8', errors='ignore')
            update_result_text(f"[+] ECU 공급 업체 정보 : {supplier}")
        else:
            update_result_text(f"[-] ECU 부정 응답: {uds_response.hex().upper()}")
    except Exception as e:
        update_result_text(f"[!] 에러: {e}")

def request_supported_dids():
    """지원 DID 목록(DID 0xF1A0) 요청 함수"""
    uds_request = bytes([0x22, 0xF1, 0xA0])
    update_result_text(f"[*] DID 0xF1A0 (지원 DID 목록) 요청 전송 중...")
    try:
        uds_response = send_and_receive_doip(uds_request)
        if uds_response and uds_response[0] == 0x62:
            did_data = uds_response[3:]
            did_list = []
            
            # 2바이트씩 잘라서 DID 목록을 재구성합니다.
            for i in range(0, len(did_data), 2):
                did_chunk = did_data[i:i+2]
                if len(did_chunk) == 2:
                    did_value = int.from_bytes(did_chunk, 'big')
                    description = DID_DESCRIPTIONS.get(did_value, "알 수 없는 DID")
                    did_list.append(f"  - 0x{did_value:04X}: {description}")
                    
            
            update_result_text("[+] ECU가 지원하는 DID 목록:\n" + "\n".join(did_list))
        else:
            update_result_text(f"[-] ECU 부정 응답: {uds_response.hex().upper()}")
    except Exception as e:
        update_result_text(f"[!] 에러: {e}")

def request_laser_sensor_data():
    """레이저 센서 데이터 요청 함수"""
    uds_request = bytes([0x22, 0x10, 0x00])
    update_result_text(f"[*] DID 0x1000 요청 전송 중...")
    try:
        uds_response = send_and_receive_doip(uds_request)
        if uds_response and uds_response[0] == 0x62:
            sensor_value = int.from_bytes(uds_response[3:], 'big')
            update_result_text(f"[+] 레이저 센서 값: {sensor_value} mm")
        else:
            update_result_text(f"[-] ECU 부정 응답: {uds_response.hex().upper()}")
    except Exception as e:
        update_result_text(f"[!] 에러: {e}")

def request_left_ultrasonic_data():
    """좌측 초음파 센서 데이터 요청 함수"""
    uds_request = bytes([0x22, 0x10, 0x01]) # DID 0x1001 요청
    update_result_text(f"[*] DID 0x1001 요청 전송 중...")
    try:
        uds_response = send_and_receive_doip(uds_request)
        if uds_response and uds_response[0] == 0x62:
            # 1. ECU로부터 '스케일링된 값'(cm * 10)을 정수로 받습니다.
            scaled_value = int.from_bytes(uds_response[3:], 'big')
            
            # 2. 10.0으로 다시 나누어 실제 cm 값으로 복원합니다.
            distance_cm = scaled_value / 10.0
            
            update_result_text(f"[+] 좌측 초음파 센서 값: {distance_cm:.1f} cm")
        elif uds_response and uds_response[0] == 0x7F: # 부정 응답 처리
            update_result_text(f"[-] ECU 부정 응답: {uds_response.hex().upper()} (센서 측정 실패)")
        else:
            update_result_text(f"[-] ECU 응답 형식 오류: {uds_response.hex().upper()}")
    except Exception as e:
        update_result_text(f"[!] 에러: {e}")

def request_dtc_data():
    """DTC 정보 요청 함수"""
    uds_request = bytes([0x19, 0x02, 0xFF])
    update_result_text(f"[*] DTC 정보 요청 전송 중...")
    try:
        uds_response = send_and_receive_doip(uds_request)
        if uds_response and uds_response[0] == 0x59:
            dtc_data = uds_response[3:]
            if not dtc_data:
                update_result_text("[+] 고장 코드가 없습니다.")
            else:
                dtc_list = []
                for i in range(0, len(dtc_data), 4):
                    dtc_chunk = dtc_data[i:i+4]
                    if len(dtc_chunk) == 4:
                        dtc_code_bytes, dtc_status = dtc_chunk[0:3], dtc_chunk[3]
                        formatted_dtc = format_dtc(dtc_code_bytes)
                        dtc_list.append(f"  - {formatted_dtc} (상태: 0x{dtc_status:02X})")
                update_result_text("[+] 감지된 고장 코드:\n" + "\n".join(dtc_list))
        else:
            update_result_text(f"[-] ECU 부정 응답: {uds_response.hex().upper()}")
    except Exception as e:
        update_result_text(f"[!] 에러: {e}")

def write_aeb_flag(is_on: bool):
    """AEB 기능 플래그를 ON/OFF 하는 SID 0x2E 요청을 보내는 함수"""
    new_data = 0x01 if is_on else 0x00
    uds_request = bytes([0x2E, 0x20, 0x00, new_data])
    status_text = 'ON' if is_on else 'OFF'
    update_result_text(f"[*] AEB 기능 {status_text} 요청 전송 중...")
    try:
        uds_response = send_and_receive_doip(uds_request)
        if uds_response and uds_response[0] == 0x6E:
            update_result_text(f"[+] AEB 기능이 성공적으로 {status_text} 되었습니다.")
        else:
            update_result_text(f"[-] ECU 부정 응답: {uds_response.hex().upper()}")
    except Exception as e:
        update_result_text(f"[!] 에러: {e}")


# --- 공통 기능 함수 ---


def send_and_receive_doip(uds_payload, update_time = True):
    """DoIP 통신을 수행하고, 마지막 통신 시간을 기록하는 공통 함수"""
    global g_last_comm_time
    if update_time:
        g_last_come_time = time.time()
        
    doip_request_packet = wrap_in_doip(uds_payload)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((RPI_HOST, DOIP_PORT))
        s.sendall(doip_request_packet)
        doip_response_packet = s.recv(1024)
        return unwrap_doip(doip_response_packet)
    

def update_result_text(text):
    """결과 텍스트 창을 업데이트하는 함수"""
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, text)
    result_text.config(state=tk.DISABLED)

# --- 각 버튼에 연결될 기능 함수들 ---
def control_session(session_type: int):
    """세션 변경(SID 0x10)을 요청하는 함수"""
    global g_extended_session_active, g_current_session_code
    uds_request = bytes([0x10, session_type])
    session_name = "Extended" if session_type == 0x03 else "Default"
    update_result_text(f"[*] {session_name} 세션 요청 전송 중...")
    try:
        uds_response = send_and_receive_doip(uds_request)
        if uds_response and uds_response[0] == 0x50:
            update_result_text(f"[+] {session_name} 세션으로 성공적으로 전환되었습니다.")
            g_extended_session_active = (session_type == 0x03)
            # --- ✨ 추가된 부분: 사용자 요청 시에도 전역 세션 상태 업데이트 ---
            g_current_session_code = session_type
        else:
            g_extended_session_active = False
            update_result_text(f"[-] 세션 전환 실패: {uds_response.hex().upper()}")
    except Exception as e:
        g_extended_session_active = False
        update_result_text(f"[!] 에러: {e}")

# --- ✨ GUI 생성 (레이아웃 수정된 부분) ---
window = tk.Tk()
window.title("ECU 진단 툴")
window.geometry("800x600")
window.configure(bg="#f0f0f0") # 배경색 설정

# 폰트 설정
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(family="Helvetica", size=10)

# --- 현재 세션 상태 표시할 라벨 추가 ---
session_status_label = tk.Label(window, text="현재 세션: 확인 중...", font=("Helvetica", 10, "italic"), bg="#f0f0f0", fg="blue")
session_status_label.pack(pady=(5, 0))


# --- 1. 센서 데이터 그룹 ---
sensor_frame = tk.LabelFrame(window, text=" 센서 데이터 ", padx=10, pady=10, bg="#f0f0f0")
sensor_frame.pack(pady=10, padx=10, fill="x")

laser_button = tk.Button(sensor_frame, text="레이저 센서", command=request_laser_sensor_data)
laser_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

ultrasonic_button = tk.Button(sensor_frame, text="좌측 초음파", command=request_left_ultrasonic_data)
ultrasonic_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# --- 2. ECU 정보 그룹 ---
info_frame = tk.LabelFrame(window, text=" ECU 정보 ", padx=10, pady=10, bg="#f0f0f0")
info_frame.pack(pady=5, padx=10, fill="x")

part_number_button = tk.Button(info_frame, text="부품 번호", command=request_part_number)
part_number_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

serial_number_button = tk.Button(info_frame, text="시리얼 번호", command=request_serial_number)
serial_number_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

vin_button = tk.Button(info_frame, text="차대번호 (VIN)", command=request_vin)
vin_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

mfg_date_button = tk.Button(info_frame, text="제조 날짜", command=request_manufacturingDate)
mfg_date_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

supplier_button = tk.Button(info_frame, text="공급업체", command=request_supplier)
supplier_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

supported_dids_button = tk.Button(info_frame, text="지원 DID 목록", command=request_supported_dids)
supported_dids_button.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

# --- 3. 진단 및 제어 그룹 ---
control_frame = tk.LabelFrame(window, text=" 진단 및 제어 ", padx=10, pady=10, bg="#f0f0f0")
control_frame.pack(pady=10, padx=10, fill="x")

dtc_button = tk.Button(control_frame, text="DTC 정보 읽기", command=request_dtc_data)
dtc_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

aeb_on_button = tk.Button(control_frame, text="AEB 기능 ON", command=lambda: write_aeb_flag(True))
aeb_on_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

aeb_off_button = tk.Button(control_frame, text="AEB 기능 OFF", command=lambda: write_aeb_flag(False))
aeb_off_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

# 세션 버튼을 새로운 행에 추가
session_extended_button = tk.Button(control_frame, text="세션 시작 (Extended)", command=lambda: control_session(0x03))
session_extended_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

session_default_button = tk.Button(control_frame, text="세션 종료 (Default)", command=lambda: control_session(0x01))
session_default_button.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

control_frame.grid_columnconfigure((0,1,2,3), weight=1)


# 프레임 내 컬럼 비율 설정 (버튼 크기 균등 분배)
sensor_frame.grid_columnconfigure((0, 1), weight=1)
info_frame.grid_columnconfigure((0, 1, 2), weight=1)
control_frame.grid_columnconfigure((0, 1, 2), weight=1)

# --- 결과 텍스트 창 ---
result_text = scrolledtext.ScrolledText(window, height=6, font=("Consolas", 14))
result_text.pack(pady=10, padx=10, fill="both", expand=True)
result_text.insert(tk.END, "버튼을 눌러 진단을 시작하세요.")
result_text.config(state=tk.DISABLED)

# --- ✨ 프로그램 시작 부분 수정 ---
if __name__ == "__main__":
    # Tester Present를 위한 백그라운드 스레드 생성 및 시작
    #tp_thread = threading.Thread(target=tester_present_thread, daemon=True)
    #tp_thread.start()

    session_poll_thread = threading.Thread(target=poll_session_status_thread, daemon=True)
    session_poll_thread.start()
    
    window.mainloop()
