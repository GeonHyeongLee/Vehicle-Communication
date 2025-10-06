import socket
import tkinter as tk
from tkinter import scrolledtext

# 라즈베리파이의 실제 IP 주소를 입력합니다.
RPI_HOST = '192.168.137.37' 
DOIP_PORT = 13400

# --- DoIP 헬퍼 함수 ---
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

# --- 최종 수정된 DTC 포맷 변환 함수 ---
def format_dtc(dtc_bytes):
    """3바이트 DTC를 UDS 표준 5자리 문자열로 올바르게 변환하는 함수"""
    if len(dtc_bytes) != 3:
        return "Invalid DTC format"
        
    first_byte = dtc_bytes[0]
    
    # 1. 첫 알파벳 결정
    dtc_type_map = {0b00: 'P', 0b01: 'C', 0b10: 'B', 0b11: 'U'}
    first_char = dtc_type_map.get(first_byte >> 6, '?')
    
    # 2. 두 번째 숫자 결정
    second_char = (first_byte >> 4) & 0x03
    
    # 3. 나머지 세 숫자 결정 (16진수 문자열로 조합)
    #    (이전 코드의 버그를 수정한 부분)
    last_three_chars = f"{(first_byte & 0x0F):X}{dtc_bytes[1]:02X}{dtc_bytes[2]:02X}"

    # 최종 조합
    return f"{first_char}{second_char}{last_three_chars}"
# --- 수정 끝 ---


def request_sensor_data():
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
                        dtc_code_bytes = dtc_chunk[0:3]
                        dtc_status = dtc_chunk[3]
                        formatted_dtc = format_dtc(dtc_code_bytes)
                        dtc_list.append(f"  - {formatted_dtc} (상태: 0x{dtc_status:02X})")
                
                update_result_text("[+] 감지된 고장 코드:\n" + "\n".join(dtc_list))
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

# --- GUI 생성 ---
window = tk.Tk()
window.title("ECU 진단 툴")
window.geometry("400x200")

button_frame = tk.Frame(window)
button_frame.pack(pady=10)

sensor_button = tk.Button(button_frame, text="레이저 센서 값 읽기 (DID 0x1000)", command=request_sensor_data)
sensor_button.pack(side=tk.LEFT, padx=5)

dtc_button = tk.Button(button_frame, text="DTC 정보 읽기 (SID 0x19)", command=request_dtc_data)
dtc_button.pack(side=tk.LEFT, padx=5)

result_text = scrolledtext.ScrolledText(window, height=5, font=("Helvetica", 12))
result_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
result_text.insert(tk.END, "버튼을 눌러 진단을 시작하세요.")
result_text.config(state=tk.DISABLED)

window.mainloop()