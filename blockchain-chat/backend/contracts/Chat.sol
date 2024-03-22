// SPDX-License-Identifier: MIT 

pragma solidity ^0.8.19;

contract Chats {

    struct ChatMessage { # represents messages and their timestamps as one datatype together
    bytes message;
    uint256 timestamp;
    }

    mapping(uint256 => mapping(address => ChatMessage[])) private chats;

    function send(uint256 chat, address user, bytes calldata message) public {
        chats[chat][user].push(ChatMessage(message, block.timestamp));
    }
}



    mapping(uint256 => mapping(address => bytes[])) private chats;
    
    function send(uint256 chat, address user, bytes calldata message) public {
        chats[chat][user].push(message);
    }
`
