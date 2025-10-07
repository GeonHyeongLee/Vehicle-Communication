import socket
import tkinter as tk

# --- 수정된 부분 ---
# 스캔으로 확인된 라즈베리파이의 실제 IP 주소를 입력합니다.
RPI_HOST = '192.168.137.37'
# --- 수정된 부분 끝 ---
DOIP_PORT = 13400

# 
def wrap_in_doip(uds_payload):
    """UDS 메시지를 DoIP 헤더로 감싸는 함수"""
    protocol_version = 0x02
    payload_type = 0x8001  # UDS Diagnostic Message
    payload_length = len(uds_payload)

    doip_header = bytearray()
    doip_header.append(protocol_version)
    doip_header.append(protocol_version ^ 0xFF)
    doip_header.extend(payload_type.to_bytes(2, 'big'))
    doip_header.extend(payload_length.to_bytes(4, 'big'))
    
    return bytes(doip_header) + uds_payload

def unwrap_doip(doip_packet):
    """DoIP 패킷에서 UDS 메시지를 추출하는 함수"""
    if len(doip_packet) < 8 or doip_packet[0] != 0x02:
        raise ValueError("Invalid DoIP packet")
    
    payload_length = int.from_bytes(doip_packet[4:8], 'big')
    uds_message = doip_packet[8:]
    
    if len(uds_message) != payload_length:
        raise ValueError("DoIP payload length mismatch")
        
    return uds_message

def request_sensor_data():
    """버튼 클릭 시 실행될 함수"""
    uds_request = bytes([0x22, 0x10, 0x00]) # DID 0x1000 요청
    doip_request_packet = wrap_in_doip(uds_request)
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5) # 5초 연결 타임아웃
            s.connect((RPI_HOST, DOIP_PORT))
            s.sendall(doip_request_packet)
            doip_response_packet = s.recv(1024)
            
            uds_response = unwrap_doip(doip_response_packet)
            
            if uds_response[0] == 0x62: # 긍정 응답
                sensor_value = int.from_bytes(uds_response[3:], 'big')
                result_label.config(text=f"센서 값: {sensor_value} mm")
            else:
                result_label.config(text=f"ECU 부정 응답: {uds_response.hex().upper()}")

    except Exception as e:
        result_label.config(text=f"에러: {e}")

# --- GUI 생성 ---
window = tk.Tk()
window.title("ECU 진단 툴")
window.geometry("400x150")

request_button = tk.Button(window, text="레이저 센서 값 읽기 (DID 0x1000)", command=request_sensor_data, font=("Helvetica", 12))
request_button.pack(pady=20)

result_label = tk.Label(window, text="센서 값: N/A", font=("Helvetica", 16))
result_label.pack(pady=10)

window.mainloop()