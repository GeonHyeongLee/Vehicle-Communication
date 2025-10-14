#include "can.h"
#include "tof.h"
#include "ultrasonic.h"

#include "dtc.h" // dtc 정보 읽기용
#include "config.h" // ota용 플래그 쓰기용

/*********************************************************************************************************************/
/*-------------------------------------------------Global variables--------------------------------------------------*/
/*********************************************************************************************************************/
McmcanType g_mcmcan; /* Global MCMCAN configuration and control structure    */

/*********************************************************************************************************************/
/*---------------------------------------------Function Implementations----------------------------------------------*/
/*********************************************************************************************************************/

/* Callback 함수 포인터 */
static void (*tofCallback) (unsigned char *rxData) = 0;

void canRegisterTofCallback (void (*callback) (unsigned char*))
{
    tofCallback = callback;
}

/* Default CAN Tx Handler */
IFX_INTERRUPT(canTxIsrHandler, 0, ISR_PRIORITY_CAN_TX);
void canTxIsrHandler (void)
{
    /* Clear the "Transmission Completed" interrupt flag */
    IfxCan_Node_clearInterruptFlag(g_mcmcan.canSrcNode.node, IfxCan_Interrupt_transmissionCompleted);
}

/* ---- ISO-TP TX 상태 ---- */
typedef struct
{
    uint8 buf[256];
    uint16 len;
    uint16 off;      // 다음 보낼 인덱스
    uint8 sn;       // CF 시퀀스(1..15)
    uint8 bs;       // Block Size
    uint8 bs_cnt;   // 남은 블록 카운터
    uint8 stmin;    // 최소 간격(ms 또는 μs 표준 해석 필요)
    uint8 active;   // 전송 진행중 플래그
    uint8 waiting_fc; // FC 기다리는 중
} IsoTpTxCtx;

static IsoTpTxCtx g_isotp_tx;

/* ---- 헬퍼: CAN 보냄 ---- */
static inline void canSend8 (uint32 id, const uint8 *d)
{
    canSendMsg(id, (const char*) d, 8);
}

/* ---- 헬퍼: UDS 응답 페이로드를 ISO-TP로 송신 시작 ---- */
static void isotp_send_response (uint32 canId, const uint8 *payload, uint16 plen)
{
    uint8 tx[8] = {0};

    // 7바이트 이하 데이터는 SF 처리
    if (plen <= 7)
    {
        // Single Frame
        tx[0] = (uint8) (plen & 0x0F);     // PCI(SF) = 0x0 | len
        for (uint8 i = 0; i < plen; i++)
            tx[1 + i] = payload[i];
        // pad 나머지 0
        canSend8(canId, tx);
        g_isotp_tx.active = 0;
        return;
    }

    // 8바이트 이상 데이터가 오면
    // First Frame(FF) 생성해서 CAN 버스로 전송
    // 이때 g_isotp_tx 전역 변수 = 상태를 기록

    // First Frame
    tx[0] = 0x10 | ((plen >> 8) & 0x0F);      // 상위 nibble=1(FF), 하위=길이 상위 4bit
    tx[1] = (uint8) (plen & 0xFF);           // 길이 하위 8bit
    // FF 데이터 6바이트
    uint8 ff_data = (plen >= 6) ? 6 : (uint8) plen;
    for (uint8 i = 0; i < ff_data; i++)
        tx[2 + i] = payload[i];
    canSend8(canId, tx);

    // TX 컨텍스트 세팅 (FC 기다림)
    memset(&g_isotp_tx, 0, sizeof(g_isotp_tx));
    memcpy(g_isotp_tx.buf, payload, plen);
    g_isotp_tx.len = plen;
    g_isotp_tx.off = ff_data;  // 이미 FF로 보낸 만큼
    g_isotp_tx.sn = 1;        // CF SN 시작은 1
    g_isotp_tx.active = 1;
    g_isotp_tx.waiting_fc = 1;

    // bs/stmin은 FC 수신 후 채움
}

/* ---- 헬퍼: FC(CTS) 받은 뒤 CF를 한 블록 보내기 ---- */
static void isotp_send_next_block (uint32 canId)
{
    if (!g_isotp_tx.active || g_isotp_tx.waiting_fc)
        return;

    uint8 tx[8];

    // 블록 사이즈만큼 CF 전송(또는 데이터 끝날 때까지)
    uint8 to_send = (g_isotp_tx.bs == 0) ? 0xFF : g_isotp_tx.bs; // BS=0이면 제한 없음
    while ((g_isotp_tx.off < g_isotp_tx.len) && (to_send > 0))
    {
        uint16 remain = g_isotp_tx.len - g_isotp_tx.off;
        uint8 chunk = (remain >= 7) ? 7 : (uint8) remain;

        memset(tx, 0, sizeof(tx));
        tx[0] = 0x20 | (g_isotp_tx.sn & 0x0F); // CF PCI
        for (uint8 i = 0; i < chunk; i++)
            tx[1 + i] = g_isotp_tx.buf[g_isotp_tx.off + i];
        canSend8(canId, tx);

        g_isotp_tx.off += chunk;
        g_isotp_tx.sn = (g_isotp_tx.sn % 15) + 1; // 1..15 순환
        if (g_isotp_tx.bs != 0)
        {
            to_send--;
            g_isotp_tx.bs_cnt++;
            if (to_send == 0 && g_isotp_tx.off < g_isotp_tx.len)
            {
                // 다시 FC 필요
                g_isotp_tx.waiting_fc = 1;
                g_isotp_tx.bs_cnt = 0;
                break;
            }
        }

        // STmin 대기(간단히 무시하거나, 타이머로 구현 권장)
        // TODO: STmin 처리
    }

    if (g_isotp_tx.off >= g_isotp_tx.len)
    {
        // 완료
        g_isotp_tx.active = 0;
    }
}

/* ---- RX ISR ---- */
// ==========================================================================
// 필요한 모든 헤더 파일들을 포함해야 합니다.
// ex: #include "tof.h"
// ex: #include "ultrasonic.h"
// ==========================================================================
/* ---- 센서 값 획득 함수들 (외부 선언) ---- */
extern unsigned int tofGetValue (void);
extern int getDistanceByUltra (UltraDir dir);

/* ==========================================================================
 * UDS/ISO-TP 프로토콜 전문 처리 함수
 * ========================================================================== */
void udsHandler (unsigned char *rxData, int rxLen)
{
    // 이 함수는 rxID가 0x7E0인 메시지만을 처리합니다.
    uint8 pci = rxData[0];
    uint8 type = pci & 0xF0;

    switch (type)
    {
        case 0x00 :
        { // SF (Single Frame)
            uint8 sfLen = pci & 0x0F;
            if (sfLen == 0 || sfLen > 7)
                break;

            uint8 SID = rxData[1];

            if (SID == 0x22 && sfLen >= 3)
            { // 03 22 10 00  =>
                uint16 DID = ((uint16) rxData[2] << 8) | rxData[3];

                switch (DID)
                {
                    case 0x1000 :
                    { // 레이저 센서 거리 요청
                      // 1. tofGetValue()가 mm 단위를 반환한다고 약속합니다.
                        uint16 distance_mm = (uint16) tofGetValue();

                        // 2. 이 mm 값을 UDS 페이로드에 담아 전송합니다.
                        uint8 payload[5] = {0x62, 0x10, 0x00,           // UDS 긍정 응답 헤더
                                (uint8) (distance_mm >> 8),    // 거리 값(mm) 상위 바이트
                                (uint8) (distance_mm & 0xFF)   // 거리 값(mm) 하위 바이트
                                };
                        isotp_send_response(0x7E8, payload, sizeof(payload));
                        break;
                    }
                    case 0x1001 :
                    { // 초음파 (좌) 센서 거리 요청
                        // 1. 좌측 초음파 센서의 거리를 cm 단위로 반환하는 함수 호출한다
                        float distance_cm = ultrasonic_getDistanceCm(ULT_LEFT);


                        // 2. 만약 센서 측정에 실패했다면, 부정 응답(NRC)를 보낸다.
                        if (distance_cm < 0) {
                            uint8 nr_payload[3] = {0x7F, 0x22, 0x31}; // 0x31는 requestOutOfRange
                            isotp_send_response(0x7E8, nr_payload, sizeof(nr_payload));
                            break;
                        }

                        // 3. float 값을 정수로 변환(소수점 첫째 자리까지 표현하기 위해 10 곱함)
                        // ex) 15.7cm => 157
                        uint16 scaled_distance = (uint16)(distance_cm * 10.0f);

                        // 4. 변환된 2바이트 정수 값을 페이로드에 담아 전송
                        uint8 payload[5] = {0x62, 0x10, 0x01,
                                (uint8)(scaled_distance >> 8),
                                (uint8)(scaled_distance & 0xFF)
                        };

                        isotp_send_response(0x7E8, payload, sizeof(payload));

                        break;
                    }


                    case 0x0001 :
                    { // 확인용 테스트
                        uint8 payload[20] = {0};
                        uint16 plen = 0;
                        payload[plen++] = 0x62;
                        payload[plen++] = 0x00;
                        payload[plen++] = 0x01;
                        const uint8 data_ex[] = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0x11, 0x22, 0x33, 0x44};
                        memcpy(&payload[plen], data_ex, sizeof(data_ex));
                        plen += sizeof(data_ex);
                        isotp_send_response(0x7E8, payload, plen);
                        break;
                    }
                    default :
                    { // 메뉴판에 없는 DID
                        uint8 nr_payload[3] = {0x7F, 0x22, 0x31};
                        isotp_send_response(0x7E8, nr_payload, sizeof(nr_payload));
                        break;
                    }

                }
            }

            else if (SID == 0x19 && sfLen >= 2)
            {
                uint8 sub_function = rxData[2];
                if (sub_function == 0x02)
                {
                    uint8 payload[50];
                    uint16 plen = 0;
                    payload[plen++] = 0x59;
                    payload[plen++] = rxData[2];
                    payload[plen++] = rxData[3];

                    for (int i = 0; i < MAX_DTCS; i++)
                    {
                        if (g_dtcStorage[i].status & DTC_STATUS_TEST_FAILED)
                        {
                            payload[plen++] = (uint8) (g_dtcStorage[i].dtc_code >> 16);
                            payload[plen++] = (uint8) (g_dtcStorage[i].dtc_code >> 8);
                            payload[plen++] = (uint8) (g_dtcStorage[i].dtc_code & 0xFF);
                            payload[plen++] = g_dtcStorage[i].status;
                        }
                    }
                    isotp_send_response(0x7E8, payload, plen);
                }
            }

            // SID 0x2E (데이터 쓰기) 처리 로직 추가
            else if (SID == 0x2E && sfLen >= 4) // SID(1) + DID(2) + Data(1 이상)
            {
                uint16 DID = ((uint16) rxData[2] << 8) | rxData[3];
                // AEB 기능 플래그 DID(0x2000)가 맞는지 확인
                if (DID == 0x2000)
                {
                    uint8 new_status = rxData[4]; // 0x01 = ON, 0x00 = OFF

                    // config 모듈의 g_config 변수 값을 직접 변경
                    // ==는 '같은지 비교하라'는 비교 연산자
                    // 만약 0x01이 들어왔으면 0x01 == 0x01이므로 true여서 isAebEnabled = 1
                    // 만약 0x00이 들어왔으면 0x00 == 0x01이므로 flase이기에 isAebEnabled = 0
                    g_config.isAebEnabled = (new_status == 0x01);


                    // 진짜 바뀌는지 안 바뀌는지 확인해보기 위한 코드
                    if (g_config.isAebEnabled) {
                        myPrintf("AEB Master Switch ON\n");
                    }
                    else {
                        myPrintf("AEB Master Switch OFF\n");
                    }
                    // (참고: 실제 제품에서는 이 시점에 변경 사항을 DFlash에 저장하라는 'Dirty' 플래그를 설정합니다)

                    // "쓰기 완료" 긍정 응답 전송
                    uint8 positive_response[] = {0x6E, 0x20, 0x00}; // 0x6E = 0x2E + 0x40
                    isotp_send_response(0x7E8, positive_response, sizeof(positive_response));
                }
                else
                {
                    // 지원하지 않는 DID에 대한 부정 응답
                    uint8 nr_payload[3] = {0x7F, 0x2E, 0x31}; // 0x31 = requestOutOfRange
                    isotp_send_response(0x7E8, nr_payload, sizeof(nr_payload));
                }
            }

            break;
        }

        case 0x10 :
        { // FF (First Frame) - 긴 요청 수신
          // (현재는 간단히 FC만 보내는 로직)
            uint8 fc[8] = {0x30, 0x00, 0x00};
            canSend8(0x7E8, fc); // FF에 대한 FC 응답
            break;
        }
        case 0x30 :
        { // FC (Flow Control) - ECU가 보낸 FF에 대한 테스터의 응답 수신
            uint8 fs = pci & 0x0F;
            if (g_isotp_tx.active && fs == 0x00)
            {
                g_isotp_tx.bs = rxData[1];
                g_isotp_tx.stmin = rxData[2];
                g_isotp_tx.waiting_fc = 0;
                isotp_send_next_block(0x7E8);
            }
            else
            {
                g_isotp_tx.active = 0;
            }
            break;
        }
            // (CF 수신 로직 등은 필요시 추가)
    }

    // FC를 받은 후 남은 CF가 있다면 모두 전송
    if (g_isotp_tx.active && !g_isotp_tx.waiting_fc)
    {
        isotp_send_next_block(0x7E8);
    }
}

/* ==========================================================================
 * 최종 RX ISR: 모든 CAN 메시지를 수신하여 분배하는 교통정리 담당관
 * ========================================================================== */
IFX_INTERRUPT(canRxIsrHandler, 0, ISR_PRIORITY_CAN_RX);
void canRxIsrHandler (void)
{
    unsigned int rxID;
    unsigned char rxData[8] = {0, };
    int rxLen;

    canRecvMsg(&rxID, rxData, &rxLen);

    // --- ID를 보고 교통정리 시작 ---
    if (rxID == 0x7E0) // UDS 진단 요청 ID인가?
    {
        // UDS 전문 담당자를 호출합니다.
        udsHandler(rxData, rxLen);
    }
    else if (rxID == 0x200) // ToF 센서 데이터 ID인가?
    {
        // ToF 전문 담당자(tof.c의 함수)를 호출합니다.
        tofUpdateFromCAN(rxData);
    }
    // else if (rxID == 0xXXX) { ... }
    // 나중에 다른 CAN ID를 사용하는 기능이 추가되면 여기에 분기문만 추가하면 됩니다.
}
/* Function to initialize MCMCAN module and nodes related for this application use case */
void canInit (CAN_BAUDRATES ls_baudrate, CAN_NODE CAN_Node)
{
    /* wake up transceiver (node 0) */
    IfxPort_setPinModeOutput(&MODULE_P20, 6, IfxPort_OutputMode_pushPull, IfxPort_OutputIdx_general);
    MODULE_P20.OUT.B.P6 = 0;

    IfxCan_Can_initModuleConfig(&g_mcmcan.canConfig, &MODULE_CAN0);
    IfxCan_Can_initModule(&g_mcmcan.canModule, &g_mcmcan.canConfig);
    IfxCan_Can_initNodeConfig(&g_mcmcan.canNodeConfig, &g_mcmcan.canModule);

    switch (ls_baudrate)
    {
        case BD_NOUSE :
            g_mcmcan.canNodeConfig.busLoopbackEnabled = TRUE;
            break;
        case BD_500K :
            g_mcmcan.canNodeConfig.baudRate.baudrate = 500000;
            break;
        case BD_1M :
            g_mcmcan.canNodeConfig.baudRate.baudrate = 1000000;
            break;
    }

    g_mcmcan.canNodeConfig.busLoopbackEnabled = FALSE;

    if (CAN_Node == CAN_NODE0)
    { /* CAN Node 0 for lite kit */
        g_mcmcan.canNodeConfig.nodeId = IfxCan_NodeId_0;
        const IfxCan_Can_Pins pins = {&IfxCan_TXD00_P20_8_OUT, IfxPort_OutputMode_pushPull, /* TX Pin for lite kit (can node 0) */
        &IfxCan_RXD00B_P20_7_IN, IfxPort_InputMode_pullUp, /* RX Pin for lite kit (can node 0) */
        IfxPort_PadDriver_cmosAutomotiveSpeed1};
        g_mcmcan.canNodeConfig.pins = &pins;
    }
    else if (CAN_Node == CAN_NODE2)
    { /* CAN Node 2 for mikrobus */
        g_mcmcan.canNodeConfig.nodeId = IfxCan_NodeId_2;
        const IfxCan_Can_Pins pins = {&IfxCan_TXD02_P15_0_OUT, IfxPort_OutputMode_pushPull, /* TX Pin for mikrobus (can node 2) */
        &IfxCan_RXD02A_P15_1_IN, IfxPort_InputMode_pullUp, /* RX Pin for mikrobus (can node 2) */
        IfxPort_PadDriver_cmosAutomotiveSpeed1};
        g_mcmcan.canNodeConfig.pins = &pins;
    }

    g_mcmcan.canNodeConfig.frame.type = IfxCan_FrameType_transmitAndReceive;
    g_mcmcan.canNodeConfig.interruptConfig.transmissionCompletedEnabled = TRUE;
    g_mcmcan.canNodeConfig.interruptConfig.traco.priority = ISR_PRIORITY_CAN_TX;
    g_mcmcan.canNodeConfig.interruptConfig.traco.interruptLine = IfxCan_InterruptLine_0;
    g_mcmcan.canNodeConfig.interruptConfig.traco.typeOfService = IfxSrc_Tos_cpu0;
    IfxCan_Can_initNode(&g_mcmcan.canSrcNode, &g_mcmcan.canNodeConfig);

    /* Reception handling configuration */
    g_mcmcan.canNodeConfig.rxConfig.rxMode = IfxCan_RxMode_sharedFifo0;
    g_mcmcan.canNodeConfig.rxConfig.rxBufferDataFieldSize = IfxCan_DataFieldSize_8;
    g_mcmcan.canNodeConfig.rxConfig.rxFifo0DataFieldSize = IfxCan_DataFieldSize_8;
    g_mcmcan.canNodeConfig.rxConfig.rxFifo0Size = 15;
    /* General filter configuration */
    g_mcmcan.canNodeConfig.filterConfig.messageIdLength = IfxCan_MessageIdLength_standard;
    g_mcmcan.canNodeConfig.filterConfig.standardListSize = 8;
    g_mcmcan.canNodeConfig.filterConfig.standardFilterForNonMatchingFrames = IfxCan_NonMatchingFrame_reject;
    g_mcmcan.canNodeConfig.filterConfig.rejectRemoteFramesWithStandardId = TRUE;
    /* Interrupt configuration */
    g_mcmcan.canNodeConfig.interruptConfig.rxFifo0NewMessageEnabled = TRUE;
    g_mcmcan.canNodeConfig.interruptConfig.rxf0n.priority = ISR_PRIORITY_CAN_RX;
    g_mcmcan.canNodeConfig.interruptConfig.rxf0n.interruptLine = IfxCan_InterruptLine_1;
    g_mcmcan.canNodeConfig.interruptConfig.rxf0n.typeOfService = IfxSrc_Tos_cpu0;
    IfxCan_Can_initNode(&g_mcmcan.canDstNode, &g_mcmcan.canNodeConfig);

    /* Rx filter configuration (default: all messages accepted) */
    canSetFilterRange(0x0, 0x7FF);
}

void canSetFilterRange (uint32 start, uint32 end)
{
    g_mcmcan.canFilter.number = 0;
    g_mcmcan.canFilter.type = IfxCan_FilterType_range;
    g_mcmcan.canFilter.elementConfiguration = IfxCan_FilterElementConfiguration_storeInRxFifo0;
    g_mcmcan.canFilter.id1 = start;
    g_mcmcan.canFilter.id2 = end;
    IfxCan_Can_setStandardFilter(&g_mcmcan.canDstNode, &g_mcmcan.canFilter);
}

void canSetFilterMask (uint32 id, uint32 mask)
{
    g_mcmcan.canFilter.number = 0;
    g_mcmcan.canFilter.type = IfxCan_FilterType_classic;
    g_mcmcan.canFilter.elementConfiguration = IfxCan_FilterElementConfiguration_storeInRxFifo0;
    g_mcmcan.canFilter.id1 = id;
    g_mcmcan.canFilter.id2 = mask;
    IfxCan_Can_setStandardFilter(&g_mcmcan.canDstNode, &g_mcmcan.canFilter);
}

void canSendMsg (unsigned int id, const char *txData, int len)
{
    /* Initialization of the TX message with the default configuration */
    IfxCan_Can_initMessage(&g_mcmcan.txMsg);

    g_mcmcan.txMsg.messageId = id;
    g_mcmcan.txMsg.dataLengthCode = len;

    /* Define the content of the data to be transmitted */
    for (int i = 0; i < 8; i++)
    {
        g_mcmcan.txData[i] = txData[i];
    }

    /* Send the CAN message with the previously defined TX message content */
    while (IfxCan_Status_notSentBusy
            == IfxCan_Can_sendMessage(&g_mcmcan.canSrcNode, &g_mcmcan.txMsg, (uint32*) &g_mcmcan.txData[0]))
    {
    }
}

int canRecvMsg (unsigned int *id, unsigned char *rxData, int *len)
{
    int err = 0;
    /* Clear the "RX FIFO 0 new message" interrupt flag */
    IfxCan_Node_clearInterruptFlag(g_mcmcan.canDstNode.node, IfxCan_Interrupt_rxFifo0NewMessage);

    /* Received message content should be updated with the data stored in the RX FIFO 0 */
    g_mcmcan.rxMsg.readFromRxFifo0 = TRUE;
    g_mcmcan.rxMsg.readFromRxFifo1 = FALSE;

    /* Read the received CAN message */
    IfxCan_Can_readMessage(&g_mcmcan.canDstNode, &g_mcmcan.rxMsg, (uint32*) &g_mcmcan.rxData);

    *id = g_mcmcan.rxMsg.messageId;
    for (int i = 0; i < 8; i++)
    {
        rxData[i] = g_mcmcan.rxData[i];
    }
    *len = g_mcmcan.rxMsg.dataLengthCode;

    return err;
}
