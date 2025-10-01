import can
import time

def main():
    bus = None
    try:
        # 1. 버스 초기화 (이전과 동일)
        bus = can.interface.Bus(channel='can0', interface='socketcan')
        print(">>> 버스 초기화 성공")

        # 2. UDS 요청(SF) 직접 만들어 보내기
        #    - can-isotp 라이브러리 대신, 우리가 직접 PCI(0x03)를 포함한 CAN 메시지를 만듭니다.
        request_msg = can.Message(
            arbitration_id=0x7E0,
            data=[0x03, 0x22, 0x00, 0x01],
            is_extended_id=False
        )
        bus.send(request_msg)
        print(f"[*] 요청 전송 (ID: 0x7E0): {request_msg.data.hex().upper()}")
        
        # 3. ECU의 응답 수신 (FF -> FC -> CF 과정을 직접 처리)
        print("[*] ECU 응답 대기 중...")
        
        # 3-1. 첫 번째 응답(First Frame) 기다리기
        #      - ECU는 12바이트 응답의 첫 조각인 FF를 보내야 합니다 (ID: 0x7E8)
        first_frame = None
        start_time = time.time()
        while time.time() - start_time < 2: # 2초 타임아웃
            msg = bus.recv(timeout=0.1)
            if msg and msg.arbitration_id == 0x7E8:
                # PCI 타입이 FF(0x10)인지 확인
                if (msg.data[0] & 0xF0) == 0x10:
                    first_frame = msg
                    print(f"[<] 최초 프레임(FF) 수신: {first_frame.data.hex().upper()}")
                    break
        
        if not first_frame:
            print("[-] 응답을 받지 못했습니다. (타임아웃)")
            return

        # 3-2. FF를 분석하고, FC(Flow Control) 프레임 보내기
        #      - "나머지 데이터 전부 보내" 라는 의미의 FC를 전송합니다.
        total_size = ((first_frame.data[0] & 0x0F) << 8) + first_frame.data[1]
        
        flow_control_msg = can.Message(
            arbitration_id=0x7E0,
            data=[0x30, 0x00, 0x00], # [PCI: FC, CTS], [BlockSize=0], [STmin=0]
            is_extended_id=False
        )
        bus.send(flow_control_msg)
        print(f"[>] 흐름 제어(FC) 전송: {flow_control_msg.data.hex().upper()}")

        # 3-3. 나머지 데이터(Consecutive Frame) 모두 수신하기
        #      - FC를 받은 ECU는 남은 데이터를 CF에 담아 보냅니다.
        full_data = bytearray(first_frame.data[2:]) # FF에 있던 데이터로 시작
        
        while len(full_data) < total_size:
            msg = bus.recv(timeout=1) # 다음 프레임 기다리기
            if msg and msg.arbitration_id == 0x7E8:
                 # PCI 타입이 CF(0x20)인지 확인
                if (msg.data[0] & 0xF0) == 0x20:
                    print(f"[<] 연속 프레임(CF) 수신: {msg.data.hex().upper()}")
                    full_data.extend(msg.data[1:])
            else:
                print("[-] 연속 프레임 수신 중 타임아웃")
                return
        
        # 수신 완료된 전체 페이로드
        received_payload = bytes(full_data)
        
        # 4. 최종 데이터 검증 (이전과 동일)
        print(f"[*] 전체 응답 수신 성공! (길이: {len(received_payload)} 바이트)")
        print(f"    - 데이터: {received_payload.hex().upper()}")
        
        expected_payload = bytes([0x62, 0x00, 0x01, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0x11, 0x22, 0x33, 0x44])
        
        if received_payload == expected_payload:
            print("[+] 검증 성공: C 코드의 응답과 일치합니다!")
        else:
            print(f"[-] 검증 실패: 기대값과 다릅니다.")
            print(f"    - 기대값: {expected_payload.hex().upper()}")

    except Exception as e:
        print(f"[!] 에러 발생: {e}")
    finally:
        if bus:
            bus.shutdown()
        print("[*] 테스트 종료.")

if __name__ == "__main__":
    main()