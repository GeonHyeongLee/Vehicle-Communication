import socket
import tkinter as tk
from tkinter import scrolledtext, font as tkFont

# 라즈베리파이의 실제 IP 주소를 입력합니다.
RPI_HOST = '192.168.137.27' 
DOIP_PORT = 13400

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
    0xF1A0: "지원 DID 목록"
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

def send_and_receive_doip(uds_payload):
    """DoIP 통신을 수행하는 공통 함수"""
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

# --- ✨ GUI 생성 (레이아웃 수정된 부분) ---
window = tk.Tk()
window.title("ECU 진단 툴")
window.geometry("800x600")
window.configure(bg="#f0f0f0") # 배경색 설정

# 폰트 설정
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(family="Helvetica", size=10)

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

# 프레임 내 컬럼 비율 설정 (버튼 크기 균등 분배)
sensor_frame.grid_columnconfigure((0, 1), weight=1)
info_frame.grid_columnconfigure((0, 1, 2), weight=1)
control_frame.grid_columnconfigure((0, 1, 2), weight=1)

# --- 결과 텍스트 창 ---
result_text = scrolledtext.ScrolledText(window, height=6, font=("Consolas", 14))
result_text.pack(pady=10, padx=10, fill="both", expand=True)
result_text.insert(tk.END, "버튼을 눌러 진단을 시작하세요.")
result_text.config(state=tk.DISABLED)

window.mainloop()