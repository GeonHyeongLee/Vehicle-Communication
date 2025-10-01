#include "can.h"

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
typedef struct {
    uint8  buf[256];
    uint16 len;
    uint16 off;      // 다음 보낼 인덱스
    uint8  sn;       // CF 시퀀스(1..15)
    uint8  bs;       // Block Size
    uint8  bs_cnt;   // 남은 블록 카운터
    uint8  stmin;    // 최소 간격(ms 또는 μs 표준 해석 필요)
    uint8  active;   // 전송 진행중 플래그
    uint8  waiting_fc; // FC 기다리는 중
} IsoTpTxCtx;

static IsoTpTxCtx g_isotp_tx;

/* ---- 헬퍼: CAN 보냄 ---- */
static inline void canSend8(uint32 id, const uint8 *d) {
    canSendMsg(id, (const char*)d, 8);
}

/* ---- 헬퍼: UDS 응답 페이로드를 ISO-TP로 송신 시작 ---- */
static void isotp_send_response(uint32 canId, const uint8 *payload, uint16 plen)
{
    uint8 tx[8] = {0};

    if (plen <= 7) {
        // Single Frame
        tx[0] = (uint8)(plen & 0x0F);     // PCI(SF) = 0x0 | len
        for (uint8 i = 0; i < plen; i++) tx[1+i] = payload[i];
        // pad 나머지 0
        canSend8(canId, tx);
        g_isotp_tx.active = 0;
        return;
    }

    // First Frame
    tx[0] = 0x10 | ((plen >> 8) & 0x0F);      // 상위 nibble=1(FF), 하위=길이 상위 4bit
    tx[1] = (uint8)(plen & 0xFF);           // 길이 하위 8bit
    // FF 데이터 6바이트
    uint8 ff_data = (plen >= 6) ? 6 : (uint8)plen;
    for (uint8 i = 0; i < ff_data; i++) tx[2+i] = payload[i];
    canSend8(canId, tx);

    // TX 컨텍스트 세팅 (FC 기다림)
    memset(&g_isotp_tx, 0, sizeof(g_isotp_tx));
    memcpy(g_isotp_tx.buf, payload, plen);
    g_isotp_tx.len = plen;
    g_isotp_tx.off = ff_data;  // 이미 FF로 보낸 만큼
    g_isotp_tx.sn  = 1;        // CF SN 시작은 1
    g_isotp_tx.active = 1;
    g_isotp_tx.waiting_fc = 1;
    // bs/stmin은 FC 수신 후 채움
}

/* ---- 헬퍼: FC(CTS) 받은 뒤 CF를 한 블록 보내기 ---- */
static void isotp_send_next_block(uint32 canId)
{
    if (!g_isotp_tx.active || g_isotp_tx.waiting_fc) return;

    uint8 tx[8];

    // 블록 사이즈만큼 CF 전송(또는 데이터 끝날 때까지)
    uint8 to_send = (g_isotp_tx.bs == 0) ? 0xFF : g_isotp_tx.bs; // BS=0이면 제한 없음
    while ( (g_isotp_tx.off < g_isotp_tx.len) && (to_send > 0) ) {
        uint16 remain = g_isotp_tx.len - g_isotp_tx.off;
        uint8 chunk = (remain >= 7) ? 7 : (uint8)remain;

        memset(tx, 0, sizeof(tx));
        tx[0] = 0x20 | (g_isotp_tx.sn & 0x0F); // CF PCI
        for (uint8 i = 0; i < chunk; i++) tx[1+i] = g_isotp_tx.buf[g_isotp_tx.off + i];
        canSend8(canId, tx);

        g_isotp_tx.off += chunk;
        g_isotp_tx.sn = (g_isotp_tx.sn % 15) + 1; // 1..15 순환
        if (g_isotp_tx.bs != 0) {
            to_send--;
            g_isotp_tx.bs_cnt++;
            if (to_send == 0 && g_isotp_tx.off < g_isotp_tx.len) {
                // 다시 FC 필요
                g_isotp_tx.waiting_fc = 1;
                g_isotp_tx.bs_cnt = 0;
                break;
            }
        }

        // STmin 대기(간단히 무시하거나, 타이머로 구현 권장)
        // TODO: STmin 처리
    }

    if (g_isotp_tx.off >= g_isotp_tx.len) {
        // 완료
        g_isotp_tx.active = 0;
    }
}

/* ---- RX ISR ---- */
IFX_INTERRUPT(canRxIsrHandler, 0, ISR_PRIORITY_CAN_RX);
void canRxIsrHandler (void)
{
    unsigned int rxID;
    unsigned char rxData[8] = {0,};
    int rxLen;

    canRecvMsg(&rxID, rxData, &rxLen);

    // 진단 요청은 0x7E0로 온다고 가정
    if (rxID != 0x7E0) {
        // 혹시 테스터의 FC(CTS)가 0x7E0로 올 수도 있으니 아래에서 별도 처리
    }

    uint8 pci = rxData[0];
    uint8 type = pci & 0xF0;

    switch (type) {
    case 0x00: { // SF
        uint8 sfLen = pci & 0x0F;
        if (sfLen == 0 || sfLen > 7) break; // 방어

        // UDS 페이로드 시작은 rxData[1]
        uint8 SID = rxData[1];
        if (SID == 0x22 && sfLen >= 3) {
            uint16 DID = ((uint16)rxData[2] << 8) | rxData[3];

            if (DID == 0x0001) {
                // 예시: 응답 페이로드 생성 (의도적으로 12바이트로 길게 만들어 FF/CF 확인 가능)
                uint8 payload[20] = {0};
                uint16 plen = 0;
                payload[plen++] = 0x62;  // PR SID
                payload[plen++] = 0x00;  // DID
                payload[plen++] = 0x01;
                // 데이터 예시(9바이트 추가 → 총 12바이트)
                const uint8 data_ex[] = {0xAA,0xBB,0xCC,0xDD,0xEE,0x11,0x22,0x33,0x44};
                memcpy(&payload[plen], data_ex, sizeof(data_ex));
                plen += sizeof(data_ex);

                // ISO-TP로 응답 시작 (0x7E8로 송신)
                isotp_send_response(0x7E8, payload, plen);
            } else {
                // 부정응답 (SF로 충분)
                uint8 nrpl[3] = {0x7F, 0x22, 0x11};
                isotp_send_response(0x7E8, nrpl, 3);
            }
        }
        break;
    }

    case 0x10: { // FF (요청이 다-프레임)
        // 전체 길이 12bit
        uint16 totalLen = ((uint16)(pci & 0x0F) << 8) | rxData[1];
        // 필요하면 여기서 요청 재조립 컨텍스트 만들어 CF들을 받아 합치세요
        // (대부분 UDS 요청은 짧아서 생략 가능이지만, 구조만 남깁니다)

        // ECU(서버) 입장에선 요청이 FF로 왔으면, CF들을 더 받아야 “요청”이 완성됨.
        // 우선 FC(CTS) 보내서 상대가 CF들을 보내도록 할 수도 있지만,
        // 표준 상 FF를 보낸 쪽은 ‘송신자’, 지금은 우리가 수신자이므로
        // **우리가 FC(CTS)를 보내야** 상대가 CF를 계속 보냅니다.
        uint8 fc[8] = {0};
        fc[0] = 0x30;  // FC(CTS)
        fc[1] = 0x00;  // BS=0 (제한없음)
        fc[2] = 0x00;  // STmin=0
        canSend8(0x7E8, fc); // 수신자->송신자(테스터)로 FC 송신 (ID는 네트워크 설계에 맞게 조정)

        // 이후 들어올 CF들을 모아서 한 덩어리로 만든 뒤 UDS 파싱 -> 응답 생성
        break;
    }

    case 0x20: { // CF
        // 보통은 위 FF에서 시작한 수신 재조립 컨텍스트에 이어붙임
        // 요청 재조립이 끝났다면 그때 UDS 처리 -> 응답 만들고, 응답이 7바이트 넘어가면 FF/CF 송신

        // (여기서는 간단히 생략)
        break;
    }

    case 0x30: { // FC (테스터가 우리 FF 응답을 받은 뒤 보내는 FlowControl)
        // 우리가 방금 FF로 ‘응답’을 보냈다면 여기로 FC가 옴.
        uint8 fs = pci & 0x0F; // 0=CTS, 1=WT, 2=OVFLW
        if (g_isotp_tx.active) {
            if (fs == 0x00) { // CTS
                g_isotp_tx.bs    = rxData[1];
                g_isotp_tx.stmin = rxData[2];
                g_isotp_tx.waiting_fc = 0;
                // FC 받았으니 CF 전송 시작
                isotp_send_next_block(0x7E8);
            } else if (fs == 0x01) {
                // WT 처리(대기) - 타이머로 재시도 로직 권장
            } else {
                // OVFLW 등 에러 처리
                g_isotp_tx.active = 0;
            }
        }
        break;
    }

    default:
        // 기타 무시
        break;
    }

    // 만약 BS=0(제한없음)으로 CF 여러개를 한 번에 보낼 수 있으면,
    // FC 처리 후 여기서 한 번 더 호출해 남은 데이터 모두 보낼 수도 있음.
    if (g_isotp_tx.active && !g_isotp_tx.waiting_fc) {
        isotp_send_next_block(0x7E8);
    }
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
