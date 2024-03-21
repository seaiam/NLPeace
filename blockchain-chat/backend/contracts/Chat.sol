// SPDX-License-Identifier: MIT 

pragma solidity ^0.8.19;

contract Chats {

    mapping(uint256 => mapping(address => bytes[])) private chats;
    
    function send(uint256 chat, address user, bytes calldata message) public {
        chats[chat][user].push(message);
    }
}
