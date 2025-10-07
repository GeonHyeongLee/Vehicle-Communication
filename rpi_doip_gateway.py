import socket
import can
import time

def main():
    # --- 1. CAN 버스 설정 ---
    can_bus = can.interface.Bus(channel='can0', interface='socketcan')
    print(">>> CAN 버스 초기화 성공")

    # --- 2. 이더넷 TCP 서버 설정 ---
    HOST = '0.0.0.0'  # 모든 IP에서 오는 요청을 받음
    PORT = 13400      # DoIP 표준 포트

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] DoIP 게이트웨이가 {PORT} 포트에서 PC의 연결을 기다립니다...")
        
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"\n[*] PC {addr} 에서 연결됨")
                
                # --- PC -> CAN 방향 ---
                doip_packet_from_pc = conn.recv(1024)
                if not doip_packet_from_pc:
                    continue
                
                print(f"[PC -> RPi] 받은 DoIP 패킷: {doip_packet_from_pc.hex().upper()}")
                
                # DoIP 헤더 제거하고 UDS 요청 추출
                uds_request_payload = doip_packet_from_pc[8:]
                
                # 추출한 UDS 요청을 CAN으로 전송 (SF)
                pci = len(uds_request_payload) # SF의 PCI는 데이터 길이와 같음
                can_data = [pci] + list(uds_request_payload)
                
                request_msg = can.Message(arbitration_id=0x7E0, data=can_data, is_extended_id=False)
                can_bus.send(request_msg)
                print(f"[RPi -> ECU] CAN으로 UDS 요청 전송: {request_msg.data.hex().upper()}")
                
                # --- CAN -> PC 방향 ---
                print("[*] ECU 응답 수신 대기...")
                # (이 부분은 manual_uds_tester.py의 수신 로직과 동일)
                # FF, FC, CF 과정을 거쳐 최종 UDS 응답 데이터를 조립합니다.
                
                # 여기서는 간단히 SF 응답만 처리하는 예시를 보여줍니다.
                # 실제로는 FF/CF 처리 로직이 필요합니다.
                uds_response_payload = None
                start_time = time.time()
                while time.time() - start_time < 2:
                    msg = can_bus.recv(timeout=0.1)
                    if msg and msg.arbitration_id == 0x7E8:
                        pci = msg.data[0]
                        if (pci & 0xF0) == 0x00: # SF 응답인 경우
                            sf_len = pci & 0x0F
                            uds_response_payload = msg.data[1:1+sf_len]
                            print(f"[ECU -> RPi] CAN으로 UDS 응답 수신: {uds_response_payload.hex().upper()}")
                            break
                
                if uds_response_payload:
                    # UDS 응답에 DoIP 헤더를 붙여 PC로 전송
                    protocol_version = 0x02
                    payload_type = 0x8001
                    payload_length = len(uds_response_payload)

                    doip_header = bytearray([protocol_version, protocol_version ^ 0xFF])
                    doip_header.extend(payload_type.to_bytes(2, 'big'))
                    doip_header.extend(payload_length.to_bytes(4, 'big'))
                    
                    doip_packet_to_pc = bytes(doip_header) + uds_response_payload
                    
                    conn.sendall(doip_packet_to_pc)
                    print(f"[RPi -> PC] DoIP로 응답 전송: {doip_packet_to_pc.hex().upper()}")
                else:
                    print("[-] ECU로부터 응답 수신 실패 (타임아웃)")

if __name__ == "__main__":
    main()