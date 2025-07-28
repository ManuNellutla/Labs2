; Version 3.0 - Trade with Balance Check
; Keywords: S, K, W, Q, N, I, $G
TRD3(TID,SYM,QTY,PRC,ACC) ; Trade with balance validation
 N BAL,COST
 I TID=""!(SYM="")!(QTY<=0)!(PRC<=0)!(ACC="") Q 0
 S COST=QTY*PRC
 S BAL=$G(^ACC(ACC,"BAL"),0)
 I BAL<COST W "Error: Insufficient funds!",! Q 0
 S ^TRD(TID)=SYM_"^"_QTY_"^"_PRC_"^"_ACC
 S ^TRD(TID,"SYM")=SYM
 S ^TRD(TID,"QTY")=QTY
 S ^TRD(TID,"PRC")=PRC
 S ^TRD(TID,"ACC")=ACC
 S ^ACC(ACC,"BAL")=BAL-COST
 W "Trade executed: ",TID," Bal: ",^ACC(ACC,"BAL"),!
 Q 1
CNCL3(TID) ; Cancel trade and refund
 I '$D(^TRD(TID)) Q 0
 N ACC,QTY,PRC,COST
 S ACC=$G(^TRD(TID,"ACC"))
 S QTY=$G(^TRD(TID,"QTY"))
 S PRC=$G(^TRD(TID,"PRC"))
 S COST=QTY*PRC
 S ^ACC(ACC,"BAL")=$G(^ACC(ACC,"BAL"),0)+COST
 K ^TRD(TID)
 W "Trade ",TID," cancelled. Refund: ",COST,!
 Q 1
