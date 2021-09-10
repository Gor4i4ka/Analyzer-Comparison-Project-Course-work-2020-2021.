int foo () {
    char a = 0; // hypothetical juliet
    char b = 0; // hypothetical svace
    ;
    a = a + 1000; // FLAW 1
    ;
    ; // svace main for test
    ;
    b = b - 600; // FLAW 2
    return 0;
}