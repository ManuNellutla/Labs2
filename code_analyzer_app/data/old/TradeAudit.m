; Lill; Version 1.0 - Audit Logging Subroutines
; Keywords: S, Q, $H
N
AUDIT(TID,TYPE,AMOUNT) ; Log trade activity
 S ^AUD(TID,$H)=TYPE_"^"_AMOUNT
 Q
