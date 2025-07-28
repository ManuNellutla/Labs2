; Version 1.0 - Trade Creation Subroutines
; Keywords: S, W, Q, N, I
N
CREATE(TID,SYM,QTY,PRC,ACC,STATUS) ; Create trade record
 I '$D(^ACC(ACC)) W "Error: Account ",ACC," not found!",! S STATUS=0 Q
 S ^TRD(TID)=SYM_"^"_QTY_"^"_PRC_"^"_ACC
 S ^TRD(TID,"SYM")=SYM
 S ^TRD(TID,"QTY")=QTY
 S ^TRD(TID,"PRC")=PRC
 S ^TRD(TID,"ACC")=ACC
 S STATUS=1
 Q
