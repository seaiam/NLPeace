// SPDX-License-Identifier: MIT 

pragma solidity ^0.8.19;

contract Chats {

    struct ChatMessage { // represents messages and their timestamps as one datatype together
        address sender;
        string message;
        uint256 timestamp;
    }

    mapping(uint256 => ChatMessage[]) private messages;
    mapping(uint256 => uint256) private counts;
    uint256 private count = 0;

    function create() public {
        messages[count].push(ChatMessage(msg.sender, "Hello World", block.timestamp));
        counts[count] = 1;
        count++;
    }

    function put(uint256 id, string calldata message) public {
        messages[id].push(ChatMessage(msg.sender, message, block.timestamp));
        counts[id]++;
    }

    function getMsg(uint256 id, uint256 index) public view returns (string memory) {
        return messages[id][index].message;
    }

    function getSender(uint256 id, uint256 index) public view returns (address){
        return messages[id][index].sender;
    }

    function getTime(uint256 id, uint256 index) public view returns (uint256){
        return messages[id][index].timestamp;
    }

    function countChat(uint256 id) public view returns (uint256){
        return counts[id];
    }

}
