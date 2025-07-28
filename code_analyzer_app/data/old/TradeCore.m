; Version 1.0 - Core Trade Management with External Subroutine Calls
; Keywords: S, W, Q, N, I, D
N
EXECUTE(TID,SYM,QTY,PRC,ACC) ; Execute trade with external calls
 N STATUS
 I TID=""!(SYM="")!(QTY<=0)!(PRC<=0)!(ACC="") W "Error: Invalid trade data!",! Q 0
 D CREATE^TradeCreate(TID,SYM,QTY,PRC,ACC,.STATUS) ; Call trade creation
 I 'STATUS Q 0
 D AUDIT^TradeAudit(TID,"EXEC",QTY*PRC) ; Log trade execution
 W "Trade ",TID," executed successfully!",!
 Q 1
CANCEL(TID) ; Cancel trade with external calls
 N STATUS,COST
 I '$D(^TRD(TID)) W "Error: Trade ",TID," not found!",! Q 0
 D CANCEL^TradeCancel(TID,.STATUS,.COST) ; Call trade cancellation
 I 'STATUS Q 0
 D AUDIT^TradeAudit(TID,"CNCL",COST) ; Log cancellation
 W "Trade ",TID," cancelled successfully!",!
 Q 1
