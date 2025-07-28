; Version 1.0 - Trade Cancellation Subroutines
; Keywords: S, K, W, Q, N, I, $G
N
CANCEL(TID,STATUS,COST) ; Cancel trade and update balance
 I '$D(^TRD(TID)) W "Error: Trade not found!",! S STATUS=0 Q
 N ACC,QTY,PRC
 S ACC=$G(^TRD(TID,"ACC"))
 S QTY=$G(^TRD(TID,"QTY"))
 S PRC=$G(^TRD(TID,"PRC"))
 S COST=QTY*PRC
 S ^ACC(ACC,"BAL")=$G(^ACC(ACC,"BAL"),0)+COST
 K ^TRD(TID)
 S STATUS=1
 Q
