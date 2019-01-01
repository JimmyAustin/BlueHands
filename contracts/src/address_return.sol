pragma solidity ^0.5.1;

contract address_return {
 function canIdentifySender (address randomAddress) public returns (bool) {
   return randomAddress == msg.sender;
 }
}