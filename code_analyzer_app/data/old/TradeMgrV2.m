; Version 2.0 - Trade Record with Validation
; Keywords: SET, KILL, WRITE, QUIT, NEW, IF, ELSE, $D
NEW
TRADE2(TRADEID,SYMBOL,QUANTITY,PRICE,ACCOUNT) ; Enhanced trade record creation
 IF TRADEID="" WRITE "Error: Trade ID required!",! QUIT 0
 IF SYMBOL=""!(QUANTITY<=0)!(PRICE<=0) WRITE "Error: Invalid trade details!",! QUIT 0
 SET ^TRADE(TRADEID)="SYMBOL^QUANTITY^PRICE^ACCOUNT"
 SET ^TRADE(TRADEID,"SYMBOL")=SYMBOL
 SET ^TRADE(TRADEID,"QUANTITY")=QUANTITY
 SET ^TRADE(TRADEID,"PRICE")=PRICE
 SET ^TRADE(TRADEID,"ACCOUNT")=ACCOUNT
 WRITE "Trade record created for ID: ",TRADEID,!
 QUIT 1
CANCEL2(TRADEID) ; Cancel with confirmation
 IF '$D(^TRADE(TRADEID)) DO  QUIT 0
 . WRITE "Error: No trade found for ID: ",TRADEID,!
 KILL ^TRADE(TRADEID)
 WRITE "Trade cancelled for ID: ",TRADEID,!
 QUIT 1
