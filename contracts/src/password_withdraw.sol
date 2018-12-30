pragma solidity ^0.5.1;

contract password_withdraw {
  function withdraw (int value) public {
    if (value == 5) {
      msg.sender.call.value(50000)("");
    }
  }

  function() payable external { }
}