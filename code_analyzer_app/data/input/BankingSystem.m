BANK ; Real-World Banking System in MUMPS
 ; Initialize system and check authentication
START ;
 N USER,PASS,LOGGEDIN
 S LOGGEDIN=0
 W !,"=== Banking System Login ==="
 W !,"Username: "
 R USER
 W !,"Password: "
 R PASS
 I $$AUTH(USER,PASS) S LOGGEDIN=1 D MENU
 I 'LOGGEDIN W !,"Invalid credentials" Q
 Q

AUTH(USER,PASS) ; Authenticate user
 ; In real-world, use hashed passwords and a user database
 I USER="admin",PASS="bank123" Q 1
 Q 0

MENU ; Main menu for banking operations
 N CHOICE,ACCNUM,NAME,ADDRESS,BAL
 F  D  Q:CHOICE=5
 . W !,"=== Banking System ==="
 . W !,"1. Create Account"
 . W !,"2. Get Account Info"
 . W !,"3. Set Balance"
 . W !,"4. View Transaction History"
 . W !,"5. Exit"
 . W !,"Select Option (1-5): "
 . R CHOICE
 . I CHOICE=1 D  ; Collect inputs for CREATE
 . . W !,"Enter Account Number (6-10 digits): "
 . . R ACCNUM
 . . W !,"Enter Customer Name (3-50 chars): "
 . . R NAME
 . . W !,"Enter Address (3-100 chars): "
 . . R ADDRESS
 . . W !,"Enter Initial Balance (0 or positive): "
 . . R BAL
 . . D CREATE(ACCNUM,NAME,ADDRESS,BAL)
 . I CHOICE=2 D  ; Collect input for GETBAL
 . . W !,"Enter Account Number (6-10 digits): "
 . . R ACCNUM
 . . D GETBAL(ACCNUM)
 . I CHOICE=3 D  ; Collect inputs for SETBAL
 . . W !,"Enter Account Number (6-10 digits): "
 . . R ACCNUM
 . . W !,"Enter New Balance (0 or positive): "
 . . R BAL
 . . D SETBAL(ACCNUM,BAL)
 . I CHOICE=4 D TRANSHIST
 . I CHOICE=5 D EXIT
 Q

CREATE(ACCNUM,NAME,ADDRESS,BAL) ; Create a new account with transaction logging
 N DATA,TIMESTAMP
 I ACCNUM'?6.10N W !,"Invalid Account Number (must be 6-10 digits)" Q
 I NAME'?3.50AN W !,"Invalid Name (3-50 alphanumeric chars)" Q
 I ADDRESS'?3.100AN W !,"Invalid Address (3-100 alphanumeric chars)" Q
 I BAL'?.N,1".".2N!(BAL<0) W !,"Invalid Balance (must be non-negative)" Q
 L +^BANK(ACCNUM):5 E  W !,"Account locked, try again later" Q
 I $D(^BANK(ACCNUM)) W !,"Account already exists" L -^BANK(ACCNUM) Q
 S TIMESTAMP=$ZTIMESTAMP
 S ^BANK(ACCNUM)="NAME="_NAME_"^ADDRESS="_ADDRESS_"^BAL="_BAL
 S ^BANKTRANS(ACCNUM,$I(^BANKTRANS(ACCNUM)))=TIMESTAMP_"^CREATE^"_BAL_"^"_NAME_"^"_ADDRESS
 W !,"Account created successfully"
 L -^BANK(ACCNUM)
 Q

GETBAL(ACCNUM) ; Retrieve account information
 N DATA
 I ACCNUM'?6.10N W !,"Invalid Account Number" Q
 L +^BANK(ACCNUM):5 E  W !,"Account locked, try again later" Q
 I '$D(^BANK(ACCNUM)) W !,"Account not found" L -^BANK(ACCNUM) Q
 S DATA=^BANK(ACCNUM)
 W !,"Account Number: ",ACCNUM
 W !,"Customer Name: ",$P(DATA,"^",1)
 W !,"Address: ",$P(DATA,"^",2)
 W !,"Balance: ",$P(DATA,"^",3)
 L -^BANK(ACCNUM)
 Q

SETBAL(ACCNUM,BAL) ; Update account balance with transaction logging
 N DATA,NAME,ADDRESS,TIMESTAMP
 I ACCNUM'?6.10N W !,"Invalid Account Number" Q
 I BAL'?.N,1".".2N!(BAL<0) W !,"Invalid Balance (must be non-negative)" Q
 L +^BANK(ACCNUM):5 E  W !,"Account locked, try again later" Q
 I '$D(^BANK(ACCNUM)) W !,"Account not found" L -^BANK(ACCNUM) Q
 S DATA=^BANK(ACCNUM)
 S NAME=$P(DATA,"^",1)
 S ADDRESS=$P(DATA,"^",2)
 S TIMESTAMP=$ZTIMESTAMP
 S ^BANK(ACCNUM)="NAME="_NAME_"^ADDRESS="_ADDRESS_"^BAL="_BAL
 S ^BANKTRANS(ACCNUM,$I(^BANKTRANS(ACCNUM)))=TIMESTAMP_"^UPDATE^"_BAL_"^"_NAME_"^"_ADDRESS
 W !,"Balance updated successfully"
 L -^BANK(ACCNUM)
 Q

TRANSHIST ; View transaction history
 N ACCNUM,TRANS,INDEX
 W !,"Enter Account Number (6-10 digits): "
 R ACCNUM
 I ACCNUM'?6.10N W !,"Invalid Account Number" Q
 L +^BANK(ACCNUM):5 E  W !,"Account locked, try again later" Q
 I '$D(^BANK(ACCNUM)) W !,"Account not found" L -^BANK(ACCNUM) Q
 W !,"Transaction History for Account: ",ACCNUM
 S INDEX=0
 F  S INDEX=$O(^BANKTRANS(ACCNUM,INDEX)) Q:INDEX=""  D
 . S TRANS=^BANKTRANS(ACCNUM,INDEX)
 . W !,"Time: ",$P(TRANS,"^",1)," | Type: ",$P(TRANS,"^",2)," | Balance: ",$P(TRANS,"^",3)," | Name: ",$P(TRANS,"^",4)," | Address: ",$P(TRANS,"^",5)
 L -^BANK(ACCNUM)
 Q

EXIT ; Exit the program
 W !,"Exiting Banking System"
 Q