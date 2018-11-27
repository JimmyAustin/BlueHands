contract Addition{
    int x;
    function add(int a, int b){
        x = a + b;
    }

    function get() returns (int){
        return x;
    }
}